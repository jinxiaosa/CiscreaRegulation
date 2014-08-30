libs=$$(pkg-config --cflags --libs opencv)

all:
	
	#mkdir build/
	g++ video.cpp $(libs) -I /opt/local/include -o exvideo.o
	#mv *.o build/
clean:
	rm -rf build exvideo* 
