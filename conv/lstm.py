#!/usr/bin/env python3
"""
Convert output of LSTM Monte Carlo Simulation to another format
"""
import argparse
import math
import sys
from collections import defaultdict
from typing import TextIO, Dict, Tuple


def read_nn(fd_csv: TextIO):
    pwd_dict = {}
    for line in fd_csv:
        lst = line.strip("\r\n").split('\t')
        pwd, prob, guess_number = lst[0:3]
        pwd_dict[pwd] = (float(prob), float(guess_number))
    fd_csv.close()
    return pwd_dict


def read_test(fd_test: TextIO):
    pwd_cnt = defaultdict(int)
    for line in fd_test:
        line = line.strip()
        pwd_cnt[line] += 1
    fd_test.close()
    return pwd_cnt


def reformat(pwd_dict: Dict[str, Tuple[float, float]], pwd_cnt: Dict[str, int], fd_save: TextIO):
    pwd_lst = []
    for pwd, cnt in pwd_cnt.items():
        if pwd not in pwd_dict:
            pwd_lst.append((pwd, sys.float_info.min, cnt, 10 ** 50))
        else:
            prob, guess_number = pwd_dict[pwd]
            pwd_lst.append((pwd, max(prob, sys.float_info.min), cnt, guess_number))
    pwd_lst = sorted(pwd_lst, key=lambda x: x[3])
    total = sum(pwd_cnt.values())
    del pwd_cnt, pwd_dict
    cracked = 0
    prev_guess_number = 0
    for pwd, prob, cnt, guess_number in pwd_lst:
        cracked += cnt
        crack_rate = cracked / total * 100
        guess_number = max(prev_guess_number + 1, math.ceil(guess_number))
        prev_guess_number = guess_number
        fd_save.write(f"{pwd}\t{-math.log2(prob)}\t{cnt}\t{guess_number}\t{cracked}\t{crack_rate}\n")
    fd_save.close()


def wrapper():
    cli = argparse.ArgumentParser("LSTM Monte Carlo results convertor")
    cli.add_argument("-c", "--csv", dest="fd_lstm_csv", type=argparse.FileType('r'),
                     help="lstm csv file for monte carlo")
    cli.add_argument("-t", "--test", dest="fd_test_set", type=argparse.FileType('r'),
                     help="test set")
    cli.add_argument("-o", "--save", dest="fd_save", type=argparse.FileType('w'),
                     help="save results")
    args = cli.parse_args()
    pwd_dict = read_nn(args.fd_lstm_csv)
    pwd_cnt = read_test(args.fd_test_set)
    reformat(pwd_dict, pwd_cnt, args.fd_save)


if __name__ == '__main__':
    wrapper()
