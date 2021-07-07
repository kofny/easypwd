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
        items = line.split("\t")
        pwd = items[0]
        cnt = int(items[1])
        total += cnt
        len_line = len(pwd)
        len_dict[len_line] += cnt
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
        print(f"unable to read {dataset.name}", file=sys.stderr)
        sys.exit(-1)
    dataset.seek(0)
    chr_dict = defaultdict(int)
    cls_dict = defaultdict(int)
    cls_number_dict = defaultdict(int)
    for line in dataset:
        line = line.strip("\r\n")
        items = line.split("\t")
        pwd = items[0]
        cnt = int(items[1])
        cls_lst = {"upper": 0, "lower": 0, "digit": 0, "other": 0}
        for c in pwd:
            if c.isalpha():
                if c.isupper():
                    cls_lst['upper'] += cnt
                    # cls_dict["upper"] += 1
                else:
                    cls_lst['lower'] += cnt
            elif c.isdigit():
                cls_lst["digit"] += cnt
            else:
                cls_lst["other"] += cnt
            for k, v in cls_lst.items():
                cls_dict[k] += v
            chr_dict[c] += cnt

        cls_number = sum([1 if c > 0 else 0 for c in cls_lst.values()])
        cls_number_dict[cls_number] += cnt
    if close_fd:
        dataset.close()
    total_chr = sum(chr_dict.values())
    return total_chr, chr_dict, cls_dict, cls_number_dict


def wrapper(dataset: TextIO, save: TextIO):
    if not dataset.seekable():
        raise Exception("Not seekable, do not use stdin please")
    if not save.writable():
        raise Exception(f"{save.name} Not writable")
    total_size, len_dict = len_dist(dataset, False)
    dataset.seek(0)
    total_chr, chr_dict, cls_dict, cls_number_dict = chr_dist(dataset, True)
    avg_len = sum([k * v for k, v in len_dict.items()]) / total_size
    avg_n_cls = sum([k * v for k, v in cls_number_dict.items()]) / total_size
    json.dump({
        "#len": total_size,
        "len": len_dict,
        "avg_len": avg_len,
        "#chr": total_chr,
        "chr": chr_dict,
        "cls": cls_dict,
        "#cls": cls_number_dict,
        "avg_#cls": avg_n_cls
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
