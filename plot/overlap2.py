"""
Overlap plus, overlap2 in short

Find how many cracked passwords overlap between two guessing methods, at all guess numbers
"""
import sys
from collections import defaultdict
from typing import TextIO, Dict

import matplotlib.pyplot as plt


def read_scored(fd_scored: TextIO, splitter: str):
    pwd_rank = defaultdict(int)
    for line in fd_scored:
        line = line.strip("\r\n")
        pwd, _, _, rank, _, _ = line.split(splitter)
        pwd_rank[pwd] = int(rank)
    return pwd_rank
    pass


def get_min(wanted: Dict[str, int], ranks_a: Dict[str, int], ranks_b: Dict[str, int]):
    min_ranks = {}
    n_ranks_a = {}
    n_ranks_b = {}
    for pwd in wanted:
        rank_a = ranks_a.get(pwd, sys.float_info.max)
        rank_b = ranks_b.get(pwd, sys.float_info.max)
        n_ranks_a[pwd] = rank_a
        n_ranks_b[pwd] = rank_b
        min_ranks[pwd] = min(rank_a, rank_b)

    return min_ranks, n_ranks_a, n_ranks_b


def wrapper(fd_wanted: TextIO, fd_scored_a: TextIO, splitter4a: str, fd_scored_b: TextIO, splitter4b: str, title: str,
            upper_bound: float):
    wanted = defaultdict(int)
    for line in fd_wanted:
        line = line.strip("\r\n")
        wanted[line] += 1
    ranks_a = read_scored(fd_scored_a, splitter4a)
    ranks_b = read_scored(fd_scored_b, splitter4b)
    only_a, overlap, only_b = "only_a", "overlap", "only_b"
    ranks = defaultdict(lambda: {only_a: set(), overlap: set(), only_b: set()})
    print("first")
    for pwd in wanted:
        rank_a = ranks_a.get(pwd, sys.float_info.max)
        rank_b = ranks_b.get(pwd, sys.float_info.max)
        if rank_a < rank_b:
            ranks[rank_a][only_a].add(pwd)
            ranks[rank_b][overlap].add(pwd)
        elif rank_a > rank_b:
            ranks[rank_b][only_b].add(pwd)
            ranks[rank_a][overlap].add(pwd)
        else:
            ranks[rank_a][overlap].add(pwd)
    ranks4num = defaultdict(lambda: {only_a: 0, overlap: 0, only_b: 0})
    print("second")
    acc_only_a, acc_overlap, acc_only_b = set(), set(), set()
    counter = 0
    total_ranks = len(ranks)
    bak = "\b" * 21
    acc_only_a_num, acc_overlap_num, acc_only_b_num = 0, 0, 0
    for rank, sets in sorted(ranks.items()):
        if rank > upper_bound:
            break
        counter += 1
        only_a_set, overlap_set, only_b_set = sets[only_a], sets[overlap], sets[only_b]
        acc_overlap |= overlap_set
        addon_overlap = sum([wanted[itm] for itm in overlap_set])
        acc_only_a |= only_a_set
        dup_only_a = dict()
        for itm in overlap_set:
            if itm in acc_only_a:
                dup_only_a[itm] = wanted[itm]
                acc_only_a.remove(itm)
        addon_a = sum([wanted[itm] for itm in only_a_set]) - sum(dup_only_a.values())
        acc_only_b |= only_b_set
        dup_only_b = dict()
        for itm in overlap_set:
            if itm in acc_only_b:
                dup_only_b[itm] = wanted[itm]
                acc_only_b.remove(itm)
        addon_b = sum([wanted[itm] for itm in only_b_set]) - sum(dup_only_b.values())
        acc_only_a_num += addon_a
        acc_only_b_num += addon_b
        acc_overlap_num += addon_overlap
        ranks4num[rank][only_a] = acc_only_a_num
        ranks4num[rank][overlap] = acc_overlap_num
        ranks4num[rank][only_b] = acc_only_b_num
        if counter % 10 == 0:
            print(f"{counter:10d}/{total_ranks:10d}{bak}", end="", file=sys.stderr)
        pass
    print("third")
    x, y_only_a, y_overlap, y_only_b = [], [], [], []
    for rank, nums in sorted(ranks4num.items()):
        only_a_num, overlap_num, only_b_num = nums[only_a], nums[overlap], nums[only_b]
        x.append(rank)
        y_only_a.append(only_a_num)
        y_overlap.append(overlap_num + only_a_num)
        y_only_b.append(only_b_num + only_a_num + overlap_num)
    fig = plt.figure()
    print("4th")

    fig.set_tight_layout(True)
    plt.plot(x, y_only_a, label="Only A")
    plt.plot(x, y_overlap, label="Overlap")
    plt.plot(x, y_only_b, label="Only B")
    plt.xscale('log')
    plt.legend()
    plt.savefig(title)
    plt.close(fig)

    pass


if __name__ == '__main__':
    for corpus in ['csdn', 'dodonew', "rockyou", "webhost", "xato"]:
        wrapper(open(f"/home/cw/Documents/Experiments/SegLab/Corpora/{corpus}-tar-only8plus.txt"),
                fd_scored_a=open(f"/home/cw/Documents/Experiments/SegLab/Simulated/Only8Plus/DRed/{corpus}.txt"),
                splitter4a="\t",
                fd_scored_b=open(f"/home/cw/Documents/Experiments/SegLab/Simulated/Only8Plus/Min/{corpus}-minus.txt"),
                splitter4b="\t", title=f"./overlap{corpus}.pdf", upper_bound=10 ** 24)
        pass
