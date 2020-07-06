#!/usr/bin/env python3
"""
find all lines composed of printable ASCII,
you may re-define "valid_chr_re" to change the behaviour
"""
import argparse
import re
import sys
from typing import TextIO


def cleaning(dataset: TextIO, output: TextIO, valid_chr_re):
    if not (dataset.readable() and output.writable()):
        print(f"{dataset.name} show be readable and {output.name} should be writable", file=sys.stderr)
        sys.exit(-1)
    for line in dataset:
        line = line.strip("\r\n")
        if valid_chr_re.search(line):
            output.write(f"{line}\n")


def main():
    cli = argparse.ArgumentParser("Cleaning Password Dataset")
    cli.add_argument("-d", "--dataset", required=False, dest="dataset", type=argparse.FileType("r"),
                     default=sys.stdin, help="password dataset, one password per line")
    cli.add_argument("-o", "--output", required=False, dest="output", type=argparse.FileType("w"),
                     default=sys.stdout, help="save filtered password here")
    cli.add_argument("-p", "--regex", required=False, dest="valid_chr_re", type=lambda k: re.compile(k),
                     default=re.compile(r"^[a-zA-Z0-9\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]{4,255}$"))
    args = cli.parse_args()
    cleaning(args.dataset, args.output, args.valid_chr_re)
    pass


if __name__ == '__main__':
    main()
