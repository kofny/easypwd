#!/usr/bin/env python3
"""
Compare the ranks obtained by two methods in a table
Note that the passwords and their frequencies should be the same in the two input files
"""
import argparse
import bisect
import re
import sys
from collections import defaultdict
from typing import TextIO, List, Dict, Tuple


def read_raw_data(fd: TextIO, skip=1, splitter=re.compile("\t"), idx_pwd=0, idx_rank=1, idx_num=2):
    lst = []
    for _ in range(skip):
        fd.readline()
    for line in fd:
        line = line.strip("\r\n")
        items = splitter.split(line)
        pwd = items[idx_pwd]
        rank = float(items[idx_rank])
        num = int(items[idx_num])
        lst.append((pwd, rank, num))
    fd.close()
    lst = sorted(lst, key=lambda x: x[1])
    _map = {pwd: (rank, freq) for pwd, rank, freq in lst}
    return _map


def gen_table(guess_number_thresholds: List[int], guess_number_display_list: List[str],
              map_a: Dict[str, Tuple[int, int]], map_b: Dict[str, Tuple[int, int]]):
    table = defaultdict(lambda: defaultdict(lambda: 0))
    for pwd, info_a in map_a.items():
        rank_a, cnt = info_a
        # info_b = map_b.get(pwd, (sys.maxsize, info_a[1]))
        rank_b = map_b.get(pwd, (sys.maxsize, cnt))[0]
        idx_a = bisect.bisect_left(guess_number_thresholds, rank_a)
        idx_b = bisect.bisect_left(guess_number_thresholds, rank_b)
        table[idx_b][idx_a] += cnt
    total = sum([f for _, f in map_a.values()])

    def print_table(splitter="\t", percent=True):
        for i in range(1, len(guess_number_thresholds) + 1):
            print(guess_number_display_list[i - 1], end=splitter)
            for j in range(1, len(guess_number_thresholds) + 1):
                if j == len(guess_number_thresholds):
                    the_end = " \\\\\n"
                else:
                    the_end = splitter
                if percent:
                    print(f"{table[i][j] / total * 100:5.2f}%", end=the_end)
                else:
                    print(f"{table[i][j]:10,d}", end=the_end)

    print("Print percentages, LaTeX format.\n"
          "file a is placed on the top of the table, file b is placed on the left of the table.")
    print_table(" & ", True)
    print("Print frequencies, LaTeX format")
    print_table(" & ", False)
    pass


def wrapper():
    cli = argparse.ArgumentParser("Unsafe Errors")
    cli.add_argument("-a", "--file-a", dest="fd_a", required=True, type=argparse.FileType('r'),
                     help="one file containing passwords, ranks and frequencies")
    cli.add_argument("-b", "--file-b", dest="fd_b", required=True, type=argparse.FileType('r'),
                     help="another file containing passwords, ranks and frequencies")
    cli.add_argument("--idx-pwd", dest="idx_pwd", required=True, type=int,
                     help="passwords are in \"idx-pwd\"th column, start from 0")
    cli.add_argument("--idx-rank", dest="idx_rank", required=True, type=int,
                     help="ranks are in \"idx-rank\"th column, start from 0")
    cli.add_argument("--idx-freq", dest="idx_freq", required=True, type=int,
                     help="frequencies are in \"idx-freq\"th column, start from 0")
    cli.add_argument("-k", "--skip", dest="skip", required=False, type=int, default=1,
                     help="Ignore the first k lines")
    cli.add_argument("-s", '--splitter', dest="splitter", type=lambda x: re.compile(x), required=False,
                     default=re.compile("\t"),
                     help="splitter of the lines")
    cli.add_argument("-t", "--thresholds", dest="thresholds",
                     default=[0, 10 ** 4, 10 ** 8, 10 ** 12, 10 ** 16, 10 ** 20],
                     type=int, required=False, nargs='+', help="the thresholds of guess numbers")
    cli.add_argument("-d", "--display", dest="display",
                     default=['\\textgreater1e0', '\\textgreater1e4', '\\textgreater1e8', '\\textgreater1e12',
                              '\\textgreater1e16', '\\textgreater1e20'],
                     type=str, required=False, nargs='+',
                     help="How to show the thresholds in string (support LaTex format)")
    args = cli.parse_args()
    gen_table(args.thresholds, args.display,
              read_raw_data(args.fd_a, args.skip, args.splitter, args.idx_pwd, args.idx_rank, args.idx_freq),
              read_raw_data(args.fd_b, args.skip, args.splitter, args.idx_pwd, args.idx_rank, args.idx_freq)
              )
    pass


if __name__ == '__main__':
    wrapper()
