#!/usr/bin/env python3
"""
A and B have the same passwords, and this file is helpful to find them.
"""
import argparse
from collections import defaultdict
from typing import Dict, TextIO, Union

import sys


def overlap(pwd_cnt_a: Dict[str, int], pwd_cnt_b: Dict[str, int], all_cnt_a, all_cnt_b):
    both = {k: (pwd_cnt_a[k], all_cnt_a[k], all_cnt_b[k]) for k in pwd_cnt_a if k in pwd_cnt_b}
    only_a = {k: (pwd_cnt_a[k], all_cnt_a[k], all_cnt_b[k]) for k in pwd_cnt_a if k not in pwd_cnt_b}
    only_b = {k: (pwd_cnt_b[k], all_cnt_a[k], all_cnt_b[k]) for k in pwd_cnt_b if k not in pwd_cnt_a}
    return both, only_a, only_b


def read_pwd_cnt(fd: TextIO, close_fd: bool = True, number: int = 10 ** 14):
    pwd_cnt = defaultdict(int)
    all_cnt = defaultdict(float)
    for line in fd:
        line = line.strip("\r\n")
        items = line.split('\t')
        pwd = items[0]
        cnt = int(items[2])
        prob = float(items[1])
        n = int(items[3])
        all_cnt[pwd] = prob
        if n > number:
            continue
        pwd_cnt[pwd] += cnt
    if close_fd:
        fd.close()
    return pwd_cnt, all_cnt


def wrapper(fd_a: TextIO, fd_b: TextIO, fd_both: Union[None, TextIO] = None, fd_only_a: Union[None, TextIO] = None,
            fd_only_b: Union[None, TextIO] = None, number: int = 10 ** 14):
    if all([fd is None for fd in [fd_both, fd_only_a, fd_only_b]]):
        print(f"Specify at least one of the following files:\n"
              f"1. only a\n2. only b\n3. both", file=sys.stderr)
    pwd_cnt_a, all_cnt_a = read_pwd_cnt(fd_a, number)
    pwd_cnt_b, all_cnt_b = read_pwd_cnt(fd_b, number)
    both, only_a, only_b = overlap(pwd_cnt_a, pwd_cnt_b, all_cnt_a, all_cnt_b)
    lst = [(fd_both, both), (fd_only_a, only_a), (fd_only_b, only_b)]
    for fd, d in lst:
        if fd is not None:
            if not fd.writable():
                raise Exception(f"{fd} not writable")
            for p, c in d.items():
                fd.write(f"{p}\t{c[0]}\t{c[1]}\t{c[2]}\n")
            fd.close()
    pass


def main():
    cli = argparse.ArgumentParser("Find overlap of two datasets of cracked passwords")
    cli.add_argument("-a", "--pwd-set-a", dest="pwd_set_a", type=argparse.FileType('r'), required=True,
                     help="Dataset A of given passwords.")
    cli.add_argument("-b", "--pwd-set-b", dest="pwd_set_b", type=argparse.FileType('r'), required=True,
                     help="Dataset B of given passwords.")
    cli.add_argument("--only-a", dest="only_a", type=argparse.FileType('w'), required=False, default=None,
                     help="Output passwords appear in dataset A only.")
    cli.add_argument("--only-b", dest="only_b", type=argparse.FileType('w'), required=False, default=None,
                     help="Output passwords appear in dataset B only.")
    cli.add_argument("--both", dest="both", type=argparse.FileType('w'), required=False, default=None,
                     help="Output passwords appear in both datasets")
    cli.add_argument("--number", dest="number", type=int, required=False, default=10 ** 14,
                     help="Guess number less than it")
    args = cli.parse_args()

    wrapper(fd_a=args.pwd_set_a, fd_b=args.pwd_set_b, fd_both=args.both, fd_only_a=args.only_a, fd_only_b=args.only_b,
            number=args.number)
    pass


if __name__ == '__main__':
    main()
    pass
