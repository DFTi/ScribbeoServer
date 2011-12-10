import os
import string
import re
import md5
import math
from subprocess import Popen, PIPE

class TranscodeSession(object):
  def __init__(self, transcoder, videoPath):
    self.transcoder = transcoder
    if self.transcoder.ffmpeg_path:
      self.ffmpeg_path = self.transcoder.ffmpeg_path
    else:
      self.ffmpeg_path = string.strip(os.popen('which ffmpeg').read())
    self.videoPath = videoPath
    self.inspection = self.inspect()
    self.fps = self.getFps()
    self.duration = self.getDuration()
    self.frame_size = self.getFrameSize()
    self.md5 = md5.new(videoPath).hexdigest()
    self.tmp_dir = transcoder.tmp_dir
    self.ts_filename_tmpl = string.Template("$md5_$bitrate_$segment.ts")
    
  def inspect(self):
    proc = Popen([self.ffmpeg_path, '-i', self.videoPath], stderr=PIPE)
    return proc.stderr.read()
    
  def getDuration(self):
    pattern = re.compile('Duration:\s([0-9]{2}):([0-9]{2}):([0-9]{2}).([0-9]{2})');
    durationMatch = pattern.search(self.inspection)
    try:
      self.durationStamp = "%s:%s:%s.%s" % (
        durationMatch.group(1),
        durationMatch.group(2),
        durationMatch.group(3),
        durationMatch.group(4)
      )
      seconds = 0
      seconds += 3600 * int(durationMatch.group(1))
      seconds += 60   * int(durationMatch.group(2))
      seconds += int(durationMatch.group(3))
      seconds += 1/self.fps * int(durationMatch.group(4))
      return seconds
    except Exception:
      raise 'Problem grabbing duraton'

  def getFrameSize(self):
    pattern = re.compile('Video:\s(.*),(.*),\s(\d*)x(\d*),');
    matches = pattern.search(self.inspection)
    try:
      width = matches.group(3)
      height = matches.group(4)
      return width, height
    except Exception:
      raise "Could not capture frame size"
          
  def getFps(self):
    pattern = re.compile('([0-9\.]{5})\sfps');
    print self.inspection
    fpsString = pattern.search(self.inspection).group(1)
    if fpsString:
      return float(fpsString)
    else:
      raise 'Problem grabbing FPS'
  
  def transcode(seg, br):
    ts_file = self.ts_path_tmpl.substitute(md5=self.md5, bitrate=br, segment=seg)
    ts_path = os.path.join(self.tmp_dir, self.ts_file)
    cmd = str(
      ("%s " % self.ffmpeg_path)
      ("-i %s " % self.videoPath)
      ("-ss \"%s\" " % self.transcoder.segment_number_to_time_offset(seg)) # start time
      ("-t 10 ") # Segment duration, 10 seconds
      ("-vcodec libx264 -y ") # Use h264, and overwrite if necessary
      ("-r 23.976 ") # Output framerate, standard h264 framerate
      ("")
      ("%s" % ts_path)
    )

class Transcoder(object):
  def __init__(self, config):
    self.rootdir = config['rootdir']
    self.ffmpeg_path = config['ffmpeg_path'] if config.has_key('ffmpeg_path') else None
    self.tmp_dir = os.path.join(self.rootdir, 'tmp')
    if not os.path.exists(self.tmp_dir):
      os.makedirs(self.tmp_dir)
    self.sessions = {}
      
  def start_transcoding(self, videoPath):
    transcodingSession = TranscodeSession(self, videoPath)
    self.sessions[transcodingSession.md5] = transcodingSession
    return self.m3u8_bitrates_for(transcodingSession.md5)
    
  def m3u8_segments_for(self, md5_hash, video_bitrate):
    segment = string.Template("#EXTINF:$length,\ntranscoder/$hash/$bitrate/$segment.ts\n")
    partCount = math.floor(self.sessions[md5_hash].duration / 10)
    m3u8_segment_file = "#EXTM3U\n#EXT-X-TARGETDURATION:10\n"
    for i in range(0, partCount):
      m3u8_segment_file += segment.substitute(length=10, hash=md5_hash, bitrate=video_bitrate, segment=i)
      last_segment_length = self.sessions[md5_hash].duration - (partCount * 10)
      m3u8_segment_file += segment.substitute(length=last_segment_length, hash=md5_hash, bitrate=video_bitrate, part=i)
      m3u8_segment_file += "#EXT-X-ENDLIST"
    return m3u8_segment_file
    
  def m3u8_bitrates_for(self, md5_hash):
    m3u8_fudge = string.Template(
      "#EXTM3U\n"
      "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=384000\n"
      "transcoder/$hash/384/segments.m3u8\n"
      "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=512000\n"
      "transcoder/$hash/512/segments.m3u8\n"
      "#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=768000\n"
      "transcoder/$hash/768/segments.m3u8\n"
    );
    return m3u8_fudge.substitute(hash=md5_hash)

  def segment_path(self, md5_hash, the_bitrate, segment_number):
    path = self.sessions[md5_hash].transcode(segment_number, the_bitrate)
    if path:
      return 'Segment not found'
    else:
      return path
        
 ### 00:24:01.49
  
  
  
  
  """
  Here is an example of how to use a Template:

>>> from string import Template
>>> s = Template('$who likes $what')
>>> s.substitute(who='tim', what='kung pao')
'tim likes kung pao'
>>> d = dict(who='tim')
>>> Template('Give $who $100').substitute(d)
Traceback (most recent call last):
[...]
ValueError: Invalid placeholder in string: line 1, col 10
>>> Template('$who likes $what').substitute(d)
Traceback (most recent call last):
[...]
KeyError: 'what'
>>> Template('$who likes $what').safe_substitute(d)
'tim likes $what'
  """
  
  
"""
#EXTM3U
#EXT-X-TARGETDURATION:10
#EXTINF:10,
segment_ab9d5cf6-d983-4ca2-809d-8827ca723ff6_512_part0.ts
#EXTINF:10,
segment_ab9d5cf6-d983-4ca2-809d-8827ca723ff6_512_part1.ts
#EXTINF:10,
segment_ab9d5cf6-d983-4ca2-809d-8827ca723ff6_512_part2.ts
#EXTINF:10,
segment_ab9d5cf6-d983-4ca2-809d-8827ca723ff6_512_part3.ts
#EXTINF:10,
segment_ab9d5cf6-d983-4ca2-809d-8827ca723ff6_512_part4.ts
#EXTINF:8,
segment_ab9d5cf6-d983-4ca2-809d-8827ca723ff6_512_part576.ts
#EXT-X-ENDLIST
"""