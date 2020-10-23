CXXFLAGS = -std=c++11 -O3 -Wall -no-pie

TARGET = plaincmp
all = $(TARGET)

plaincmp: ./kits/plaincmp.cpp ./kits/plaincmp.h
	g++ ./kits/plaincmp.cpp -o $@ $(CXXFLAGS)

.PHONY: clean
clean:
	rm -f plaincmp

