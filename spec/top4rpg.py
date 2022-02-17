#!/usr/bin/env python3
"""
Top 10 rules for Rule-based Password Guessing.
"""
import argparse
import json
import sys
from typing import List


def read_rules(rule_path) -> List[str]:
    with open(rule_path, 'r') as f_rule:
        raw_rules = [r.strip() for r in f_rule]
        rules = [r for r in raw_rules if r and r[0] != '#']
    return rules


def top_rules(log_path: str, rules: List[str], n: int):
    counter = [[i, 0] for i in range(len(rules))]
    with open(log_path, 'r') as f_log:
        parsed = 0
        for line in f_log:
            if not line.startswith('['):
                continue
            line = line.strip('\r\n')
            word, rule_ids = json.loads(line)
            for rule_id in rule_ids:
                counter[rule_id][1] += 1
            parsed += 1
            if parsed % 1000 == 0:
                print(f"parsed {parsed}\r", end='')
    sorted(counter, key=lambda x: x[1], reverse=True)
    n = max(min(len(rules), n), 1)
    wanted_rules = [[rules[rule_id], count] for rule_id, count in counter[:n]]
    total_chosen = sum([count for _, count in counter])
    return wanted_rules, total_chosen


def top_hit_rules(rules: List[str], hit_path: str, n: int):
    hit_counter = [[i, 0] for i in range(len(rules))]
    rule_map = {}
    for i, rule in enumerate(rules):
        rule_map[rule] = i
    with open(hit_path, 'r') as f_hits:
        for hit_line in f_hits:
            word, _, rule, _, _, _ = hit_line.strip('\r\n').split('\t')
            rule_id = rule_map[rule]
            hit_counter[rule_id][1] += 1
        pass
    sorted(hit_counter, key=lambda x: x[1], reverse=True)
    n = max(min(len(rules), n), 1)
    wanted_rules = [[rules[rule_id], count] for rule_id, count in hit_counter[:n]]
    total_hit = sum([count for _, count in hit_counter])
    return wanted_rules, total_hit


def printing(rules, total, msg, fd=sys.stdout):
    print(msg, file=fd)
    for rule, count in rules:
        print(f"{rule:16}, {count:8}, {count / total:5.2%}", file=fd)
    pass


def wrapper():
    cli = argparse.ArgumentParser("Top Rules for RPG")
    cli.add_argument('-r', '--rules', dest='rules_path', required=True, type=str, help='filepath of rules')
    cli.add_argument('--log', dest='log_path', type=str, help='filepath of log')
    cli.add_argument('--hit', dest='hit_path', type=str, help='filepath of hit passwords based on `words + rules`')
    cli.add_argument('-n', '--top-n', dest='n', type=int, default=10, help='top n rules to display')
    args = cli.parse_args()
    rules = read_rules(rule_path=args.rules_path)
    if args.log_path is not None:
        chosen_rules, total_chosen = top_rules(log_path=args.log_path, rules=rules, n=args.n)
        printing(chosen_rules, total_chosen, msg='Chosen rules by model')
    if args.hit_path is not None:
        hit_rules, total_hit = top_hit_rules(hit_path=args.hit_path, rules=rules, n=args.n)
        printing(hit_rules, total_hit, msg='Hit rules by `words + rules`')
    pass


if __name__ == '__main__':
    wrapper()
    pass
