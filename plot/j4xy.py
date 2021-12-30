#!/usr/bin/env python3
"""
Json for CDF Zipf (j4cdf)
"""
import argparse
import json
from typing import Dict, Tuple, Callable, List, Union

import numpy
import pandas as pd

"""
total <= 0 refers to that we will not divide total to apply y_list
"""


def read_cdf(file: str) -> Tuple[List[int], List[float]]:
    with open(file) as f_file:
        data = pd.read_csv(f_file, names=["rank", "freq"])
        raw = list(numpy.array(data[["freq"]]))
        y = [i[0].split('/') for i in raw]
        y = [float(a[0]) / float(a[-1]) for a in y]
        x = [int(i) for i in list(numpy.array(data[['rank']]))]
        return x, y


def read_adams(file: str) -> Tuple[List[float], List[float]]:
    import re
    with open(file) as f_src:
        x, y = [], []
        data = re.compile(r"\[LOG]: \(#guesses: (\d+) \|~10\^\d\|\)\t\(recovered: ([.\d]+)%\)")
        for line in f_src:
            line = line.strip("\r\n")
            g = data.match(line)
            if g is not None:
                guess, cracked = g.groups()
                x.append(int(guess))
                y.append(float(cracked))
        return x, y


def read_gc(file: str) -> Tuple[List[float], List[float]]:
    with open(file) as f_src:
        x, y = [], []
        for line in f_src:
            _, _, _, rank, cracked, _ = line.strip("\r\n").split("\t")
            x.append(int(rank))
            y.append(int(cracked))
        return x, y


def read_bert_adams(file: str):
    with open(file) as f_src:
        x, y = [], []
        for line in f_src:
            _, _, _, rank, _, acc = line.strip("\r\n").split('\t')
            x.append(int(rank))
            y.append(int(acc))
        return x, y


def wrapper():
    cli = argparse.ArgumentParser("Parse data in various format into `default.json`-format")
    task_func_dict: Dict[str, Callable[[str], Tuple[List[Union[float, int]], List[float]]]] = {
        'cdf': read_cdf,
        'adams': read_adams,
        'gc': read_gc,
        'bert_adams': read_bert_adams,
    }
    cli.add_argument("-l", "--label", required=False, dest="label", default=None, type=str,
                     help="how to identify this curve")
    cli.add_argument("-f", "--file", required=False, dest="fd_in", type=str,
                     default=None, help="CDF Zipf result file to be parsed")
    cli.add_argument('-t', "--task", required=True, dest='task', type=str, choices=list(task_func_dict.keys()),
                     help='Choose the task you want to call')
    cli.add_argument("--total", default=-1, type=int,
                     help='the total number. It is useful when we calculate the percentage')
    cli.add_argument("-s", "--save", required=True, dest="fd_save", type=str,
                     help="save parsed data here")
    cli.add_argument("--lower", required=False, dest="lower_bound", default=0, type=int,
                     help="guesses less than this will be ignored and will not appear in beautified json file")
    cli.add_argument("--upper", required=False, dest="upper_bound", default=10 ** 18, type=int,
                     help="guesses greater than this will be ignored and will not appear in beautified json file")
    cli.add_argument("-c", "--color", required=False, dest="color", default=None, type=str,
                     help="color of curve, using DEFAULT config if you dont set this flag")
    cli.add_argument("--line-style", required=False, dest="line_style", default="solid", type=str,
                     help="style of line, solid or other")
    cli.add_argument("--marker", required=False, dest="marker", default=None, type=str,
                     choices=["|", "+", "o", ".", ",", "<", ">", "v", "^", "1", "2", "3", "4", "s", "p", "_", "x", "*",
                              "D", 'P', 'h', 'H', 'X'],
                     help="the marker for points of curve, default None")
    cli.add_argument("--marker-size", required=False, dest="marker_size", default=2, type=float,
                     help="marker size")
    cli.add_argument("--mark-every", required=False, dest="mark_every", default=None, type=int, nargs="+",
                     help="show marker every n points")
    cli.add_argument("--line-width", required=False, dest="line_width", default=1.0, type=float,
                     help="width of line, can be float point number")
    cli.add_argument("--show-text", required=False, dest="show_text", action="store_true",
                     help="show text at specified position")
    cli.add_argument("--text-x", required=False, dest="text_x", default=0, type=float,
                     help='x position of text')
    cli.add_argument("--text-y", required=False, dest="text_y", default=0, type=float,
                     help='y position of text')
    cli.add_argument("--text-fontsize", required=False, dest="text_fontsize", default=12, type=int,
                     help='fontsize of text')
    args = cli.parse_args()

    line_style = args.line_style
    if line_style not in {'solid', 'dashed', 'dashdot', 'dotted'}:
        seq = [float(i) for i in line_style.split(" ") if len(i) > 0]
        offset = seq[0]
        onoffseq = seq[1:]
        if len(onoffseq) % 2 != 0:
            raise Exception("onoffseq should have even items!")
        line_style = (offset, tuple(onoffseq))
    chosen_task = task_func_dict[args.task]
    x, y = chosen_task(args.fd_in)
    text_color = args.color if args.color is not None else "black"
    total = args.total
    json.dump({
        "label": args.label,
        "total": total,
        "need_divide_total": total > 0,
        "marker": args.marker,
        "marker_size": args.marker_size,
        "mark_every": args.mark_every,
        "color": args.color,
        "line_style": line_style,
        "line_width": args.line_width,
        "text_x": args.text_x,
        "text_y": args.text_y,
        "text_fontsize": args.text_fontsize,
        "text_color": text_color,
        "show_text": args.show_text,
        "x_list": x,
        "y_list": y,
    }, open(args.fd_save, "w"), indent=2)
    pass


if __name__ == '__main__':
    wrapper()
