#!/usr/bin/env python3
"""
The original format of a line in the given source file is :
<p1234p>\t<A1D4A1>
The parsed format is:
<p1234p>\t<p>\t<A1>\t<1234>\t<D4>\t<p>\t<A1>
"""
import argparse
import re
from collections import defaultdict
from typing import TextIO

terminal_re = re.compile(r"([ADKOXY]\d+)")


def read_pwd(fd: TextIO, testing: TextIO, save: TextIO):
    test_set = defaultdict(int)
    for line in testing:
        line = line.strip("\r\n")
        test_set[line] += 1

    for line in fd:
        line = line.strip("\r\n")
        items = [itm for itm in line.split("\t") if len(itm) > 0]
        if len(items) == 2:
            pwd = items[0]
            if pwd not in test_set:
                continue
            struct = items[1]
            terminals = terminal_re.findall(struct)
            start = 0
            lst = [pwd, f"{test_set[pwd]}"]
            for terminal in terminals:
                # tag = terminal[0]
                num = int(terminal[1:])
                segment = pwd[start:start + num]
                start += num
                lst.append(segment)
                lst.append(terminal)
            pass

            save.write("\t".join(lst) + "\n")
        pass
    fd.close()
    save.flush()
    save.close()
    pass


def wrapper():
    cli = argparse.ArgumentParser("post-parsing structure for pcfgv4.1")
    cli.add_argument("--struct", dest="struct", type=argparse.FileType('r'), help="struct file")
    cli.add_argument("--testing", dest="testing", type=argparse.FileType('r'), help="testing set")
    cli.add_argument("--save", dest="save", type=argparse.FileType('w'), help="save results")
    args = cli.parse_args()
    read_pwd(args.struct, args.testing, args.save)
    pass


if __name__ == '__main__':
    wrapper()
