"""
We will mask some characters/chunks in passwords
"""
import argparse
import bisect
import random
from typing import Callable, List, Dict, Set
from collections import defaultdict
from functools import reduce

import math
import pickle

import sys


def read_passwords(password_file: str, line_splits: Callable[[str], List[str]], is_valid: Callable[[str], bool]):
    """

    :param password_file: file containing passwords per line
    :param line_splits: split passwords into one or several items (i.e., characters or chunks)
    :param is_valid: is the line a valid password
    :return: passwords, each password is a list
    """
    line_dict = defaultdict(int)
    total_pwd = 0
    valid_pwd = 0
    with open(password_file, 'r') as fin:
        for line in fin:
            line = line.strip('\r\n')
            total_pwd += 1
            if not is_valid(line):
                continue
            valid_pwd += 1
            line_dict[line] += 1
            pass
        pass
    print(f"total passwords: {total_pwd}, valid passwords: {valid_pwd}", file=sys.stderr)
    for line, _ in line_dict.items():
        pwd = line_splits(line)
        yield pwd
    pass


def comb(n, m):
    large, small = max(m, n - m), min(m, n - m)
    prod = reduce(lambda x, y: x * y, list(range(large + 1, n + 1)), 1)
    d = reduce(lambda x, y: x * y, list(range(2, small + 1)), 1)

    return prod // d


def masking(pwd: List[str], p: float, min_visible: int, min_masked: int,
            num_masked_prob_cache: Dict[int, List[float]], mask='\t'):
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
    prob_cum_list = num_masked_prob_cache[n]
    rand_float = random.random()
    idx = bisect.bisect_right(prob_cum_list, rand_float)
    m = min_masked + idx
    is_masks = [True] * m + [False] * (n - m)
    random.shuffle(is_masks)
    masked_pwd = []
    for item, is_mask in zip(pwd, is_masks):
        if is_mask:
            masked_pwd.append(mask)
        else:
            masked_pwd.append(item)
        pass
    return masked_pwd


def save_templates(templates_dict: Dict[str, Set], save: str):
    n_dict = {}
    for cls_name, templates in templates_dict.items():
        n_dict[cls_name] = templates
        print(f"{cls_name} has {len(templates)} items")
    with open(save, 'wb') as f_save:
        pickle.dump(n_dict, f_save)
    pass


def wrapper():
    cli = argparse.ArgumentParser("Masking passwords")
    cli.add_argument("-i", "--input", dest="input", type=str, required=True, help='Passwords to parse')
    cli.add_argument('-o', '--output', dest='output', type=str, required=True, help="Save sampled templates")
    cli.add_argument("--splitter", dest="splitter", type=str, required=False,
                     default='empty', help='split the password according to the splitter. '
                                           'Note that empty = ``, space = ` `, tab = `\\t`')
    cli.add_argument("-p", "--prob", dest="prob", type=float, required=False, default=0.5,
                     help="the probability of masking an item")
    cli.add_argument("-c", '--constraints', dest="constrains", type=int, nargs=2, required=False, default=[4, 5],
                     help='[a, b] refers to  we have at least `a` observable characters, `b` masked characters')
    cli.add_argument("-l", "--length-bound", dest="length_bound", type=str, required=False, default=16,
                     help='length longer than the bound will be ignored')
    cli.add_argument("-n", '--num-samples', dest='num_samples', type=int, default=30, required=False,
                     help='number of samples for each class of templates')
    cli.add_argument("-m", "--mask", dest="mask", type=str, required=False, default="\t",
                     help='the mask to replace the origin characters in passwords')
    args = cli.parse_args()
    pwd_file, splitter, p, (min_masked, min_visible), length_upper_bound, num_samples = \
        args.input, args.splitter.lower(), args.prob, args.constrains, args.length_bound, args.num_samples
    output, mask = args.output, args.mask
    length_lower_bound = min_masked + min_visible
    if splitter == 'empty':
        def line_splits(line: str):
            return list(line)
    else:
        splitter = {'space': ' ', 'tab': '\t'}.get(splitter, splitter)

        def line_splits(line: str):
            return line.split(splitter)

    def is_valid(line: str):
        return length_lower_bound <= len(line) <= length_upper_bound

    passwords = read_passwords(password_file=pwd_file, line_splits=line_splits, is_valid=is_valid)
    num_masked_prob_cache = {}
    pwd_mask_dict = defaultdict(set)
    for pwd in passwords:
        masked_pwd = masking(pwd=pwd, p=p, min_visible=min_visible, min_masked=min_masked,
                             num_masked_prob_cache=num_masked_prob_cache, mask=mask)
        pwd_mask_dict[tuple(masked_pwd)].add(tuple(pwd))
    print(f"templates: {len(pwd_mask_dict)}", file=sys.stderr)
    classes = [
        ('super-rare', [1, 5]),
        ('rare', [10, 15]),
        ('uncommon', [50, 150]),
        ('common', [1000, 1500])
    ]
    templates_dict = defaultdict(set)
    for masked_pwd, pwd_set in pwd_mask_dict.items():
        for cls_name, (lower_bound, upper_bound) in classes:
            if lower_bound <= len(pwd_set) <= upper_bound:
                templates_dict[cls_name].add(masked_pwd)
                break
        pass
    save_templates(templates_dict, save=output)
    pass


if __name__ == '__main__':
    wrapper()
