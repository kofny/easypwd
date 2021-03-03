#!/usr/bin/env python3
"""
Calculation of Unsafe Errors
"""
import argparse
import re
from math import floor, ceil
from typing import TextIO, Tuple, Set


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
    num_list = [n for _, _, n in lst]
    total = sum(num_list)
    top_25 = floor(0.25 * total)
    bottom_25 = ceil(0.75 * total)
    easiest_items = [p for p, _, _ in lst[:top_25]]
    hardest_items = [p for p, _, _ in lst[bottom_25:]]
    return set(easiest_items), set(hardest_items), total


def count_unsafe(data4a: Tuple[Set[str], Set[str], int], data4b: Tuple[Set[str], Set[str], int]):
    easy_a, hard_a, total_a = data4a
    easy_b, hard_b, total_b = data4b
    if total_a != total_b:
        raise Exception("Check whether the two datasets are the same.")
        pass
    a_easy_b_hard = easy_a & hard_b
    a_hard_b_easy = hard_a & easy_b

    return a_easy_b_hard, a_hard_b_easy, total_a


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
    args = cli.parse_args()
    a_easy_b_hard, a_hard_b_easy, total = count_unsafe(
        read_raw_data(args.fd_a, args.skip, args.splitter, args.idx_pwd, args.idx_rank, args.idx_freq),
        read_raw_data(args.fd_b, args.skip, args.splitter, args.idx_pwd, args.idx_rank, args.idx_freq))
    print(f"a easiest 25% in b hardest 25%: {len(a_easy_b_hard):8}, {len(a_easy_b_hard) / total * 100:5.2f}%")
    print(f"a hardest 25% in b easiest 25%: {len(a_hard_b_easy):8}, {len(a_hard_b_easy) / total * 100:5.2f}%")
    pass


if __name__ == '__main__':
    wrapper()
