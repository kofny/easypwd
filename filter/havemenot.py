#!/usr/bin/env python3
"""
testing set has some passwords, and these passwords are not in training set.
"""
import argparse
from collections import defaultdict
from typing import Dict, TextIO, Tuple


def diff(testing_set: Dict[str, int], training_set: Dict[str, int]) -> Dict[str, int]:
    keys_in_testing_not_in_training = testing_set.keys() - training_set.keys()
    testing_set_only = {k: v for k, v in testing_set.items() if k in keys_in_testing_not_in_training}
    return testing_set_only


def read_sets(training: TextIO, testing: TextIO) -> Tuple[Dict[str, int], Dict[str, int]]:
    if not training.readable() or not testing.readable():
        raise Exception(f"Can not read {training.name} or {testing.name}")
    training_set = defaultdict(int)
    for line in training:
        line = line.strip("\r\n")
        training_set[line] += 1
    training.close()
    testing_set = defaultdict(int)
    for line in testing:
        line = line.strip("\r\n")
        testing_set[line] += 1
    testing.close()
    return training_set, testing_set


def main():
    cli = argparse.ArgumentParser("Remove intersections across training set and testing set")
    cli.add_argument("-s", "--src", dest="training", required=True, type=argparse.FileType('r'), help="training set")
    cli.add_argument("-t", "--tar", dest="testing", required=True, type=argparse.FileType('r'), help="training set")
    cli.add_argument("-o", "--out", dest="save", required=True, type=argparse.FileType('w'), help="save results")
    cli.add_argument("-m", "--minimal", dest="min_len", required=False, type=int, default=1,
                     help="passwords less than (not equal to) this will be ignored")
    args = cli.parse_args()
    training_set, testing_set = read_sets(training=args.training, testing=args.testing)
    testing_only = diff(testing_set=testing_set, training_set=training_set)
    min_len = max(1, args.min_len)
    for pwd, cnt in testing_only.items():
        if len(pwd) < min_len:
            continue
        s = f"{pwd}\n"
        for _ in range(cnt):
            args.save.write(s)
    args.save.close()
    pass


if __name__ == '__main__':
    main()
