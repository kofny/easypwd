CXXFLAGS = -std=c++11 -O3 -Wall -no-pie

TARGET = plaincmp
all = $(TARGET)

plaincmp: ./guessing/plaincmp.cpp ./guessing/plaincmp.h
	g++ ./guessing/plaincmp.cpp -o $@ $(CXXFLAGS)

.PHONY: clean
clean:
	rm -f plaincmp

