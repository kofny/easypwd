"""
Sampling some passwords from the dataset and generate a number of masked passwords (templates)
"""
import argparse
import bisect
import os.path
import random
from collections import defaultdict
from functools import reduce
from typing import Dict, List, Tuple

import math
import pickle
import sys


def read_pwd(pwd_file: str, len_lower_bound: int, len_upper_bound: int):
    pwd_cnt = defaultdict(int)
    with open(pwd_file, 'r') as f_pwd_file:
        for line in f_pwd_file:
            line = line.strip('\r\n')
            if len_lower_bound <= len(line) <= len_upper_bound:
                pwd_cnt[line] += 1
    len_pwd_cnt = defaultdict(dict)
    passwords = []
    for pwd, cnt in pwd_cnt.items():
        pwd = tuple(pwd)
        len_pwd_cnt[len(pwd)][pwd] = cnt
        passwords.append(pwd)
    return len_pwd_cnt, passwords


def match(pwd: Tuple, template: Tuple, mask: str):
    for a, b in zip(pwd, template):
        if b != mask and a != b:
            return False
    return True


def comb(_n, _m):
    large, small = max(_m, _n - _m), min(_m, _n - _m)
    prod = reduce(lambda x, y: x * y, list(range(large + 1, _n + 1)), 1)
    d = reduce(lambda x, y: x * y, list(range(2, small + 1)), 1)

    return prod // d


def worker(passwords_share, passwords, len_pwd_cnt, at_least_share, min_visible, min_masked, mask, classes, p, messages,
           msg_idx):
    round_index = 1
    total_passwords_share = len(passwords_share)
    num_masked_prob_cache = {}
    templates_dict = {}
    pwd_mask_dict = {}
    while True:
        pwd_idx = 1
        for pwd in passwords:
            n = len(pwd)
            max_masked = n - min_visible
            if max_masked < min_masked:
                raise Exception(f"The password should have at least {min_visible + min_masked} items, "
                                f"but {len(pwd)}: {pwd}")
                pass
            if n not in num_masked_prob_cache:
                prob_list = []
                total = 0
                for m in range(min_masked, max_masked + 1):
                    c = comb(n, m)
                    total += c * math.pow(p, m) * math.pow(1 - p, n - m)
                    prob_list.append(total)
                prob_list = [prob / total for prob in prob_list]
                num_masked_prob_cache[n] = prob_list
                pass
            idx = bisect.bisect_right(num_masked_prob_cache[n], random.random())
            m = min_masked + idx
            is_masks = [True] * m + [False] * (n - m)
            random.shuffle(is_masks)
            masked_pwd = tuple(mask if is_mask else item for item, is_mask in zip(pwd, is_masks))
            matched_passwords = set()
            pwd_len = len(pwd)
            for each_pwd in len_pwd_cnt[pwd_len].keys():
                if match(each_pwd, masked_pwd, mask):
                    matched_passwords.add(tuple(each_pwd))
                    pass
                pass

            for cls_name, (lower_bound, upper_bound) in classes:
                if lower_bound <= len(matched_passwords) <= upper_bound:
                    if cls_name not in templates_dict:
                        templates_dict[cls_name] = set()
                    if len(templates_dict[cls_name]) < at_least_share:
                        templates_dict[cls_name].add(masked_pwd)
                        pwd_mask_dict[masked_pwd] = matched_passwords
                    else:
                        del matched_passwords
                    break
                pass
            msg = []
            for cls_name, _ in classes:
                msg.append(f"{cls_name:>10}: {len(templates_dict.get(cls_name, [])):4,}")
            msg = f"[R{round_index:02}, {pwd_idx / total_passwords_share * 100:9.6f}%] {'; '.join(msg)}"
            messages[msg_idx] = msg
            pwd_idx += 1
            ok = len(templates_dict) == len(classes) and all(
                [len(templates) >= at_least_share for templates in templates_dict.values()])
            if ok:
                return templates_dict, pwd_mask_dict
            pass
        round_index += 1
        pass
    pass


def sampling(len_pwd_cnt: Dict[int, Dict[Tuple, int]], passwords: List[Tuple], at_least: int):
    random.shuffle(passwords)
    classes = [
        ('super-rare', [1, 5]),
        ('rare', [10, 15]),
        ('uncommon', [50, 150]),
        ('common', [1000, 15000])
    ]
    pwd_mask_dict = {}
    min_visible, min_masked = 4, 5
    p = 0.5  # the prob of masking a character or a chunk
    mask = '\t'

    num_masked_prob_cache = {}
    templates_dict = {}
    round_index = 1
    total_passwords = len(passwords)
    while True:
        pwd_idx = 1
        for pwd in passwords:
            n = len(pwd)
            max_masked = n - min_visible
            if max_masked < min_masked:
                raise Exception(f"The password should have at least {min_visible + min_masked} items, "
                                f"but {len(pwd)}: {pwd}")
                pass
            if n not in num_masked_prob_cache:
                prob_list = []
                total = 0
                for m in range(min_masked, max_masked + 1):
                    c = comb(n, m)
                    total += c * math.pow(p, m) * math.pow(1 - p, n - m)
                    prob_list.append(total)
                prob_list = [prob / total for prob in prob_list]
                num_masked_prob_cache[n] = prob_list
                pass
            idx = bisect.bisect_right(num_masked_prob_cache[n], random.random())
            m = min_masked + idx
            is_masks = [True] * m + [False] * (n - m)
            random.shuffle(is_masks)
            masked_pwd = tuple(mask if is_mask else item for item, is_mask in zip(pwd, is_masks))
            matched_passwords = set()
            pwd_len = len(pwd)
            for each_pwd in len_pwd_cnt[pwd_len].keys():
                if match(each_pwd, masked_pwd, mask):
                    matched_passwords.add(tuple(each_pwd))
                    pass
                pass

            for cls_name, (lower_bound, upper_bound) in classes:
                if lower_bound <= len(matched_passwords) <= upper_bound:
                    if cls_name not in templates_dict:
                        templates_dict[cls_name] = set()
                    if len(templates_dict[cls_name]) < at_least:
                        templates_dict[cls_name].add(masked_pwd)
                        pwd_mask_dict[masked_pwd] = matched_passwords
                    else:
                        del matched_passwords
                    break
                pass
            msg = []
            for cls_name, _ in classes:
                msg.append(f"{cls_name:>10}: {len(templates_dict.get(cls_name, [])):4,}")
            print(f"[R{round_index:02}, {pwd_idx / total_passwords * 100:9.6f}%] "
                  f"{'; '.join(msg)}", end='\r', file=sys.stderr)
            pwd_idx += 1
            ok = len(templates_dict) == len(classes) and all(
                [len(templates) >= at_least for templates in templates_dict.values()])
            if ok:
                print("")
                return templates_dict, pwd_mask_dict
            pass
        round_index += 1
        pass
    # templates_dict, _ = check(_pwd_mask_dict=pwd_mask_dict, cleanup=True)
    # return templates_dict, pwd_mask_dict


def wrapper():
    cli = argparse.ArgumentParser("Masking by randomly sampling")
    cli.add_argument("-i", '--passwords', dest='passwords', type=str, required=True, help='password file')
    cli.add_argument("--min", dest='at_least', type=int, required=False, default=120,
                     help='the min number of each class of templates')
    cli.add_argument("-c", '--constraints', dest="constrains", type=int, nargs=2, required=False, default=[4, 5],
                     help='[a, b] refers to  we have at least `a` observable characters, `b` masked characters')
    cli.add_argument("-l", "--length-bound", dest="length_bound", type=str, required=False, default=16,
                     help='length longer than the bound will be ignored')
    cli.add_argument("-s", '--save-in-folder', dest='save', type=str, required=True, help="save results in this folder")
    cli.add_argument("--cleanup", dest="cleanup", default=10000, type=int, required=False,
                     help='cleanup the templates which correspond to too few passwords '
                          '(depending on the `--threshold4cleanup` option)')
    cli.add_argument("--threshold4cleanup", dest='threshold4cleanup', default=1, type=int, required=False,
                     help='remove the template if its corresponding passwords is no more than `threshold4cleanup`')
    # cli.add_argument("")
    args = cli.parse_args()
    (min_visible, min_masked), length_upper_bound = args.constrains, args.length_bound
    cleanup_freq, threshold4cleanup = args.cleanup, args.threshold4cleanup
    save_folder = args.save
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    print("Pre-processing passwords...", end='', file=sys.stderr)
    len_pwd_cnt, passwords = read_pwd(pwd_file=args.passwords, len_lower_bound=min_visible + min_masked,
                                      len_upper_bound=length_upper_bound)
    print(f"{len(passwords)} valid passwords.", file=sys.stderr)
    # print(f"{len(len_pwd_cnt)} valid passwords found!", file=sys.stderr)
    templates_dict, pwd_mask_dict = sampling(
        len_pwd_cnt=len_pwd_cnt, passwords=passwords, at_least=args.at_least
    )
    masked_pickle = os.path.join(save_folder, 'masked.pickle')
    with open(masked_pickle, 'wb') as f_masked_pickle:
        pickle.dump((templates_dict, pwd_mask_dict), file=f_masked_pickle)

    pass


if __name__ == '__main__':
    try:
        wrapper()
    except KeyboardInterrupt:
        print("\n"
              "You cancelled the process", file=sys.stderr)
        sys.exit(1)
    pass
