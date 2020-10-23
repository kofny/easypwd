#!/usr/bin/env python3
"""
The minimal rank among several models
"""
import argparse
import sys
from typing import TextIO, Dict, Generator, List


def init_targets(targets: TextIO):
    pwd_rank = {}
    for line in targets:
        line = line.strip("\r\n")
        num, _ = pwd_rank.get(line, (0, 0))
        pwd_rank[line] = (num + 1, sys.maxsize)
    return pwd_rank


def read_scored(scored: TextIO, splitter: str):
    for line in scored:
        line = line.strip("\r\n")
        pwd, _, _, rank, _, _ = line.split(splitter)
        yield pwd, int(rank)


def parse_rank(pwd_rank: Dict, model_rank: Generator):
    for pwd, rank in model_rank:
        num, origin_rank = pwd_rank[pwd]
        if rank < origin_rank:
            pwd_rank[pwd] = (num, rank)


def wrapper(targets: TextIO, scored_files: List[TextIO], splitter: str, save2: TextIO):
    if not save2.writable():
        print(f"{save2.name} is not writable", file=sys.stderr)
        sys.exit(-1)
    pwd_rank = init_targets(targets)
    total = sum([n for n, _ in pwd_rank.values()])
    for scored in scored_files:
        rs = read_scored(scored, splitter)
        parse_rank(pwd_rank, model_rank=rs)
        scored.close()
    prev_rank = 0
    cracked = 0
    for pwd, (num, rank) in sorted(pwd_rank.items(), key=lambda x: x[1][1], reverse=False):
        cracked += num
        rank = round(max(rank, prev_rank + 1))
        save2.write(f"{pwd}\t{0.0}\t{num}\t{rank}\t{cracked}\t{cracked / total * 100:5.2f}\n")
        pass
    save2.flush()
    save2.close()


def main():
    cli = argparse.ArgumentParser("MinRank of Several Models")
    cli.add_argument("-t", "--target", dest="target", type=argparse.FileType("r"), required=True,
                     help="target set")
    cli.add_argument("-m", "--models", dest="models", type=argparse.FileType("r"), required=True,
                     nargs="+", help="scored target files of 1 or more models")
    cli.add_argument("--split", dest="split", type=str, required=False, default="\t",
                     help="how to split a line in scored target of models")
    cli.add_argument("-s", "--save", type=argparse.FileType('w'), required=True,
                     help="save min_rank here")
    args = cli.parse_args()
    wrapper(targets=args.target, scored_files=args.models, splitter=args.split, save2=args.save)


if __name__ == '__main__':
    main()
