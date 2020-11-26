#!/usr/bin/env python3
"""
Easy toolkit for Guess-Crack Curve
This is a method to beautify the data of guesses and cracked file
"""
import argparse
import json
import sys
from collections import defaultdict
from typing import TextIO, Tuple, Callable

default_pos = -10 ** 40


def read_dict(f_dict: TextIO):
    if f_dict is None:
        return []
    pwd_cnt = defaultdict(int)
    for line in f_dict:
        line = line.strip("\r\n")
        pwd_cnt[line] += 1
    sorted_pwd_cnt = sorted(pwd_cnt.items(), key=lambda x: x[1], reverse=True)
    f_dict.close()
    return [pwd for pwd, _ in sorted_pwd_cnt]


def count_test_set(file: TextIO, close_fd: bool = False):
    count = defaultdict(int)
    for line in file:
        line = line.strip("\r\n")
        count[line] += 1
    if close_fd:
        file.close()
    return count


def jsonify(label: str, fd_gc: TextIO, fd_save: TextIO, fd_dict: TextIO,
            fd_test: TextIO, key: Callable[[str], Tuple[str, int]],
            text_xy: Tuple[float, float], text_fontsize: int, show_text: bool,
            lower_bound: int = 0, upper_bound: int = 10 ** 10,
            color: str = None, line_style: str = '-', line_width: float = 2, marker: str = None
            ):
    if not fd_save.writable() or fd_save.closed:
        raise Exception(f"{fd_save.name} is not writable or closed")
    if not fd_gc.readable() or fd_gc.closed:
        raise Exception(f"{fd_gc.name} is not readable or closed")

    test_items = count_test_set(fd_test, True)
    pwd_dict = read_dict(fd_dict)
    total = sum(test_items.values())
    guesses_list = []
    cracked_list = []
    cracked = 0

    for guesses, pwd in enumerate(pwd_dict):
        if pwd not in test_items:
            continue
        cracked += test_items[pwd]
        del test_items[pwd]
        if guesses < lower_bound:
            continue
        if guesses > upper_bound:
            break
        guesses_list.append(guesses)
        cracked_list.append(cracked)
    base_guesses = len(pwd_dict)
    for line in fd_gc:
        pwd, guesses = key(line)
        if pwd not in test_items:
            continue
        cracked += test_items[pwd]
        guesses += base_guesses
        del test_items[pwd]
        if guesses < lower_bound:
            continue
        if guesses > upper_bound:
            break
        guesses_list.append(guesses)
        cracked_list.append(cracked)
    fd_gc.close()
    text_x, text_y = text_xy
    if text_x != default_pos and text_y != default_pos:
        show_text = True
    if text_x == default_pos:
        text_x = guesses_list[-1]
    if text_y == default_pos:
        text_y = cracked_list[-1] / total * 100

    if color is None:
        text_color = "black"
    else:
        text_color = color
    curve = {
        "label": label,
        "total": total,
        "marker": marker,
        "color": color,
        "line_style": line_style,
        "line_width": line_width,
        "guesses_list": guesses_list,
        "cracked_list": cracked_list,
        "text_x": text_x,
        "text_y": text_y,
        "text_fontsize": text_fontsize,
        "text_color": text_color,
        "show_text": show_text,
    }
    json.dump(curve, fd_save, indent=2)
    fd_save.close()


def main():
    line_style_dict = {
        "solid": "-",
        "dash": "--",
        "dot_dash": "-.",
        "dot": ":"
    }
    cli = argparse.ArgumentParser("Beautify Guess-Crack result file")
    cli.add_argument("-l", "--label", required=False, dest="label", default=None, type=str,
                     help="how to identify this curve")
    cli.add_argument("-f", "--gc", required=True, dest="fd_gc", type=argparse.FileType("r"),
                     help="guess crack file to be parsed")
    cli.add_argument("-s", "--save", required=True, dest="fd_save", type=argparse.FileType("w"),
                     help="save parsed data here")
    cli.add_argument("-d", "--dict-attack", required=False, dest="fd_dict", type=argparse.FileType('r'),
                     default=None, help="apply dict attack first")
    cli.add_argument("-t", "--test", required=True, dest="fd_test", type=argparse.FileType('r'),
                     help="test set, to count number of passwords in test set")
    cli.add_argument("--lower", required=False, dest="lower_bound", default=0, type=int,
                     help="guesses less than this will be ignored and will not appear in beautified json file")
    cli.add_argument("--upper", required=False, dest="upper_bound", default=10 ** 18, type=int,
                     help="guesses greater than this will be ignored and will not appear in beautified json file")
    cli.add_argument("-c", "--color", required=False, dest="color", default=None, type=str,
                     help="color of curve, using DEFAULT config if you dont set this flag")
    cli.add_argument("--line-style", required=False, dest="line_style", default="solid", type=str,
                     choices=list(line_style_dict.keys()), help="style of line, solid or other")
    cli.add_argument("--marker", required=False, dest="marker", default=None, type=str,
                     choices=["+", "o", ".", ",", "<", ">", "v", "^", "1", "2", "3", "4", "s", "p", "_", "x", "*"],
                     help="the marker for points of curve, default None")
    cli.add_argument("--line-width", required=False, dest="line_width", default=1.0, type=float,
                     help="width of line, can be float point number")
    cli.add_argument("--gc-split", required=False, dest="gc_split", default="\t", type=str,
                     help="how to split a line in guess-crack file, default is '\\t'")
    cli.add_argument("--idx-guess", required=False, dest="idx_guess", default=3, type=int,
                     help="index of guess in a split line, start from 0")
    cli.add_argument("--idx-pwd", required=False, dest="idx_pwd", default=0, type=int,
                     help="index of pwd in a split line, start from 0")
    cli.add_argument("--show-text", required=False, dest="show_text", action="store_true",
                     help="show text at specified position")
    cli.add_argument("--text-x", required=False, dest="text_x", default=default_pos, type=float,
                     help='x position of text')
    cli.add_argument("--text-y", required=False, dest="text_y", default=default_pos, type=float,
                     help='y position of text')
    cli.add_argument("--text-fontsize", required=False, dest="text_fontsize", default=12, type=int,
                     help='fontsize of text')

    args = cli.parse_args()

    gc_split = args.gc_split.replace('\\\\', '\\')

    def my_key(line: str):
        try:
            split_line = line.strip("\r\n").split(gc_split)
            return split_line[args.idx_pwd], int(split_line[args.idx_guess])
        except Exception as e:
            print(e, file=sys.stderr)
            print(f"file to get guess and crack in {line}", end="", file=sys.stderr)
            print(f"Your gc-split is '{gc_split}',\n"
                  f"    idx_pwd is '{args.idx_pwd}',\n"
                  f"    idx_guess is '{args.idx_guess}'", file=sys.stderr)
            sys.exit(-1)

    jsonify(label=args.label, fd_gc=args.fd_gc, fd_save=args.fd_save, fd_test=args.fd_test,
            fd_dict=args.fd_dict,
            lower_bound=args.lower_bound, upper_bound=args.upper_bound, color=args.color,
            marker=args.marker,
            line_style=line_style_dict.get(args.line_style, "solid"),
            line_width=args.line_width, key=my_key, text_xy=(args.text_x, args.text_y),
            text_fontsize=args.text_fontsize, show_text=args.show_text)


if __name__ == '__main__':
    main()
