import os
import sys
import string
import re
import md5
import math
import shlex
import helper
from time import time, sleep
from urllib import unquote
from subprocess import call, Popen, PIPE
WIN32 = True if sys.platform.startswith('win') else False
if WIN32:
  import winhelper
DISABLE_LIVE_TRANSCODE = False
# How long sessions will idle/transcode until killed and cleaned up
SESSION_EXPIRY = helper.hours_to_seconds(6) 

class Segmenter(object):
  def __init__(self, path=None):
    if path:
      self.path = os.path.abspath(path)
    else:  
      name = 'live_segmenter.exe' if WIN32 else 'live_segmenter'
      self.path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), name)
    self.cmd_tmpl = string.Template(self.path+" 10 $tmpDir $segmentPrefix mpegts $startSegment")
    if not helper.validate_exec(self.path):
      DISABLE_LIVE_TRANSCODE = True
      print "Live transcode disabled. Could not find segmenter at path: "+self.path
  
class Ffmpeg(object):
  def __init__(self, path=None):
    if path:
      self.path = os.path.abspath(path)
    else: 
      name = 'ffmpeg.exe' if WIN32 else 'ffmpeg'
      self.path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), name)
    self.cmd_tmpl = string.Template(self.path+" "
      "-ss $startTime "
      "-i \"$videoPath\" "
      "-vcodec libx264 -r 23.976 "
      "-b $bitrate -bt $bitrate -loglevel quiet "
      "-vf \"crop=iw:ih:0:0,scale=$frameWidth:$frameHeight\" -aspect \"$frameWidth:$frameHeight\" "
      "-acodec libmp3lame -ab 48k -ar 48000 -ac 2 -async 1 "
      "-bufsize 1024k -threads 4 -preset fast -tune grain "
      "-f mpegts - ")
    if not helper.validate_exec(self.path):
      DISABLE_LIVE_TRANSCODE = True
      print "Live transcode disabled. Could not find ffmpeg at path: "+self.path

class TranscodeSession(object):
  def __init__(self, transcoder, videoPath):
    self.alive = True
    self.idleTime = 0
    self.lastRequest = time()
    self.transcoder = transcoder
    self.videoPath = videoPath
    self.inspection = self.inspect()
    #self.fps = self.getFps()
    self.duration = self.getDuration()
    self.segment_duration = 10
    self.frame_size = 640,360 #self.getFrameSize()
    self.md5 = md5.new(videoPath).hexdigest()
    self.tmp_dir = transcoder.tmp_dir
    self.ts_filename_tmpl = string.Template("$md5hash-$bitrate-$segment.ts")
    self.current_ffmpeg_process = None
    self.current_segmenter_process = None
    self.win_batch_process = None
  
  def idle_time(self):
    self.idleTime = (time() - self.lastRequest)
    return self.idleTime
    
  def cleanup(self):
    if self.idle_time() > SESSION_EXPIRY:
      if self.current_ffmpeg_process:
        self.current_segmenter_process.kill()
        self.current_ffmpeg_process.kill()
      for ts in os.listdir(self.tmp_dir):
        if ts.startswith(self.md5):
          os.remove(os.path.join(self.tmp_dir, ts))
          self.alive = False
          
          
  def inspect(self):
    proc = Popen([self.transcoder.ffmpeg.path, '-i', self.videoPath], stderr=PIPE)
    proc.wait()
    return proc.stderr.read() 
    
  def getDuration(self):
    pattern = re.compile('Duration:\s([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{2})');
    durationMatch = pattern.search(self.inspection)
    seconds = 0
    seconds += 3600 * int(durationMatch.group(1))
    seconds += 60   * int(durationMatch.group(2))
    seconds += int(durationMatch.group(3))
    seconds += 1#/self.fps * int(durationMatch.group(4))
    return seconds

  def getFrameSize(self):
    pattern = re.compile('Video:\s(.*),(.*),\s(\d*)x(\d*),');
    matches = pattern.search(self.inspection)
    try:
      width = matches.group(3)
      height = matches.group(4)
      return width, height
    except Exception:
      raise 'Problem capturing frame size'
  
  def getFps(self):
    pattern = re.compile('([0-9\.]{5})\sfps')
    fpsString = pattern.search(self.inspection).group(1)
    if fpsString:
      return float(fpsString)
    else:
      return float(24)
      raise 'Problem grabbing FPS'
      
  def call_ffmpeg(self, **kwargs):
    self.killProcessing()
    cmd = self.transcoder.ffmpeg.cmd_tmpl.substitute(
      startTime=int(kwargs['start_segment'])*self.segment_duration,
      videoPath=self.videoPath,
      #duration=kwargs['num_segments']*self.segment_duration,
      frameWidth=self.frame_size[0],
      frameHeight=self.frame_size[1],
      bitrate=int(kwargs['bitrate'])*1000,
    )
    segmenter_cmd = self.transcoder.segmenter.cmd_tmpl.substitute(
      tmpDir=helper.shellquote(self.transcoder.tmp_dir),
      startSegment=kwargs['start_segment'],
      segmentPrefix=self.md5+"-"+kwargs['bitrate'],
    )
    print "About to start processes....."
    if WIN32:
      winCmd = cmd+' | '+segmenter_cmd
      self.win_batch_process_pid = winhelper.runCmdViaBatchFile(winCmd, os.path.join(self.tmp_dir, 'transcode.bat'))
    else:
      with open(os.devnull, 'w') as fp:
        self.current_ffmpeg_process = Popen(shlex.split(cmd), stdout=PIPE, stderr=fp)
        self.current_segmenter_process = Popen(shlex.split(segmenter_cmd), stdin=self.current_ffmpeg_process.stdout, stdout=fp, stderr=fp)
    print "Launched ffmbc and such!"
   
  def killProcessing(self):
    if WIN32 and self.win_batch_process:
      self.win_batch_process.kill()
    elif self.current_ffmpeg_process:
      self.current_segmenter_process.kill()
      self.current_ffmpeg_process.kill()
          
  def transcode(self, seg, br, do_block=True):
    self.lastRequest = time() # Reset the timer.
    seg = int(seg)
    self.ts_file = self.ts_filename_tmpl.substitute(md5hash=self.md5, bitrate=br, segment=seg)
    self.ts_path = os.path.join(self.tmp_dir, self.ts_file)
    ts_file_5 = self.ts_filename_tmpl.substitute(md5hash=self.md5, bitrate=br, segment=seg+5)
    ts_path_5 = os.path.join(self.tmp_dir, ts_file_5)
    if not os.path.exists(self.ts_path):        
      self.call_ffmpeg(start_segment = seg, bitrate=br)
      while not os.path.exists(ts_path_5):
        sleep(5)
        continue      
    return self.ts_path

class Transcoder(object):
  def __init__(self, config):
    self.sessions = {} # We store our TranscodeSessions here
    self.ffmpeg = Ffmpeg(config['ffmpeg_path'])
    self.segmenter = Segmenter(config['segmenter_path'])
    self.rootdir = config['rootdir']
    if config['notes_dir']:
      self.tmp_dir = os.path.join(config['notes_dir'], 'tmp')
    else:
      self.tmp_dir = os.path.join(self.rootdir, 'tmp')
    if not os.path.exists(self.tmp_dir):
      os.makedirs(self.tmp_dir)
      
  def cleanup(self):
    # This method will check self.sessions and ask if they are stale (lastRequest - now)
    # They get "unstale" because we set the session's lastRequest to time() on every segment request
    deadSessions = []
    for md5, session in self.sessions.iteritems():
      if session.alive:
        session.cleanup()
      else:
        deadSessions.append(md5)
    for md5 in deadSessions:
      del self.sessions[md5]
      
  def start_transcoding(self, videoPath):
    if DISABLE_LIVE_TRANSCODE:
      print "Live transcoding is currently disabled! There is a problem with your configuration."
      return
    print "Initiating transcode for asset at path: "+videoPath
    videoPath = unquote(videoPath)
    video_md5 = md5.new(videoPath).hexdigest()
    if self.sessions.has_key(video_md5): # Session already exists?
      return self.m3u8_bitrates_for(video_md5)
    transcodingSession = TranscodeSession(self, videoPath)
    self.sessions[transcodingSession.md5] = transcodingSession
    return self.m3u8_bitrates_for(transcodingSession.md5)
    
  def m3u8_segments_for(self, md5_hash, video_bitrate):
    segment = string.Template("#EXTINF:$length,\n$md5hash-$bitrate-$segment.ts\n")
    partCount = math.floor(self.sessions[md5_hash].duration / 10)
    m3u8_segment_file = "#EXTM3U\n#EXT-X-TARGETDURATION:10\n"
    for i in range(0, int(partCount)):
      m3u8_segment_file += segment.substitute(length=10, md5hash=md5_hash, bitrate=video_bitrate, segment=i)
    last_segment_length = math.ceil((self.sessions[md5_hash].duration - (partCount * 10)))
    m3u8_segment_file += segment.substitute(length=last_segment_length, md5hash=md5_hash, bitrate=video_bitrate, segment=i)
    m3u8_segment_file += "#EXT-X-ENDLIST"
    return m3u8_segment_file
    
  def m3u8_bitrates_for(self, md5_hash):
    m3u8_fudge = string.Template(
      "#EXTM3U\n"
     # "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=384000\n"
     # "$hash-384-segments.m3u8\n"
     # "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=512000\n"
     # "$hash-512-segments.m3u8\n"
      "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=768000\n"
      "$hash-768-segments.m3u8\n"
     # "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1024000\n"
     # "$hash-1024-segments.m3u8\n"
    )
    return m3u8_fudge.substitute(hash=md5_hash)

  def segment_path(self, md5_hash, the_bitrate, segment_number):
    # A segment was requested.
    path = self.sessions[md5_hash].transcode(segment_number, the_bitrate)
    if path:
      return path
    else:
      raise "Segment path not found"
