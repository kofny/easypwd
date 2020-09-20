#!/usr/bin/env python3
"""
Get Distribution of Length, Characters
"""
import argparse
import json
import sys
from collections import defaultdict
from typing import TextIO, Dict


def len_dist(dataset: TextIO, close_fd: bool = False) -> (int, Dict[int, int]):
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
    if close_fd:
        dataset.close()
    return total, len_dict


def chr_dist(dataset: TextIO, close_fd: bool = False) -> (int, Dict[str, int], Dict[str, int]):
    """

    :param close_fd:
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
        line = line.strip("\r\n")
        for c in line:
            if c.isalpha():
                if c.isupper():
                    cls_dict["upper"] += 1
                else:
                    cls_dict['lower'] += 1
            elif c.isdigit():
                cls_dict["digit"] += 1
            else:
                cls_dict["other"] += 1
            chr_dict[c] += 1
    if close_fd:
        dataset.close()
    total_chr = sum(chr_dict.values())
    return total_chr, chr_dict, cls_dict


def wrapper(dataset: TextIO, save: TextIO):
    if not dataset.seekable():
        raise Exception("Not seekable, do not use stdin please")
    if not save.writable():
        raise Exception(f"{save.name} Not writable")
    total_size, len_dict = len_dist(dataset, False)
    dataset.seek(0)
    total_chr, chr_dict, cls_dict = chr_dist(dataset, True)
    json.dump({
        "#len": total_size,
        "len": len_dict,
        "#chr": total_chr,
        "chr": chr_dict,
        "cls": cls_dict
    }, save, indent=2)
    save.close()


def main():
    cli = argparse.ArgumentParser("Count the distribution of Length and Characters")
    cli.add_argument("-d", "--dataset", dest="dataset", required=True, type=argparse.FileType("r"),
                     help="dataset to be analysed")
    cli.add_argument("-s", "--save", dest="save", required=True, type=argparse.FileType("w"),
                     help="save result here")
    args = cli.parse_args()
    wrapper(args.dataset, args.save)


if __name__ == '__main__':
    main()
    pass
