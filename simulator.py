"""
This is a Monte Carlo Simulator.
What we need is just sampled probabilities and scored target set
"""
import argparse
import bisect
from math import log2
from typing import TextIO, List, Tuple, Generator


def my_cumsum(lst: List[float]):
    if len(lst) <= 0:
        return []
    acc = 0
    cumsum = []
    for v in lst:
        acc += v
        cumsum.append(acc)
    return cumsum


def read_ml2p_list(ml2p_file: TextIO, close_fd: bool) -> List[float]:
    """
    a probability per line (log2)
    file will be closed if close_fd is True
    :param ml2p_file:
    :param close_fd:
    :return:
    """
    ml2p_list = []
    ml2p_file.seek(0)
    for line in ml2p_file:
        ml2p = float(line.strip("\r\n"))
        ml2p_list.append(ml2p)
    if close_fd:
        ml2p_file.close()
    return ml2p_list


def rank_from_minus_log2prob(ml2p_list: List[float]) -> (List[float], List[float]):
    """
    sampled probabilities (log2)
    :param ml2p_list:
    :return:
    """
    ml2p_list.sort()
    logn = log2(len(ml2p_list))
    ranks = my_cumsum([2 ** (ml2p - logn) for ml2p in ml2p_list])
    return ml2p_list, ranks


def minus_log_prob2rank(minus_log_probs: List[float], positions: List[float], minus_log_prob: float) -> float:
    idx = bisect.bisect_right(minus_log_probs, minus_log_prob)
    return positions[idx - 1] if idx > 0 else 1


def read_scored_target(scored: TextIO, splitter: str = "\t", close_fd: bool = True) -> List[Tuple[str, int, float]]:
    scored.seek(0)
    scored_list = []
    for line in scored:
        pwd, num, prob = line.strip("\r\n").split(splitter)
        scored_list.append((pwd, int(num), float(prob)))
    if close_fd:
        scored.close()
    return scored_list


def simulator(scored_list: List[Tuple[str, int, float]], ml2p_list: List[float], ranks: List[float]):
    """
    simulate crack-guess curve
    :param scored_list: list of (pwd, num, ml2p)
    :param ml2p_list: ml2p of sampled passwords
    :param ranks: ranks of sampled passwords
    :return:
    """
    prev_rank = 0
    cracked = 0
    scored_list = sorted(scored_list, key=lambda _pwd, _num, _ml2p: _ml2p, reverse=False)
    total = sum([_num for _, _num, _ in scored_list])
    for pwd, num, ml2p in scored_list:
        rank = int(max(minus_log_prob2rank(ml2p_list, ranks, ml2p), prev_rank + 1) + 0.5)
        prev_rank = rank
        cracked += num
        yield pwd, ml2p, num, rank, cracked, cracked / total * 100
    del scored_list
    del ml2p_list
    del ranks


def saver(itr: Generator[Tuple[str, float, int, int, int, float]], save2: TextIO):
    for pwd, ml2p, num, rank, cracked, cracked_rate in itr:
        save2.write(f"{pwd}\t{ml2p:.8f}\t{num}\t{rank}\t{cracked}\t{cracked_rate:.2f}\n")
    save2.close()
    pass


def main():
    cli = argparse.ArgumentParser("Monte Carlo Simulator Wrapper")
    cli.add_argument("-p", "--prob", required=True, dest="prob", type=argparse.FileType('r'),
                     help="prob of sampled passwords")
    cli.add_argument("-t", "--target", required=True, dest="scored", type=argparse.FileType("r"),
                     help="(pwd, num, minus log2 prob) of passwords in target set")
    cli.add_argument("-s", "--save", required=True, dest="save", type=argparse.FileType("w"),
                     help="save (pwd, minus log2 prob, num, #guesses, #cracked, %cracked) to this file")
    args = cli.parse_args()
    ml2p_list = read_ml2p_list(ml2p_file=args.prob, close_fd=True)
    ml2p_list, ranks = rank_from_minus_log2prob(ml2p_list=ml2p_list)
    scored_list = read_scored_target(scored=args.scored, close_fd=True)
    itr = simulator(scored_list=scored_list, ml2p_list=ml2p_list, ranks=ranks)
    saver(itr=itr, save2=args.save)
    pass


if __name__ == '__main__':
    main()
