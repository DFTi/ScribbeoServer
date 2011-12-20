/usr/local/bin/ffmpeg -i /Library/WebServer/Documents/Projects/DFT/Test_Movs/Dexter.S06E01.REPACK.720p.HDTV.x264-IMMERSE.mkv -ss 0 -vcodec libx264 -y -r 23.976 -acodec libmp3lame -ab 48k -ar 48000 -ac 2 -bufsize 512k -vf "crop=iw:ih:0:0,scale=640:360" -aspect "640:360" -threads 4 -preset superfast -tune film,grain -profile baseline -b 200k -f mpegts -flags2 +fast -flags +loop - | ./live_segmenter 10 /Library/WebServer/Documents/Projects/DFT/Test_Movs/tmp/ awesome mpegts


ffmpeg -i /Library/WebServer/Documents/Projects/DFT/Test_Movs/VT_24P_TC-iPadDailies.mov -ss 0 -t 60 -vcodec libx264 -y -r 23.976 -acodec libfaac -bufsize 2048k -vf "crop=iw:ih:0:0,scale=640:360" -aspect "640:360" -threads 4 -preset ultrafast -tune film -b 1024000 -f mpegts - | ./live_segmenter 10 /Library/WebServer/Documents/Projects/DFT/Test_Movs/tmp/ a mpegts


ffmpeg -threads 4 -flags2 +fast -flags +loop -g 30 -keyint_min 1 -bf 0 -b_strategy 0 -flags2 -wpred-dct8x8 -cmp +chroma -deblockalpha 0 -deblockbeta 0 -refs 1 -coder 0 -me_range 16 -subq 5 -partitions +parti4x4+parti8x8+partp8x8 -trellis 0 -sc_threshold 40 -i_qfactor 0.71 -qcomp 0.6 -map 0.0:0.0 -map 0.1:0.1 -ss 0.0 -i /Library/WebServer/Documents/Projects/DFT/Test_Movs/Dexter.S06E01.REPACK.720p.HDTV.x264-IMMERSE.mkv -vf "crop=iw:ih:0:0,scale=640:360" -aspect "640:360" -y -f mpegts -vcodec libx264 -bufsize 1024k -b 200k -bt 220k -qmax 48 -qmin 2 -r 23.976 -acodec libmp3lame -ab 48k -ar 48000 -ac 2 - | ./live_segmenter 10 /Library/WebServer/Documents/Projects/DFT/Test_Movs/tmp/ dx mpegts

ffmpeg -i /Library/WebServer/Documents/Projects/DFT/Test_Movs/VT_24P_TC-iPadDailies.mov -ss 0 -t 600 -vcodec libx264 -y -r 23.976 -acodec libfaac -bufsize 2048k -vf "crop=iw:ih:0:0,scale=640:360" -aspect "640:360" -threads 4 -preset ultrafast -tune film -b 1024000 -f mpegts - | mediastreamsegmenter -t 10 -f /Library/WebServer/Documents/Projects/DFT/Test_Movs/tmp/ 

" -threads 4 -flags2 +fast -flags +loop -g 30 -keyint_min 1 -bf 0 -b_strategy 0 -flags2 -wpred-dct8x8 -cmp +chroma -deblockalpha 0 -deblockbeta 0 -refs 1 -coder 0 -me_range 16 -subq 5 -partitions +parti4x4+parti8x8+partp8x8 -trellis 0 -sc_threshold 40 -i_qfactor 0.71 -qcomp 0.6 -map 0.0:0.0 -map 0.1:0.1 -ss $startTime -t 10 -i "+videoPath+" -vf \"crop=iw:ih:0:0,scale=$frameWidth:$frameHeight\" -aspect \"$frameWidth:$frameHeight\" -y -f mpegts -vcodec libx264 -bufsize 1024k -b $bitrate -bt $bitrate -qmax 48 -qmin 2 -r 23.976 -acodec libmp3lame -ab 48k -ar 48000 -ac 2 \"$outFile\""

" "
      "-ss $startTime -t 10 -y "
      "-i "+videoPath+" "
      "-vcodec libx264 "#-preset superfast -tune film,grain -profile baseline "
      "-b $bitrate -bt $bitrate -r 23.976 "
      "-qmax 48 -qmin 2 "
      "-acodec libmp3lame -ab 48k -ar 48000 -ac 2 "
      "-bufsize 1024k "
      "-vf \"crop=iw:ih:0:0,scale=$frameWidth:$frameHeight\" -aspect \"$frameWidth:$frameHeight\" "
      "-threads 4 "
      "-flags2 +fast -flags +loop -g 30 -keyint_min 1 -bf 0 -b_strategy 0 -flags2 -wpred-dct8x8 -cmp +chroma -deblockalpha 0 -deblockbeta 0 -refs 1 -coder 0 -me_range 16 -subq 5 -partitions +parti4x4+parti8x8+partp8x8 -trellis 0 -sc_threshold 40 -i_qfactor 0.71 -qcomp 0.6 -map 0.0:0.0 -map 0.1:0.1 "
      "\"$outFile\""
      
      
      ffmpeg -i /Library/WebServer/Documents/Projects/DFT/Test_Movs/Dexter.S06E01.REPACK.720p.HDTV.x264-IMMERSE.mkv -ss 60 -t 100 -vcodec libx264 -r 23.976 -b 384000 -bt 384000 -vf "crop=iw:ih:0:0,scale=640:360" -aspect "640:360" -acodec libmp3lame -ab 48k -ar 48000 -ac 2 -bufsize 1024k -threads 4 -preset ultrafast -tune film -f mpegts - | ./live_segmenter 10 /Library/WebServer/Documents/Projects/DFT/Test_Movs/tmp 32005e2f1e1df696a409a29e35cae36e-384 mpegts