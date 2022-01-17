#!/usr/bin/env python3
"""
Dictionary Attack
"""
import argparse
import sys
from collections import defaultdict


def intersect(dictionary: str, corpus: str):
    d = set()
    with open(dictionary, 'r') as fin:
        for line in fin:
            line = line.strip('\r\n')
            d.add(line)
    wanted = defaultdict(int)
    total = 0
    with open(corpus, 'r') as fin:
        for line in fin:
            line = line.strip('\r\n')
            total += 1
            if line in d:
                wanted[line] += 1
    return wanted, total


def wrapper():
    cli = argparse.ArgumentParser('Dictionary Attack')
    cli.add_argument('dict', type=str, help='Dictionary')
    cli.add_argument("target", type=str, help='Password dataset to be cracked')
    args = cli.parse_args()
    wanted, total = intersect(args.dict, args.target)
    cnt = sum(wanted.values())
    print(f"Dictionary cracked {cnt} passwords, the percentage is {cnt / total * 100:5.2f}", file=sys.stderr,
          flush=True)
    pass


if __name__ == '__main__':
    wrapper()
