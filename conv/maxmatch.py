"""
This is a py file used to split a given line based on maximum matching
"""
import argparse
import copy
import json
from typing import List, TextIO, Dict, Tuple, Set

from collections import defaultdict

import sys


def read_bpe_vocab(f_bpe_vocab: TextIO) -> Dict[str]:
    chunks = {}
    for line in f_bpe_vocab:
        line = line.strip("\r\n")
        chunk, _ = line.split(" ")
        chunks[chunk] = len(chunks) + 1
    f_bpe_vocab.close()
    return chunks


def read_cracked(f_cracked: TextIO, ranges: List[Tuple[int, int]]) -> Dict[Tuple[int, int], Dict[str, int]]:
    cracked = defaultdict(lambda: defaultdict(int))
    for line in f_cracked:
        line = line.strip("\r\n")
        pwd, _, count, guesses, _, _ = line.split("\t")
        guesses = int(guesses)
        count = int(count)
        for r in ranges:
            left, right = r
            if left <= guesses < right:
                cracked[r][pwd] = count
    return cracked


def maxmatch(given_string: str, vocab: Dict[str, int], stack: List[str], matched_length: int, target_length: int,
             wanted: List[str]):
    if matched_length == target_length:
        for item in stack:
            wanted.append(vocab[item])
        return
    if len(wanted) > 0:
        return
    for index in range(target_length, matched_length, -1):
        chunk = given_string[matched_length:index]
        if chunk in vocab:
            stack.append(chunk)
            maxmatch(given_string, vocab, stack, matched_length + len(chunk), target_length, wanted)
            stack.pop()
            if len(wanted) > 0:
                return
        pass
    pass


def avg_rank(cracked: Dict[Tuple[int, int], Dict[str, int]], vocab: Dict[str, int], end="\x03") \
        -> Dict[Tuple[int, int], float]:
    ranks = dict()
    for r, pwd_cnt in sorted(cracked.items(), key=lambda x: x[0][0]):
        total_sum = 0
        total_cnt = 0
        for pwd, cnt in pwd_cnt.items():
            wanted = []
            maxmatch(pwd + end, vocab, [], 0, len(pwd) + len(end), wanted)
            total_sum += sum(wanted)
            total_cnt += len(wanted)
        if total_cnt > 0:
            avg = total_sum / total_cnt
            ranks[r] = avg
    return ranks


def wrapper():
    cli = argparse.ArgumentParser("Max Match based on BPE vocab")
    cli.add_argument("--vocab", dest="vocab", type=argparse.FileType('r'), required=True, help="BPE vocab filename")
    cli.add_argument("--cracked", dest="cracked", type=argparse.FileType('r'), required=True,
                     help="cracked passwords with count and guess number")
    cli.add_argument("--ranges", dest="ranges", type=int, required=False,
                     default=[1, 100, 10000, 10 ** 6, 10 ** 8, 10 ** 10, 10 ** 12, 10 ** 14], nargs="+")
    cli.add_argument("--save", dest="save", type=argparse.FileType('w'), default=sys.stdout, required=False,
                     help="save results in the specified filename")
    args = cli.parse_args()
    ranges = []
    for i in range(len(args.ranges) - 1):
        ranges.append((args.ranges[i], args.ranges[i + 1]))
    vocab = read_bpe_vocab(args.vocab)
    cracked = read_cracked(args.cracked, ranges)
    ranks = avg_rank(cracked, vocab)
    args.save.write(json.dumps(ranks))
    args.save.flush()
    args.save.close()
    pass


if __name__ == '__main__':
    wrapper()
