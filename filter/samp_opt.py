#!/usr/bin/env python3
"""
optimised sampling process
"""
import argparse
import random
import sys
from typing import TextIO
from functools import partial


def partial_count(file_name, ends_with: str):
    buffer = 1024 * 1024
    print(f"Counting the number of lines...", file=sys.stderr, end='')
    with open(file_name) as f:
        return sum(x.count(ends_with) for x in iter(partial(f.read, buffer), ''))


def samp(corpus: str, samp_corpora: TextIO, samp_size: int, corpus_size: int, ends_with: str):
    pwd_set = []
    if corpus_size < 0:
        corpus_size = partial_count(corpus, ends_with)
    print(f"{corpus_size:,} lines", file=sys.stderr)
    target_size = min(corpus_size, samp_size)
    choices = set()
    for i in range(target_size):
        choices.add(random.randint(i, corpus_size))
        if i % 262144 == 0:
            print(f"{i / corpus_size * 100:6.4}%", end='\r', file=sys.stderr)
    print(f"100.00% Sampled!", file=sys.stderr)
    with open(corpus, 'r') as f_corpus:
        idx = 0
        for line in f_corpus:
            line = line.strip("\r\n")
            if idx in choices:
                pwd_set.append(line)
            idx += 1
            if idx % 262144 == 0:
                print(f"{idx / corpus_size * 100:6.4}%", end='\r', file=sys.stderr)
        pass

    for line in pwd_set:
        samp_corpora.write(f"{line}\n")
    samp_corpora.flush()
    samp_corpora.close()
    print("100.00% Done!   ", file=sys.stderr)


def wrapper():
    cli = argparse.ArgumentParser('Sample some passwords from dataset')
    cli.add_argument('-c', '--corpus', dest='corpus', required=True, type=str,
                     help='corpus to be split')
    cli.add_argument('--corpus-size', dest='corpus_size', required=False, default=-1, type=int,
                     help='specify the size of the corpus to save time')
    cli.add_argument('-s', '--sample-file', dest='samp_file', required=True, type=argparse.FileType("w"),
                     help="sampled file will be saved here")
    cli.add_argument('-n', '--samp-size', dest='samp_size', required=True, type=int,
                     help='How many passwords should this script sample')
    cli.add_argument('--ends-with', dest='ends_with', required=False, default='n', choices=['n', 'r', 'rn'],
                     help='A line ends with \\n, \\r, or \\r\\n')
    args = cli.parse_args()
    ends_with = {'n': '\n', 'r': '\r', "rn": "\r\n"}[args.ends_with]
    samp(args.corpus, args.samp_file, samp_size=args.samp_size,
         corpus_size=args.corpus_size, ends_with=ends_with)
    pass


if __name__ == '__main__':
    wrapper()
