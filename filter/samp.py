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
from typing import TextIO, List


def samp(corpus: TextIO, samp_corpora: List[TextIO],
         samp_size: int, fd_removed: TextIO, valid_pwd: Pattern):
    for samp_corpus in samp_corpora:
        if not samp_corpus.writable():
            print("Training and Testing SHOULD be Writable!", file=sys.stderr)
            sys.exit(-1)
    if len(samp_corpora) < 1:
        print("At least one sample file!", file=sys.stderr)
        sys.exit(-1)
    pwd_set = []
    count_invalid = defaultdict(int)
    for line in corpus:
        line = line.strip("\r\n")
        if valid_pwd.match(line) is None:
            count_invalid[line] += 1
            continue
        pwd_set.append(line)
    samp_size = min(len(pwd_set), samp_size)
    for idx, samp_corpus in enumerate(samp_corpora):
        shuffle(pwd_set)
        for line in pwd_set[:samp_size]:
            samp_corpus.write(f"{line}\n")
        samp_corpus.flush()
        print(f"{idx + 1} sample file saved here: {samp_corpus.name}", file=sys.stderr)
        samp_corpus.close()

    if len(count_invalid) != 0 and fd_removed is not None:

        print(f"Removed invalid passwords saved in {fd_removed.name}", file=sys.stderr)
        for p, n in sorted(count_invalid.items(), key=lambda x: x[1], reverse=True):
            fd_removed.write(f"{p}\t{n}\n")
        fd_removed.close()
    print("Done!", file=sys.stderr)


def wrapper():
    cli = argparse.ArgumentParser('Sample some passwords from dataset')
    cli.add_argument('-c', '--corpus', dest='corpus', required=True, type=argparse.FileType('r'),
                     help='corpus to be split')
    cli.add_argument('-s', '--sample-files', dest='samp_files', required=True, nargs='+', type=argparse.FileType("w"),
                     help="sampled files will be saved here")
    cli.add_argument('-n', '--samp-size', dest='samp_size', required=True, type=int,
                     help='How many passwords should this script sample')
    cli.add_argument('-r', '--regex-valid', dest='valid_pwd', required=False, type=str,
                     default=r"^[a-zA-Z0-9\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]{4,255}$",
                     help="what is a valid password")
    cli.add_argument("--removed", dest="fd_removed", required=False, type=str, default="no",
                     help="valid passwords will display here, "
                          "no for ignoring, - for default save path, or existing path")
    args = cli.parse_args()
    if args.samp_size < 1:
        sys.exit(-1)
    if args.fd_removed == 'no':
        fd_removed = None
    elif args.fd_removed == '-':
        fd_removed = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       f"{os.path.basename(args.corpus.name)}.invalid"), "w")
    else:
        if os.path.exists(args.fd_removed):
            make_sure = input(f"{args.fd_removed} exists, remove? [Y/N]")
            if make_sure != 'y' and make_sure != 'Y':
                sys.exit(0)
        fd_removed = open(args.fd_removed, 'w')
    regex_valid = args.valid_pwd.replace('\\\\', '\\')
    print(f"Using RegEx: {regex_valid}", file=sys.stderr)
    valid_pwd = re.compile(regex_valid)
    samp(args.corpus, args.samp_files, samp_size=args.samp_size,
         valid_pwd=valid_pwd, fd_removed=fd_removed)
    pass


if __name__ == '__main__':
    wrapper()
