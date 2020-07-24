CXXFLAGS = -std=c++11 -O3 -Wall -no-pie

TARGET = target_stat
all = $(TARGET)

target_stat: ./plaincmp.cpp ./plaincmp.h
	g++ ./plaincmp.cpp -o $@ $(CXXFLAGS)

.PHONY: clean
clean:
	rm -f target_stat

