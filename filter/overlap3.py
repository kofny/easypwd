"""
Overlap plus plus, overlap3 in short

Find how many cracked passwords overlap between two guessing methods, at all guess numbers
"""
from collections import defaultdict
from typing import TextIO


def read_scored(fd_scored: TextIO, splitter: str):
    pwd_rank = defaultdict(int)
    for line in fd_scored:
        line = line.strip("\r\n")
        pwd, _, _, rank, _, _ = line.split(splitter)
        pwd_rank[pwd] = int(rank)
    pass
