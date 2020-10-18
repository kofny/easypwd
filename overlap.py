#!/usr/bin/env python3
"""
A and B have the same passwords, and this file is helpful to find them.
"""
from collections import defaultdict
from typing import Dict, TextIO, Union


def overlap(pwd_cnt_a: Dict[str, int], pwd_cnt_b: Dict[str, int]):
    both = {k: pwd_cnt_a[k] for k in pwd_cnt_a if k in pwd_cnt_b}
    only_a = {k: pwd_cnt_a[k] for k in pwd_cnt_a if k not in pwd_cnt_b}
    only_b = {k: pwd_cnt_b[k] for k in pwd_cnt_b if k not in pwd_cnt_a}
    return both, only_a, only_b


def read_pwd_cnt(fd: TextIO, close_fd: bool = True):
    pwd_cnt = defaultdict(int)
    for line in fd:
        pwd_cnt[line.strip("\r\n")] += 1
    if close_fd:
        fd.close()
    return pwd_cnt


def wrapper(fd_a: TextIO, fd_b: TextIO, fd_both: Union[None, TextIO] = None, fd_only_a: Union[None, TextIO] = None,
            fd_only_b: Union[None, TextIO] = None):
    pwd_cnt_a = read_pwd_cnt(fd_a)
    pwd_cnt_b = read_pwd_cnt(fd_b)
    both, only_a, only_b = overlap(pwd_cnt_a, pwd_cnt_b)
    for fd, d in [(fd_both, both), (fd_only_a, only_a), (fd_only_b, only_b)]:
        if fd is not None:
            if not fd.writable():
                raise Exception(f"{fd} not writable")
            for p, c in d.items():
                fd.write(f"{p}\t{c}\n")
            fd.close()
    pass


def main():
    pass


if __name__ == '__main__':
    wrapper(open("/home/cw/Documents/tmp/cracked_pwd.txt"), open("/home/cw/Documents/tmp/real_cracked.txt"),
            fd_only_b=open("/home/cw/Documents/tmp/real_only.txt", "w"))
    pass
