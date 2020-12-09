#!/usr/bin/env python3
"""
Split dataset to training and testing set
"""
import argparse
import os
import re
import sys
from collections import defaultdict
from random import shuffle
from re import Pattern
from typing import TextIO


def split2(corpus: TextIO, training_corpus: TextIO, testing_corpus: TextIO,
           training_ratio: int, testing_ratio: int, discard_ratio: int, regex_valid: Pattern):
    if not training_corpus.writable() or not testing_corpus.writable():
        print("Training and Testing SHOULD be Writable!", file=sys.stderr)
        sys.exit(-1)
    batch = training_ratio + testing_ratio + discard_ratio
    training_per_batch = training_ratio
    testing_per_batch = training_ratio + testing_ratio
    pwd_set = []
    count_invalid = defaultdict(int)
    for line in corpus:
        line = line.strip("\r\n")
        if regex_valid.match(line) is None:
            count_invalid[line] += 1
            continue
        pwd_set.append(line)
    shuffle(pwd_set)

    counter = 0
    for line in pwd_set:
        counter += 1
        if counter > batch:
            counter = 1
        if counter <= training_per_batch:
            training_corpus.write(f"{line}\n")
        elif counter <= testing_per_batch:
            testing_corpus.write(f"{line}\n")
    training_corpus.flush()
    testing_corpus.flush()
    training_corpus.close()
    testing_corpus.close()
    if len(count_invalid) != 0:
        removed = open(os.path.join(os.path.dirname(os.path.abspath(corpus.name)),
                                    f"{os.path.basename(corpus.name)}.invalid"), "w")
        print(f"Removed invalid passwords saved in {removed.name}")
        for p, n in sorted(count_invalid.items(), key=lambda x: x[1], reverse=True):
            removed.write(f"{p}\t{n}\n")
        removed.close()
    print("Done!")


def main():
    cli = argparse.ArgumentParser('Split corpus to training and testing')
    cli.add_argument('-c', '--corpus', dest='corpus', required=True, type=argparse.FileType('r'),
                     help='corpus to be split')
    cli.add_argument('-s', '--training', dest='training', required=True, type=argparse.FileType("w"),
                     help="training set will be saved here, source")
    cli.add_argument('-t', '--testing', dest='testing', required=True, type=argparse.FileType('w'),
                     help='testing set will be saved here, target')
    cli.add_argument('-a', '--ratio4train', dest='ratio4train', required=False, type=int, default=3,
                     help='the ratio of training set, an integer, training takes a / (a + b + d)')
    cli.add_argument('-b', '--ratio4test', dest='ratio4test', required=False, type=int, default=1,
                     help='the ratio of testing set, an integer, testing takes b / (a + b + d)')
    cli.add_argument("-d", '--discard', dest='ratio4discard', required=False, type=int, default=0,
                     help="ignore this part of passwords, d / (a + b + d)")
    cli.add_argument("-p", "--regex", required=False, dest="valid_chr_re",
                     type=lambda k: re.compile(k.replace("\\\\", "\\")),
                     default=re.compile(r"^[a-zA-Z0-9\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]{4,255}$"),
                     help="passwords matched by this regex will be kept and used to split")
    args = cli.parse_args()
    args.ratio4discard = max(0, args.ratio4discard)
    if args.ratio4train < 1 or args.ratio4test < 1:
        sys.stderr.write(f"Check ratio!\n")
        sys.exit(-1)
    split2(args.corpus, args.training, args.testing, args.ratio4train, args.ratio4test, args.ratio4discard,
           regex_valid=args.valid_chr_re)

    pass


if __name__ == '__main__':
    main()
    pass
