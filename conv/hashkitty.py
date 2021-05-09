#!/usr/bin/env python3
"""
The output file of hashcat is hard to read to some extend.
THis file will convert the output of (plain, crack_pos) to (pwd, num, #guesses, #cracked, %cracked)
"""
import argparse
import sys
from collections import defaultdict
from typing import TextIO, Dict, Generator, Tuple, Any
import binascii


def hex2str(hex_str):
    _hex = hex_str.encode('utf-8')
    str_bin = binascii.unhexlify(_hex)
    return str_bin.decode('utf-8')


def read_hc_res(hc_res: TextIO,
                hash_idx: int = 0, pwd_idx: int = 1, guess_number_idx: int = 2) -> Dict[str, int]:
    hashes_pos = {}
    for line in hc_res:
        line = line.strip("\r\n")
        items = line.split(":")
        _hash, _pwd, _guess_number = items[hash_idx], items[pwd_idx], items[guess_number_idx]
        if _pwd.startswith(r'#HEX['):
            _pwd = hex2str(_pwd[5:-1])
        hashes_pos[_hash] = int(_guess_number)
    return hashes_pos


def read_target_set(f_hashes: TextIO) -> Dict[str, int]:
    hashes = defaultdict(int)
    for line in f_hashes:
        line = line.strip("\r\n")
        hashes[line] += 1
    f_hashes.close()
    return hashes


def hcgood(hashes_pos: Dict[str, int], hashes_cnt: Dict[str, int]):
    total = sum(hashes_cnt.values())
    hash_cnt_pos_list = []
    for _hash, cnt in hashes_cnt.items():
        crack_pos = hashes_pos.get(_hash, sys.float_info.max)
        hash_cnt_pos_list.append((_hash, cnt, crack_pos))
    del hashes_cnt
    del hashes_pos
    hash_cnt_pos_list = sorted(hash_cnt_pos_list, key=lambda x: x[2], reverse=False)
    cracked = 0
    for _hash, cnt, crack_pos in hash_cnt_pos_list:
        cracked += cnt
        yield _hash, .0, cnt, crack_pos, cracked, cracked / total * 100


def save(data: Generator[Tuple[str, float, int, int, int, float], Any, None], fd: TextIO, close_fd: bool = True):
    for pwd, prob, cnt, rank, cracked, cracked_rate in data:
        fd.write(f"{pwd}\t{prob}\t{cnt}\t{rank}\t{cracked}\t{cracked_rate:5.2f}\n")
    fd.flush()
    if close_fd:
        fd.close()


def wrapper(hc_res: TextIO, f_hashes: TextIO, save2: TextIO):
    pwd_pos = read_hc_res(hc_res)
    hc_res.close()
    pwd_cnt = read_target_set(f_hashes)
    f_hashes.close()
    hcg = hcgood(pwd_pos, pwd_cnt)
    save(hcg, save2, close_fd=True)


def main():
    cli = argparse.ArgumentParser("Convert Result of hashcat to Easy-to-read Format")
    cli.add_argument("-i", "--input", dest="res", required=True, type=argparse.FileType("r"),
                     help="hashcat result file, format should be (plain:crack_pos)")
    cli.add_argument("-t", "--hashes", dest="target", required=True, type=argparse.FileType("r"),
                     help="hashes file")
    cli.add_argument("-s", "--save", dest="save", required=True, type=argparse.FileType("w"),
                     help="save results to this file")
    args = cli.parse_args()
    hc_res, targets, save2 = args.res, args.target, args.save
    wrapper(hc_res=hc_res, f_hashes=targets, save2=save2)


if __name__ == '__main__':
    main()
