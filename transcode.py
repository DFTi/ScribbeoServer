import os
import sys
import string
import re
import md5
import math
import time
import shlex
from urllib import unquote
from subprocess import call, Popen, PIPE

WIN32 = True if sys.platform.startswith('win32') else False

def shellquote(path):
  #return path
  if WIN32:
    return '"'+path+'"'
  else:
    return path.replace(' ', '\ ')
    

class TranscodeSession(object):
  def __init__(self, transcoder, videoPath):
    if sys.platform.startswith('win32'):
      raise "live_segmenter not built for windows!!!!"
    self.segmenter_path = os.path.abspath(os.path.dirname(sys.argv[0]))+'live_segmenter'
    ## The above will not work on windows :/
    self.ffmpegs = {}
    """
    ffmpegs = {
      "hashvalue":Ffmpeg
    }
    """
    self.transcoder = transcoder
    if self.transcoder.ffmpeg_path:
      self.ffmpeg_path = self.transcoder.ffmpeg_path
    else:
      self.ffmpeg_path = string.strip(os.popen('which ffmpeg').read())
    self.videoPath = videoPath
    self.inspection = self.inspect()
    #self.fps = self.getFps()
    self.duration = self.getDuration()
    self.segment_duration = 10
    self.frame_size = 640,360#self.getFrameSize()
    self.md5 = md5.new(videoPath).hexdigest()
    self.tmp_dir = transcoder.tmp_dir
    self.ts_filename_tmpl = string.Template("$md5hash-$bitrate-$segment.ts")
    self.current_ffmpeg_process = False
    self.ffmpeg_cmd_tmpl = string.Template(self.ffmpeg_path+" "
    "-ss $startTime "
    "-i \""+videoPath+"\" "
    #"-analyzeduration 100000000 "
    "-vcodec libx264 -r 23.976 "
    "-b $bitrate -bt $bitrate "
    "-vf \"crop=iw:ih:0:0,scale=$frameWidth:$frameHeight\" -aspect \"$frameWidth:$frameHeight\" "
    "-acodec libmp3lame -ab 48k -ar 48000 -ac 2 -async 1 "
    "-bufsize 1024k -threads 4 -preset superfast -tune grain "
    #"-flags2 +fast -flags +loop -g 30 -keyint_min 1 -bf 0 -b_strategy 0 "
    #"-sc_threshold 40 -me_range 16 -subq 5 -qmax 48 -qmin 2 "
    #"-deblockalpha 0 -deblockbeta 0 -refs 1 -coder 0 "
    #"-loglevel quiet "
    "-f mpegts - ")
    self.segmenter_cmd_tmpl = string.Template("./live_segmenter 10 "+shellquote(self.tmp_dir)+" $segmentPrefix mpegts $startSegment")
      # FIXME: Detect CPU's for optimized transcoding (threads)
    #self.cached_segments = [0]*int(math.ceil(self.duration/10)) # init list with 10 0's ... [seg] = 0:uncached, 1:processing, 2:cached
    #self.current_ffmpeg_process = False
    #self.cached_segment_chunk_size = 10
  """    
      /usr/local/bin/ffmpeg -i /Library/WebServer/Documents/Projects/DFT/Test_Movs/Dexter.S06E01.REPACK.720p.HDTV.x264-IMMERSE.mkv -ss 0 -t 60 -vcodec libx264 -y -r 23.976 -acodec libfaac -bufsize 2048k -vf "crop=iw:ih:0:0,scale=640:360" -aspect "640:360" -threads 4 -preset ultrafast -tune film -b 1024000 -f mpegts - | ./live_segmenter 10 /Library/WebServer/Documents/Projects/DFT/Test_Movs/tmp/ namePrefix mpegts
  """
    
  def inspect(self):
    proc = Popen([self.ffmpeg_path, '-i', self.videoPath], stderr=PIPE)
    time.sleep(1)
    return proc.stderr.read()
    
    
  def getDuration(self):
    #print "INSPECTION FROM getDURATION IS CURRENTLY: "+self.inspection 
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
    if self.current_ffmpeg_process:
      self.current_segmenter_process.kill()
      self.current_ffmpeg_process.kill()
    cmd = self.ffmpeg_cmd_tmpl.substitute(
      startTime=int(kwargs['start_segment'])*self.segment_duration,
      #duration=kwargs['num_segments']*self.segment_duration,
      frameWidth=self.frame_size[0],
      frameHeight=self.frame_size[1],
      bitrate=int(kwargs['bitrate'])*1000,
    )
    
    segmenter_cmd = self.segmenter_cmd_tmpl.substitute(
      startSegment=kwargs['start_segment'],
      segmentPrefix=self.md5+"-"+kwargs['bitrate'],
    )
    
    print cmd
    
    self.current_ffmpeg_process = Popen(shlex.split(cmd), stdout=PIPE)
    self.current_segmenter_process = Popen(shlex.split(segmenter_cmd), stdin=self.current_ffmpeg_process.stdout)
    
  def transcode(self, seg, br, do_block=True):
    seg = int(seg)
    
    self.ts_file = self.ts_filename_tmpl.substitute(md5hash=self.md5, bitrate=br, segment=seg)
    self.ts_path = os.path.join(self.tmp_dir, self.ts_file)
    ts_file_5 = self.ts_filename_tmpl.substitute(md5hash=self.md5, bitrate=br, segment=seg+5)
    ts_path_5 = os.path.join(self.tmp_dir, ts_file_5)
      
    print "TRANSCODE REQUESTED FOR SEGMENT "+str(seg)+" with bitrate "+br+" at path:"+self.ts_path
      
    if not os.path.exists(self.ts_path):        
      self.call_ffmpeg(start_segment = seg, bitrate=br)
      while not os.path.exists(ts_path_5):
        continue
      
      #time.sleep(20)
      
    return self.ts_path

class Transcoder(object):
  def __init__(self, config):
    self.rootdir = config['rootdir']
    self.ffmpeg_path = config['ffmpeg_path'] if config.has_key('ffmpeg_path') else None
    self.tmp_dir = os.path.join(self.rootdir, 'tmp')
    if not os.path.exists(self.tmp_dir):
      os.makedirs(self.tmp_dir)
    self.sessions = {}
      
  def start_transcoding(self, videoPath):
    print "Initiating transcode for "+videoPath
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
    path = self.sessions[md5_hash].transcode(segment_number, the_bitrate)
    if path:
      return path
    else:
      raise "Segment path not found"


"""
ScribbeoServer git:(live_transcode)  ffmpeg -i clips/Cuts/311\ PC01\ 111411.mov 
ffmpeg version 0.8.7, Copyright (c) 2000-2011 the FFmpeg developers
  built on Dec  9 2011 20:01:29 with clang 3.0 (tags/Apple/clang-211.12)
  configuration: --prefix=/usr/local/Cellar/ffmpeg/0.8.7 --enable-shared --enable-gpl --enable-version3 --enable-nonfree --enable-hardcoded-tables --cc=/usr/bin/clang --enable-libx264 --enable-libfaac --enable-libmp3lame --enable-libtheora --enable-libvorbis --enable-libvpx --enable-libxvid --disable-ffplay
  libavutil    51.  9. 1 / 51.  9. 1
  libavcodec   53.  8. 0 / 53.  8. 0
  libavformat  53.  5. 0 / 53.  5. 0
  libavdevice  53.  1. 1 / 53.  1. 1
  libavfilter   2. 23. 0 /  2. 23. 0
  libswscale    2.  0. 0 /  2.  0. 0
  libpostproc  51.  2. 0 / 51.  2. 0
[mov,mp4,m4a,3gp,3g2,mj2 @ 0x7fa7b4007c00] max_analyze_duration 5000000 reached at 5015510

Seems stream 1 codec frame rate differs from container frame rate: 47952.00 (47952/1) -> 23.98 (2997/125)
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'clips/Cuts/311 PC01 111411.mov':
  Metadata:
    creation_time   : 2011-11-14 23:53:55
  Duration: 00:23:07.74, start: 0.000000, bitrate: 2335 kb/s
    Stream #0.0(eng): Audio: aac, 44100 Hz, stereo, s16, 106 kb/s
    Metadata:
      creation_time   : 2011-11-14 23:53:55
    Stream #0.1(eng): Video: h264 (Main), yuv420p, 420x236, 2218 kb/s, 23.98 fps, 23.98 tbr, 23976 tbn, 47952 tbc
    Metadata:
      creation_time   : 2011-11-14 23:53:55
    Stream #0.2(eng): Data: tmcd / 0x64636D74
    Metadata:
      creation_time   : 2011-11-15 00:12:13
At least one output file must be specified

/Applications/Air Video Server.app/Contents/Resources/ffmpeg
--conversion-id 78e55543-1af1-4e75-8584-3c0ad80cc128
--port-number 46631
-threads 4
-flags2 +fast
-flags +loop
-g 30
-keyint_min 1
-bf 0
-b_strategy 0
-flags2
-wpred-dct8x8
-cmp +chroma
-deblockalpha 0
-deblockbeta 0
-refs 1
-coder 0
-me_range 16
-subq 5
-partitions +parti4x4+parti8x8+partp8x8
-trellis 0
-sc_threshold 40
-i_qfactor 0.71
-qcomp 0.6
-map 0.0:0.0
-map 0.2:0.2
-ss 0.0
-i /Users/keyvan/Projects/ScribbeoServer/clips/Cuts/test.mov
-cropleft 0
-cropright 0
-croptop 0
-cropbottom 0
-s 818x460
-aspect 1.7782608
-y
-f mpegts
-vcodec libx264
-bufsize 512k
-b 1200k
-bt 1300k
-qmax 48
-qmin 2
-r 23.976
-acodec libmp3lame
-ab 192k
-ar 44100
-vol 765
-ac 2
-


"""