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
from typing import TextIO


def split2(corpus: TextIO, training_corpus: TextIO, testing_corpus: TextIO,
           training_ratio: int, testing_ratio: int, len_min: int = 4, len_max: int = 40):
    if not training_corpus.writable() or not testing_corpus.writable():
        print("Training and Testing SHOULD be Writable!", file=sys.stderr)
        sys.exit(-1)
    batch = training_ratio + testing_ratio
    training_per_batch = training_ratio
    pwd_set = []
    count_invalid = defaultdict(int)
    valid_chr = re.compile(r"^[a-zA-Z0-9\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]+$")
    for line in corpus:
        line = line.strip("\r\n")
        if valid_chr.match(line) is None:
            count_invalid[line] += 1
            continue
        if len_min <= len(line) <= len_max:
            pwd_set.append(line)
    shuffle(pwd_set)

    counter = 0
    for line in pwd_set:
        counter += 1
        if counter > batch:
            counter = 1
        if counter <= training_per_batch:
            training_corpus.write(f"{line}\n")
        else:
            testing_corpus.write(f"{line}\n")
    training_corpus.flush()
    testing_corpus.flush()
    training_corpus.close()
    testing_corpus.close()
    if len(count_invalid) != 0:
        removed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
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
                     help='the ratio of training set, an integer, training takes a / (a + b)')
    cli.add_argument('-b', '--ratio4test', dest='ratio4test', required=False, type=int, default=1,
                     help='the ratio of testing set, an integer, testing takes b / (a + b)')
    cli.add_argument('-l', '--low', dest='len_min', required=False, type=int, default=4,
                     help='length less than this will be ignored')
    cli.add_argument('-u', '--high', dest='len_max', required=False, type=int, default=255,
                     help="length larger than this will be ignored")
    args = cli.parse_args()
    if args.ratio4train < 1 or args.ratio4test < 1 or args.len_max < args.len_min:
        sys.exit(-1)
        pass
    split2(args.corpus, args.training, args.testing, args.ratio4train, args.ratio4test, len_max=args.len_max,
           len_min=args.len_min)

    pass


if __name__ == '__main__':
    main()
    pass
