#!/usr/bin/env python3
"""
optimised sampling process
Obtain the expectation
"""
import argparse
import random
import sys
from typing import TextIO


def samp(corpus: str, samp_corpora: TextIO, rate: float):
    pwd_set = []
    with open(corpus, 'r') as f_corpus:
        idx = 0
        for line in f_corpus:
            line = line.strip("\r\n")
            v = random.random()
            if v < rate:
                pwd_set.append(line)
            idx += 1
            if idx % 262144 == 0:
                print(f"{idx:10}", end='\r', file=sys.stderr)
        pass
    for line in pwd_set:
        samp_corpora.write(f"{line}\n")
    samp_corpora.flush()
    samp_corpora.close()


def wrapper():
    cli = argparse.ArgumentParser('Sample some passwords from dataset')
    cli.add_argument('-c', '--corpus', dest='corpus', required=True, type=str,
                     help='corpus to be split')
    cli.add_argument('-s', '--sample-file', dest='samp_file', required=True, type=argparse.FileType("w"),
                     help="sampled file will be saved here")
    cli.add_argument('--rate', dest='rate', required=True, type=float,
                     help='A password will be sampled with probability `rate`')
    args = cli.parse_args()
    samp(args.corpus, args.samp_file, rate=args.rate)
    pass


if __name__ == '__main__':
    wrapper()
