#!/usr/bin/env python3
"""
find all lines composed of printable ASCII,
you may re-define "valid_chr_re" to change the behaviour
"""
import argparse
import re
import sys
from typing import TextIO


def cleaning(dataset: str, encoding: str, output: TextIO, valid_chr_re):
    fd_dataset = open(dataset, encoding=encoding)
    if not (fd_dataset.readable() and output.writable()):
        print(f"{dataset} show be readable and {output.name} should be writable", file=sys.stderr)
        sys.exit(-1)
    line = ""
    try:
        for _line in fd_dataset:
            line = _line.strip("\r\n")
            if valid_chr_re.search(line):
                output.write(f"{line}\n")
    except UnicodeDecodeError as e:
        print(f"{line}| {e.reason}", file=sys.stderr)
        sys.exit(-1)


def main():
    cli = argparse.ArgumentParser("Cleaning Password Dataset")
    cli.add_argument("-d", "--dataset", required=True, dest="dataset", type=str,
                     help="password dataset, one password per line")
    cli.add_argument("-e", '--encoding', required=False, dest="encoding", type=str, choices=['utf-8', 'latin-1'],
                     default='utf-8', help='set the encoding of dataset')
    cli.add_argument("-o", "--output", required=False, dest="output", type=argparse.FileType("w"),
                     default=sys.stdout, help="save filtered password here")
    cli.add_argument("-p", "--regex", required=False, dest="valid_chr_re",
                     type=lambda k: re.compile(k),
                     default=re.compile(r"^[a-zA-Z0-9\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]{4,255}$"))
    args = cli.parse_args()
    cleaning(args.dataset, args.encoding, args.output, args.valid_chr_re)
    pass


if __name__ == '__main__':
    main()
