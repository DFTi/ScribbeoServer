all:
	gcc -Wall -g live_segmenter.c -o live_segmenter -lavformat -lavcodec -lavutil -lbz2 -lm -lz -lfaac -lx264 -lpthread

clean:
	rm -f live_segmenter
