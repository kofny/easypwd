"""
Get Distribution of Length, Characters
"""
import argparse
import json
import sys
from collections import defaultdict
from typing import TextIO, Dict


def len_dist(dataset: TextIO) -> (int, Dict[int, int]):
    if not dataset.readable():
        print(f"unble to read {dataset.name}", file=sys.stderr)
        sys.exit(-1)
    dataset.seek(0)
    total = 0
    len_dict = defaultdict(int)
    for line in dataset:
        line = line.strip("\r\n")
        total += 1
        len_line = len(line)
        len_dict[len_line] += 1
    return total, len_dict


def chr_dist(dataset: TextIO) -> (int, Dict[str, int], Dict[str, int]):
    """

    :param dataset:
    :return: total, chr_dict, cls_dict
    """
    if not dataset.readable():
        print(f"unble to read {dataset.name}", file=sys.stderr)
        sys.exit(-1)
    dataset.seek(0)
    chr_dict = defaultdict(int)
    cls_dict = defaultdict(int)
    for line in dataset:
        for c in line:
            if c.isalpha():
                cls_dict["alpha"] += 1
            elif c.isdigit():
                cls_dict["digit"] += 1
            else:
                cls_dict["other"] += 1
            chr_dict[c] += 1
    total_chr = sum(chr_dict.values())
    return total_chr, chr_dict, cls_dict


def main():
    cli = argparse.ArgumentParser("Count the distribution of Length and Characters")
    cli.add_argument()
    pass


if __name__ == '__main__':
    pass
