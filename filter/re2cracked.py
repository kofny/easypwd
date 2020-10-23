#!/usr/bin/env python3
"""
We have a file of cracked passwords and corresponding probabilities, guess numbers and frequencies,
now we want to remove some passwords using this script.
"""
import argparse
import sys
from collections import defaultdict
from typing import List, Tuple, Dict, TextIO


def lets_rm(cracked_list: List[Tuple[str, float, int, int, int, float]], wanted: Dict[str, int]):
    res = []
    cur_cracked = 0
    total = sum(wanted.values())
    for pwd, mlp, cnt, guesses, cracked, percent in cracked_list:
        if pwd in wanted:
            cur_cracked += cnt
            res.append([pwd, mlp, cnt, guesses, cur_cracked, cur_cracked / total * 100])
    return res


def read_cracked(fd_cracked: TextIO):
    cracked_list: List[Tuple[str, float, int, int, int, float]] = []
    for line in fd_cracked:
        line = line.strip('\r\n')
        pwd, mlp, cnt, guesses, cracked, percent = line.split("\t")
        mlp, guesses = float(mlp), int(guesses)
        if mlp >= 1022.0:
            guesses = sys.float_info.max
        cracked_list.append((pwd, mlp, int(cnt), guesses, int(cracked), float(percent)))
    fd_cracked.close()
    return cracked_list

    pass


def main():
    cli = argparse.ArgumentParser("Remove unwanted cracked passwords")
    cli.add_argument("-c", "--cracked", dest="cracked", required=True, type=argparse.FileType('r'),
                     help="formatted cracked file")
    cli.add_argument("-o", "--output", dest="output", required=True, type=argparse.FileType('w'),
                     help="save results here")
    cli.add_argument("-w", "--wanted", dest="wanted", required=True, type=argparse.FileType('r'),
                     help="passwords in this file will be kept.")
    args = cli.parse_args()
    cracked_list = read_cracked(args.cracked)
    wanted = defaultdict(int)
    for line in args.wanted:
        line = line.strip("\r\n")
        wanted[line] += 1
    args.wanted.close()
    results = lets_rm(cracked_list, wanted)
    for pwd, mlp, cnt, guesses, cracked, percent in results:
        args.output.write(f"{pwd}\t{mlp}\t{cnt}\t{guesses}\t{cracked}\t{percent}\n")
    args.output.flush()
    args.output.close()
    pass


if __name__ == '__main__':
    main()
