"""
This is augmented version of rankcmp.py
Now we can set color of the cell in LaTeX format


Compare the ranks obtained by two methods in a table
Note that the passwords and their frequencies should be the same in the two input files
"""

import argparse
import bisect
import re
import sys
from collections import defaultdict
from typing import TextIO, List, Dict, Tuple


def read_raw_data(fds: List[TextIO], skip=1, splitter=re.compile("\t"), idx_pwd=0, idx_rank=1, idx_num=2):
    maps = []
    for fd in fds:
        lst = []
        for _ in range(skip):
            fd.readline()
        for line in fd:
            line = line.strip("\r\n")
            items = splitter.split(line)
            pwd = items[idx_pwd]
            rank = float(items[idx_rank])
            num = int(items[idx_num])
            lst.append((pwd, rank, num))
        fd.close()
        lst = sorted(lst, key=lambda x: x[1])
        _map = {pwd: (rank, freq) for pwd, rank, freq in lst}
        maps.append(_map)
    return maps


def get_color_map(name: str):
    try:
        import matplotlib.pyplot as plt
        return plt.get_cmap(name)
    except ImportError:
        print("Failed to import matplotlib. Make sure that you have installed matplotlib:\n"
              "\tpip install matplotlib", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Failed to get color map named " + name +
              ". Ignore specified color. Make sure that you have typed in the correct"
              " name based on the following link: \n"
              "https://matplotlib.org/stable/tutorials/colors/colormaps.html#sequential", end=sys.stderr)
        return None


def gen_table(guess_number_thresholds: List[int], guess_number_display_list: List[str],
              map_as: List[Dict[str, Tuple[int, int]]], map_bs: List[Dict[str, Tuple[int, int]]],
              color_map_bottom_left=None, color_map_top_right=None, color_map_diagonal=None):
    tables = []
    totals = []
    for index in range(len(map_as)):
        map_a = map_as[index]
        map_b = map_bs[index]
        tables.append(defaultdict(lambda: defaultdict(lambda: 0)))
        for pwd, info_a in map_a.items():
            rank_a, cnt = info_a
            # info_b = map_b.get(pwd, (sys.maxsize, info_a[1]))
            rank_b = map_b.get(pwd, (sys.maxsize, cnt))[0]
            idx_a = bisect.bisect_left(guess_number_thresholds, rank_a)
            idx_b = bisect.bisect_left(guess_number_thresholds, rank_b)
            tables[index][idx_b][idx_a] += cnt
        totals.append(sum([f for _, f in map_a.values()]))

    def print_table(splitter="\t", percent=True,
                    cmap_bl=color_map_bottom_left, cmap_tr=color_map_top_right, cmap_d=color_map_diagonal):
        for i in range(1, len(guess_number_thresholds) + 1):
            print(f"{guess_number_display_list[i - 1]:18}", end=splitter)
            for j in range(1, len(guess_number_thresholds) + 1):
                if j == len(guess_number_thresholds):
                    the_end = " \\\\\n"
                else:
                    the_end = splitter
                percent_val, real_val = 0, 0
                for idx in range(len(tables)):
                    percent_val += tables[idx][i][j] / totals[idx]
                    real_val += tables[idx][i][j]

                if percent_val <= 1e-5:
                    cell_color = ""
                elif i == j and cmap_d is not None:
                    cell_color = f"\\cellcolor[rgb]{{{', '.join([f'{itm:.6f}' for itm in cmap_d(percent_val)[:3]])}}}"
                elif i < j and cmap_tr is not None:
                    cell_color = f"\\cellcolor[rgb]{{{', '.join([f'{itm:.6f}' for itm in cmap_tr(percent_val)[:3]])}}}"
                elif i > j and cmap_bl is not None:
                    cell_color = f"\\cellcolor[rgb]{{{', '.join([f'{itm:.6f}' for itm in cmap_bl(percent_val)[:3]])}}}"
                else:
                    cell_color = ""

                if percent:
                    cell_value = f"{cell_color}{percent_val / len(tables) * 100:5.2f}\\%"
                else:
                    cell_value = f"{cell_color}{real_val // len(tables):5d}"

                print(cell_value, end=the_end)

    print("Print percentages, LaTeX format.\n"
          "file a is placed on the top of the table, file b is placed on the left of the table.")
    print_table(" & ", True)

    print("\nPrint frequencies, LaTeX format")
    print_table(" & ", False)

    print("\nPrint percentages, LaTeX format without colors.")
    print_table(" & ", True, None, None, None)

    print("\nPrint frequencies, LaTeX format")
    print_table(" & ", False, None, None, None)
    pass


def wrapper():
    cli = argparse.ArgumentParser("Unsafe Errors")
    cli.add_argument("-a", "--file-a", dest="fd_a", required=True, type=argparse.FileType('r'), nargs='+',
                     help="one file containing passwords, ranks and frequencies")
    cli.add_argument("-b", "--file-b", dest="fd_b", required=True, type=argparse.FileType('r'), nargs='+',
                     help="another file containing passwords, ranks and frequencies")
    cli.add_argument("--idx-pwd", dest="idx_pwd", required=True, type=int,
                     help="passwords are in \"idx-pwd\"th column, start from 0")
    cli.add_argument("--idx-rank", dest="idx_rank", required=True, type=int,
                     help="ranks are in \"idx-rank\"th column, start from 0")
    cli.add_argument("--idx-freq", dest="idx_freq", required=True, type=int,
                     help="frequencies are in \"idx-freq\"th column, start from 0")
    cli.add_argument("-k", "--skip", dest="skip", required=False, type=int, default=1,
                     help="Ignore the first k lines")
    cli.add_argument("-s", '--splitter', dest="splitter", type=lambda x: re.compile(x), required=False,
                     default=re.compile("\t"),
                     help="splitter of the lines")
    cli.add_argument("-t", "--thresholds", dest="thresholds",
                     default=[0, 10 ** 4, 10 ** 8, 10 ** 12, 10 ** 16, 10 ** 20],
                     type=int, required=False, nargs='+', help="the thresholds of guess numbers")
    cli.add_argument("-d", "--display", dest="display",
                     default=['\\textgreater1e0', '\\textgreater1e4', '\\textgreater1e8', '\\textgreater1e12',
                              '\\textgreater1e16', '\\textgreater1e20'],
                     type=str, required=False, nargs='+',
                     help="How to show the thresholds in string (support LaTex format)")
    cli.add_argument("-color-maps", required=False, dest="color_maps", nargs=3, type=str,
                     default=["Greens", "Reds", "Purples"],
                     help="Need three color names to color the table. "
                          "Form left to right, the color is used for ``diagonal``, ``bottom left``, ``top right``"
                          " part of the table.")
    args = cli.parse_args()

    gen_table(args.thresholds, args.display,
              read_raw_data(args.fd_a, args.skip, args.splitter, args.idx_pwd, args.idx_rank, args.idx_freq),
              read_raw_data(args.fd_b, args.skip, args.splitter, args.idx_pwd, args.idx_rank, args.idx_freq),
              color_map_diagonal=get_color_map(args.color_maps[0]),
              color_map_bottom_left=get_color_map(args.color_maps[1]),
              color_map_top_right=get_color_map(args.color_maps[2]))
    pass


if __name__ == '__main__':
    wrapper()
