#!/usr/bin/env python3
"""
Count the frequency of passwords, or segments
"""
import argparse
import random
import re
from enum import Enum
from typing import TextIO

from collections import defaultdict

import sys


class DefSplitter(Enum):
    WHOLE = "whole"
    CHR = "chr"


def count(file: TextIO, sample_size: int, splitter: str, start: int, step: int):
    counter = defaultdict(int)
    universe = []
    for line in file:
        line = line.strip("\r\n")
        universe.append(line)
    samples = random.sample(universe, min(sample_size, len(universe)))
    for line in samples:
        if splitter == DefSplitter.WHOLE:
            sections = [line]
        elif splitter == DefSplitter.CHR:
            sections = list(line)
        else:
            sections = [s for s in re.split(splitter, line) if len(s) > 0]
            sections = sections[start:len(sections):step]
        for sec in sections:
            counter[sec] += 1
    frequencies = sorted(counter.values(), reverse=True)
    return frequencies


def wrapper():
    cli = argparse.ArgumentParser("Count frequency")
    cli.add_argument("-f", "--file", dest="file", required=True, type=argparse.FileType('r'), help="file to be counted")
    cli.add_argument("-s", "--save", dest="save", required=True, type=argparse.FileType('w'),
                     help="frequencies will be saved here.")
    cli.add_argument("--splitter", dest="splitter", required=False, type=lambda s: s.replace("\\\\", "\\"),
                     default=DefSplitter.WHOLE,
                     help=f"`{DefSplitter.WHOLE.value}` to count the appearance of whole password, "
                          f"`{DefSplitter.CHR.value}` to count that of characters, "
                          f"any other strings to split the password and count the split segments.")
    cli.add_argument("--start", dest="start", required=False, type=int, default=0,
                     help="split the password, and the first element counted is at index of \"start\".")
    cli.add_argument("--step", dest="step", required=False, type=int, default=1,
                     help="split the password, and the next element counted is "
                          "\"step\" distance away from the previous element.")
    cli.add_argument("--sample", dest="sample", required=False, type=int, default=sys.maxsize, help="sample size")
    cli.add_argument("--end", dest="end", required=False, type=str, default="\n", help="end of a line.")
    args = cli.parse_args()
    frequencies = count(file=args.file, sample_size=args.sample, splitter=args.splitter, start=args.start,
                        step=args.step)
    fd_out: TextIO = args.save
    line_end: str = args.end
    for freq in frequencies:
        fd_out.write(f"{freq}{line_end}")
    fd_out.flush()
    fd_out.close()
    pass


if __name__ == '__main__':
    wrapper()
