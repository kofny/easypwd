CXXFLAGS = -std=c++11 -O3 -Wall -no-pie

TARGET = target_stat.log_prob
all = $(TARGET)

target_stat.log_prob: ./TargetStat.cpp ./TargetStat.h
	g++ ./TargetStat.cpp -o $@ $(CXXFLAGS)

.PHONY: clean
clean:
	rm -f target_stat.log_prob

