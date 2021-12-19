#!/usr/bin/env python3
"""
optimised sampling process
"""
import argparse
import random
import sys
from typing import TextIO
from functools import partial


def partial_count(file_name):
    buffer = 1024 * 1024
    with open(file_name) as f:
        return sum(x.count('\n') for x in iter(partial(f.read, buffer), ''))


def samp(corpus: str, samp_corpora: TextIO,
         samp_size: int, corpus_size: int):
    pwd_set = []
    if corpus_size < 0:
        corpus_size = partial_count(corpus)
    choices = set(random.sample(range(0, corpus_size), min(corpus_size, samp_size)))
    with open(corpus, 'r') as f_corpus:
        idx = 0
        for line in f_corpus:
            line = line.strip("\r\n")
            if idx in choices:
                pwd_set.append(line)
            idx += 1
        pass

    for line in pwd_set[:samp_size]:
        samp_corpora.write(f"{line}\n")
    samp_corpora.flush()
    samp_corpora.close()
    print("Done!", file=sys.stderr)


def wrapper():
    cli = argparse.ArgumentParser('Sample some passwords from dataset')
    cli.add_argument('-c', '--corpus', dest='corpus', required=True, type=str,
                     help='corpus to be split')
    cli.add_argument('--corpus-size', dest='corpus_size', required=False, default=-1,
                     help='specify the size of the corpus to save time')
    cli.add_argument('-s', '--sample-file', dest='samp_file', required=True, type=argparse.FileType("w"),
                     help="sampled file will be saved here")
    cli.add_argument('-n', '--samp-size', dest='samp_size', required=True, type=int,
                     help='How many passwords should this script sample')
    args = cli.parse_args()
    samp(args.corpus, args.samp_file, samp_size=args.samp_size,
         corpus_size=args.corpus_size)
    pass


if __name__ == '__main__':
    wrapper()
