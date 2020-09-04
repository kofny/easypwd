#!/usr/bin/env python3
"""
Easy toolkit for Guess-Crack Curve
This is a method to beautify the data of guesses and cracked file
"""
import argparse
import json
import sys
from typing import TextIO, Tuple, Callable


def wc_l(file: TextIO, close_fd: bool = False):
    """
    a pure function, file will not be closed and move the pointer to the begin
    :param close_fd: whether close file or not
    :param file: file to count lines
    :return: number of lines
    """
    if file.closed:
        raise Exception(f"You are counting line number of {file.name},"
                        f" however, it has been closed")
    file.seek(0)
    new_line = "\n"
    buf_size = 8 * 1024 * 1024
    count = 0
    while True:
        buffer = file.read(buf_size)
        if not buffer:
            count += 1
            break
        count += buffer.count(new_line)
    if close_fd:
        file.close()
    else:
        file.seek(0)
    return count


def default_key(line: str):
    try:
        _, _, _, guesses, cracked, _ = line.strip("\r\n").split("\t")
        guesses, cracked = int(guesses), int(cracked)
        return guesses, cracked
    except ValueError:
        print(f"{line} can not be parsed by default parser, rewrite this function", file=sys.stderr)
        sys.exit(-1)


def actual_key(line: str):
    try:
        _, _, guesses, cracked, _ = line.strip("\r\n").split("\t")
        guesses, cracked = int(guesses), int(cracked)
        return guesses, cracked
    except ValueError:
        print(f"{line} can not be parsed by default parser, rewrite this function", file=sys.stderr)
        sys.exit(-1)


def jsonify(label: str, fd_gc: TextIO, fd_save: TextIO,
            fd_test: TextIO, count_test: Callable[[TextIO, bool], int] = wc_l,
            lower_bound: int = 0, upper_bound: int = 10 ** 10,
            color: str = None, line_style: str = '-', line_width: float = 2, marker: str = None,
            key: Callable[[str], Tuple[int, int]] = default_key):
    """

    :param label:
    :param fd_gc:
    :param fd_save:
    :param lower_bound:
    :param upper_bound:
    :param color:
    :param line_style:
    :param line_width:
    :param marker:
    :param fd_test:
    :param count_test:
    :param key: parse line for result, identify whether threshold is larger than guesses number
    :return:
    """
    if not fd_save.writable() or fd_save.closed:
        raise Exception(f"{fd_save.name} is not writable or closed")
    if not fd_gc.readable() or fd_gc.closed:
        raise Exception(f"{fd_gc.name} is not readable or closed")
    total = count_test(fd_test, True)
    guesses_list = []
    cracked_list = []
    for line in fd_gc:
        guesses, cracked = key(line)
        if guesses < lower_bound:
            continue
        if guesses > upper_bound:
            break
        # do something here
        guesses_list.append(guesses)
        cracked_list.append(cracked)
    fd_gc.close()
    curve = {
        "label": label,
        "total": total,
        "marker": marker,
        "color": color,
        "line_style": line_style,
        "line_width": line_width,
        "guesses_list": guesses_list,
        "cracked_list": cracked_list
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
    cli.add_argument("-t", "--test", required=True, dest="fd_test", type=argparse.FileType('r'),
                     help="test set, to count number of passwords in test set")
    cli.add_argument("--lower", required=False, dest="lower_bound", default=0, type=int,
                     help="guesses less than this will be ignored and will not appear in beautified json file")
    cli.add_argument("--upper", required=False, dest="upper_bound", default=10 ** 10, type=int,
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
    cli.add_argument("--idx-crack", required=False, dest="idx_crack", default=4, type=int,
                     help="index of crack in a split line, start from 0")
    args = cli.parse_args()

    def my_key(line: str):
        try:
            split_line = line.strip("\r\n").split(args.gc_split)
            return int(split_line[args.idx_guess]), int(split_line[args.idx_crack])
        except ValueError:
            print(f"file to get guess and crack in {line}", end="")
            print(f"Your gc-split is '{args.gc_split}',\n"
                  f"    idx_guess is '{args.idx_guess}',\n"
                  f"    idx_crack is '{args.idx_crack}'")
            sys.exit(-1)

    jsonify(label=args.label, fd_gc=args.fd_gc, fd_save=args.fd_save, fd_test=args.fd_test,
            lower_bound=args.lower_bound, upper_bound=args.upper_bound, color=args.color,
            marker=args.marker,
            line_style=line_style_dict.get(args.line_style, "solid"),
            line_width=args.line_width, key=my_key)


if __name__ == '__main__':
    main()
