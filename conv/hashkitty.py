#!/usr/bin/env python3
"""
The output file of hashcat is hard to read to some extend.
THis file will convert the output of (plain, crack_pos) to (pwd, num, #guesses, #cracked, %cracked)
"""
import argparse
import sys
from collections import defaultdict
from typing import TextIO, Dict, Generator, Tuple, Any


def read_hc_res(hc_res: TextIO) -> Dict[str, int]:
    pwd_pos = {}
    for line in hc_res:
        line = line.strip("\r\n")
        k = line.rfind(":")
        plain_pwd, crack_pos = line[:k], line[k + 1:]
        pwd_pos[plain_pwd] = int(crack_pos)
    return pwd_pos


def read_target_set(targets: TextIO) -> Dict[str, int]:
    pwd_cnt = defaultdict(int)
    for line in targets:
        pwd = line.strip("\r\n")
        pwd_cnt[pwd] += 1
    return pwd_cnt


def hcgood(pwd_pos: Dict[str, int], pwd_cnt: Dict[str, int]):
    total = sum(pwd_cnt.values())
    pwd_cnt_pos_list = []
    for pwd, cnt in pwd_cnt.items():
        crack_pos = pwd_pos.get(pwd, sys.float_info.max)
        pwd_cnt_pos_list.append((pwd, cnt, crack_pos))
    del pwd_cnt
    del pwd_pos
    pwd_cnt_pos_list = sorted(pwd_cnt_pos_list, key=lambda x: x[2], reverse=False)
    cracked = 0
    for pwd, cnt, crack_pos in pwd_cnt_pos_list:
        cracked += cnt
        yield pwd, .0, cnt, crack_pos, cracked, cracked / total * 100


def save(data: Generator[Tuple[str, float, int, int, int, float], Any, None], fd: TextIO, close_fd: bool = True):
    for pwd, prob, cnt, rank, cracked, cracked_rate in data:
        fd.write(f"{pwd}\t{prob}\t{cnt}\t{rank}\t{cracked}\t{cracked_rate:5.2f}\n")
    fd.flush()
    if close_fd:
        fd.close()


def wrapper(hc_res: TextIO, targets: TextIO, save2: TextIO):
    pwd_pos = read_hc_res(hc_res)
    hc_res.close()
    pwd_cnt = read_target_set(targets)
    targets.close()
    hcg = hcgood(pwd_pos, pwd_cnt)
    save(hcg, save2, close_fd=True)


def main():
    cli = argparse.ArgumentParser("Convert Result of hashcat to Easy-to-read Format")
    cli.add_argument("-r", "--res", dest="res", required=True, type=argparse.FileType("r"),
                     help="hashcat result file, format should be (plain:crack_pos)")
    cli.add_argument("-t", "--target", dest="target", required=True, type=argparse.FileType("r"),
                     help="target set that hashcat cracked")
    cli.add_argument("-s", "--save", dest="save", required=True, type=argparse.FileType("w"),
                     help="save results to this file")
    args = cli.parse_args()
    hc_res, targets, save2 = args.res, args.target, args.save
    wrapper(hc_res=hc_res, targets=targets, save2=save2)


if __name__ == '__main__':
    main()
