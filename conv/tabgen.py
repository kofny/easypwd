#!/usr/bin/env python3
"""
Generate table for LaTeX
"""
import argparse
import os
import sys
from math import ceil
from typing import List, TextIO

__conv_dict = {
    "$": r"\$",
    "#": r"\#",
    "&": r"\&",
    "%": r"\%",
    "{": r"\{",
    "}": r"\}",
    "~": r"\~{}",
    "_": r"\_{}",
    "^": r"\^{}",
    "\\": r"\textbackslash",
    "|": r"$\vert$",
    ">": r"\textgreater",
    "<": r"\textless",
}


def conv_latex(s: str) -> str:
    converted = ""
    for c in s:
        if c in __conv_dict:
            converted += __conv_dict[c]
        else:
            converted += c
    return converted


def texify(columns: List[List[str]], top: float, percentage: bool, cnt: int, skip: int, conv: bool):
    """

    :param columns: columns of table
    :param top: use elements in top items
    :param percentage: top is a percent
    :param cnt: how many samples
    :param skip: skip top_skip items
    :param conv: convert to latex table
    :return:
    """
    top, percentage, cnt, skip = abs(top), abs(percentage), abs(cnt), abs(skip)
    if skip >= cnt:
        raise Exception(f"Skip too many items")
    table: List[List[str]] = [[] for _ in range(cnt - skip)]
    for column in columns:
        n_row = len(column)
        tmp_top = top
        if percentage:
            tmp_top = ceil(top * n_row)
        if tmp_top > n_row:
            tmp_top = n_row
        if cnt > tmp_top:
            raise Exception(f"Invalid cnt: {cnt}, top: {tmp_top}, row: {n_row}")
        step = tmp_top / cnt
        indices = [i * step for i in range(cnt)]
        indices = [max(int(idx), int(indices[i - 1]) + 1) if i > 0 else int(idx) for i, idx in enumerate(indices)]
        for i, idx in enumerate(indices):
            if i < skip:
                continue
            s = column[idx]
            if len(s) > 2 and s.endswith("@@"):
                s = s[:len(s) - 2] + "<w>"
            if conv:
                table[i - skip].append(conv_latex(s))
            else:
                table[i - skip].append(s)
        pass
    return table


def show_table(table: List[List[str]], fd: TextIO):
    if not fd.writable():
        raise Exception(f"Can not write into {fd.name}")
    for row in table:
        output = f" {' & '.join(row)} \\\\ {os.linesep}"
        fd.write(output)


def read_columns(files: List[TextIO]):
    columns = []
    for file in files:
        column = []
        for line in file:
            line = line.strip("\r\n")
            item = line.split(" ")[0]
            column.append(item)
        columns.append(column)
    return columns
    pass


def main():
    cli = argparse.ArgumentParser("Table Generator")
    cli.add_argument("-f", "--files", required=True, nargs="+", type=argparse.FileType("r"), help="files")
    cli.add_argument("-u", "--universe", required=True, type=float, help="top lines")
    cli.add_argument("--percentage", required=False, default=False, action="store_true",
                     help="--universe is percentage")
    cli.add_argument("-n", "--sample-n", required=True, type=int, help="sample n items averagely")
    cli.add_argument("-k", "--skip", required=False, default=1, type=int, help="skip first k items")
    cli.add_argument("--latex", required=False, default=False, action="store_true", help="latex format")
    cli.add_argument("-o", "--output", required=False, default=sys.stdout, type=argparse.FileType("w"),
                     help="save table")
    args = cli.parse_args()
    columns = read_columns(args.files)
    table = texify(columns=columns, top=args.universe, percentage=args.percentage, cnt=args.sample_n, skip=args.skip,
                   conv=args.latex)
    show_table(table, args.output)
    pass


if __name__ == '__main__':
    main()
