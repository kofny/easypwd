#!/usr/bin/env python3
"""
find all lines which are unique
"""
import argparse
import sys
from random import shuffle
from typing import TextIO, Set


def uniq(fd: TextIO):
    if not fd.readable() or fd.closed:
        print(f"{fd.name} can not be used to read")
        sys.exit(-1)
    uniq_lines = set()
    for line in fd:
        line = line.strip("\r\n")
        uniq_lines.add(line)
    return uniq_lines


def save(uniq_lines: Set[str], save2: TextIO, order: str):
    if not save2.writable() or save2.closed:
        print(f"{save2.name} can not be used to write")
        sys.exit(-1)
    if order == 'order':
        uniq_lines = sorted(uniq_lines, reverse=False)
    elif order == 'reverse':
        uniq_lines = sorted(uniq_lines, reverse=True)
    elif order == 'random':
        uniq_lines = list(uniq_lines)
        shuffle(uniq_lines)
    else:
        sys.stderr.write(f"Unknown method: {order}")
        sys.exit(-1)

    for _l in uniq_lines:
        save2.write(f"{_l}\n")
    save2.flush()


def main():
    cli = argparse.ArgumentParser("Unique Lines of a File")
    cli.add_argument("-i", dest="input", required=False, type=argparse.FileType("r"), default=sys.stdin,
                     help="file to be parsed")
    cli.add_argument("-o", dest="output", required=False, type=argparse.FileType("w"), default=sys.stdout,
                     help="results to be saved")
    cli.add_argument("-s", "--sort", dest="order", default="order", type=str,
                     choices=["reverse", "random", "order"], help="the order of unique lines in output stream")
    try:
        args = cli.parse_args()
        uniq_lines = uniq(args.input)
        save(uniq_lines, save2=args.output, order=args.order)
        args.output.close()
    except KeyboardInterrupt:
        print(f"Canceled")
        sys.exit(-1)


if __name__ == '__main__':
    main()
