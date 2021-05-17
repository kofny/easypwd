#!/usr/bin/env python3
"""
The output file of hashcat is hard to read to some extend.
THis file will convert the output of (plain, crack_pos) to (pwd, num, #guesses, #cracked, %cracked)
"""
import argparse
import sys
from collections import defaultdict
from typing import TextIO, Dict, Generator, Tuple, Any, List


def read_hc_res(hc_res: TextIO,
                wanted_indices: List[int], guess_number_idx: int) -> Dict[str, int]:
    wanted_pos = {}
    for line in hc_res:
        line = line.strip("\r\n")
        items = line.split(":")
        _wanted = ":".join([items[i] for i in wanted_indices])
        _guess_number = items[guess_number_idx]
        wanted_pos[_wanted] = int(_guess_number)
    return wanted_pos


def read_target_set(f_target: TextIO) -> Dict[str, int]:
    targets = defaultdict(int)
    for line in f_target:
        line = line.strip("\r\n")
        try:
            t, cnt = line.split("\t")
            cnt = int(cnt)
        except Exception:
            t, cnt = line, 1
        targets[t] += cnt
    f_target.close()
    return targets


def hcgood(wanted_pos: Dict[str, int], target_cnt: Dict[str, int]):
    total = sum(target_cnt.values())
    hash_cnt_pos_list = []
    for _target, cnt in target_cnt.items():
        crack_pos = wanted_pos.get(_target, sys.float_info.max)
        hash_cnt_pos_list.append((_target, cnt, crack_pos))
    del target_cnt
    del wanted_pos
    hash_cnt_pos_list = sorted(hash_cnt_pos_list, key=lambda x: x[2], reverse=False)
    cracked = 0
    for _target, cnt, crack_pos in hash_cnt_pos_list:
        cracked += cnt
        yield _target, .0, cnt, crack_pos, cracked, cracked / total * 100


def save(data: Generator[Tuple[str, float, int, int, int, float], Any, None], fd: TextIO, close_fd: bool = True):
    for pwd, prob, cnt, rank, cracked, cracked_rate in data:
        fd.write(f"{pwd}\t{prob}\t{cnt}\t{rank}\t{cracked}\t{cracked_rate:5.2f}\n")
    fd.flush()
    if close_fd:
        fd.close()


def wrapper(hc_res: TextIO, f_target: TextIO, save2: TextIO, wanted_indices: List[int], guess_number_idx: int):
    wanted_pos = read_hc_res(hc_res, wanted_indices=wanted_indices, guess_number_idx=guess_number_idx)
    hc_res.close()
    target_cnt = read_target_set(f_target)
    f_target.close()
    hcg = hcgood(wanted_pos, target_cnt)
    save(hcg, save2, close_fd=True)


def main():
    cli = argparse.ArgumentParser("Convert Result of hashcat to Easy-to-read Format")
    cli.add_argument("-i", "--input", dest="res", required=True, type=argparse.FileType("r"),
                     help="hashcat result file, format should be (plain:crack_pos)")
    cli.add_argument("-t", "--target", dest="target", required=True, type=argparse.FileType("r"),
                     help="hashes file")
    cli.add_argument("-s", "--save", dest="save", required=True, type=argparse.FileType("w"),
                     help="save results to this file")
    cli.add_argument("--key-indices", dest="wanted_indices", type=int, nargs='+', help="wanted indices", default=[0])
    cli.add_argument("--guesses-index", dest="guesses_index", type=int, help="wanted index", default=-1)
    args = cli.parse_args()
    hc_res, targets, save2 = args.res, args.target, args.save
    wanted_indices, guess_number_idx = args.wanted_indices, args.guesses_index
    wrapper(hc_res=hc_res, f_target=targets, save2=save2, wanted_indices=wanted_indices,
            guess_number_idx=guess_number_idx)


if __name__ == '__main__':
    main()
