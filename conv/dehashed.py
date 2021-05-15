#!/usr/bin/env python3
"""
The output file of hashcat is hard to read to some extend.
This file will obtain the dehashed passwords in the output of hashcat.
"""
import argparse
from typing import TextIO
from collections import defaultdict
import binascii


def hex2str(hex_str):
    _hex = hex_str.encode('utf-8')
    str_bin = binascii.unhexlify(_hex)
    return str_bin.decode('utf-8')


def parse_hc_res(hc_res: TextIO, wanted_idx: int, save2: TextIO, hashes: TextIO):
    needed = defaultdict(int)
    for line in hashes:
        line = line.strip("\r\n")
        items = line.split(":")
        needed[items[0]] += 1
    for line in hc_res:
        line = line.strip("\r\n")
        items = line.split(":")
        _hash = items[0]
        _wanted = items[wanted_idx]
        if _wanted.startswith(r'$HEX['):
            _wanted = hex2str(_wanted[5:-1])
        for _ in range(needed[_hash]):
            save2.write(f"{_wanted}\n")


def main():
    cli = argparse.ArgumentParser("Convert Result of hashcat to Easy-to-read Format")
    cli.add_argument("-i", "--input", dest="res", required=True, type=argparse.FileType("r"),
                     help="hashcat result file, format should be (plain:crack_pos)")
    cli.add_argument("--idx", dest="wanted_idx", required=True, type=int, default=1, help="which column do you want?")
    cli.add_argument("--hashes", dest="hashes", required=True, type=argparse.FileType('r'),
                     help="The number of each hash")
    cli.add_argument("-s", "--save", dest="save", required=True, type=argparse.FileType("w"),
                     help="save results to this file")
    args = cli.parse_args()
    hc_res, save2 = args.res, args.save
    idx, hashes = args.wanted_idx, args.hashes
    parse_hc_res(hc_res=hc_res, wanted_idx=idx, save2=save2, hashes=hashes)


if __name__ == '__main__':
    main()
