#!/usr/bin/env python3
"""
Given a number of entries, and a map containing entries and frequencies,
count the frequency of given entries.
"""
import argparse
import re
from collections import defaultdict
from typing import TextIO, Pattern


def count(file: TextIO, splitter: Pattern):
    counter = defaultdict(int)
    for line in file:
        line = line.strip("\r\n")
        items = splitter.split(line)
        if len(items) != 2:
            raise Exception(f"\"{line}\" is abnormal, need \"entry{splitter.pattern}frequency")
        counter[items[0]] += int(items[1])
    file.close()
    return counter


def read_entries(file: TextIO):
    entries = set()
    for line in file:
        line = line.strip("\r\n")
        entries.add(line.lower())
    file.close()
    return entries


def wrapper():
    cli = argparse.ArgumentParser("The code counts the frequency of passwords, segments or characters in a dataset.")
    cli.add_argument("-f", "--file", dest="file", required=True, type=argparse.FileType('r'),
                     help="This file contains all entries and frequencies")
    cli.add_argument("-e", "--entries", dest="entries", required=True, type=argparse.FileType('r'),
                     help="entries to be counted")
    cli.add_argument("-s", "--save", dest="save", required=True, type=argparse.FileType('w'),
                     help="frequencies will be saved here.")
    cli.add_argument("--splitter", dest="splitter", required=False, type=lambda s: re.compile(s),
                     default="\t",
                     help="split the lines in \"-f\" file. If you want to use `Tab`, use $'\\t' in bash")
    args = cli.parse_args()
    counter = count(args.file, args.splitter)
    entries = read_entries(args.entries)
    total = sum(counter.values())
    given = {k: counter.get(k, 0) for k in entries}
    onlyGiven = sum(given.values())
    print(f"Containing given entries: {onlyGiven},\n"
          f"Total entries: {total},\n"
          f"Proportion: {onlyGiven / total * 100:7.4f}%")
    top = 10
    i = 0
    for entry, freq in sorted(given.items(), key=lambda x: x[1], reverse=True):
        to_print = f"{entry}{args.splitter.pattern}{freq:8}{args.splitter.pattern}{freq / total * 100:7.4f}\n"
        if i < top:
            print(to_print, end="")
            i += 1
        args.save.write(to_print)
    pass


if __name__ == '__main__':
    wrapper()
