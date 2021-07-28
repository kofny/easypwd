#!/usr/bin/env python3
"""
Count the discrete degree of the password dataset
"""
import argparse
from collections import defaultdict

from typing import TextIO

import math


def discrete(dataset: TextIO):
    d = defaultdict(int)
    u = set()
    for line in dataset:
        line = line.strip('\r\n')
        d[len(line)] += 1
        u.add(line)
    uniq = len(u)
    del u
    total = sum(d.values())
    avg = sum([k * v for k, v in d.items()]) / total
    sqr_diff = sum([(k - avg) ** 2 * v for k, v in d.items()]) / (total - 1)
    std_diff = math.sqrt(sqr_diff)
    dis = std_diff / avg
    return dis, uniq
    pass


def wrapper():
    cli = argparse.ArgumentParser("Count discrete degree of each password dataset")
    cli.add_argument("files", nargs="+", type=argparse.FileType('r'), help="Files to be parsed")
    args = cli.parse_args()
    for dataset in args.files:
        dis, uniq = discrete(dataset=dataset)
        print(f"File: {dataset.name}\n"
              f"\tDiscrete Degree: {dis:8.4f}, Unique entries: {uniq}")
        dataset.close()
    pass


if __name__ == '__main__':
    wrapper()
