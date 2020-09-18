CXXFLAGS = -std=c++11 -O3 -Wall -no-pie

TARGET = plaincmp
all = $(TARGET)

plaincmp: ./plaincmp.cpp ./plaincmp.h
	g++ ./plaincmp.cpp -o $@ $(CXXFLAGS)

.PHONY: clean
clean:
	rm -f plaincmp

