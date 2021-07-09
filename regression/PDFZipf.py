"""
frequency-rank curves for PDF-Zipf model
"""
import argparse
from typing import TextIO, List
import sys
import math

try:
    import statsmodels.api as sm
    from scipy.stats import ks_2samp
except ImportError:
    print(f"Make sure that you have installed statsmodels and scipy:\n"
          f"\tpip install statsmodels scipy", file=sys.stderr)
    sys.exit(-1)


def read_frequency_list(fd_freq: TextIO, filter_less: int):
    freq_list = []
    for line in fd_freq:
        line = int(line.strip("\r\n"))
        freq_list.append(line)
    filtered_freq_list = [f for f in freq_list if f >= filter_less]
    coverage = f"{len(filtered_freq_list) / len(freq_list) * 100}%"
    return filtered_freq_list, coverage


def pdf_fitting(frequencies: List[int]):
    log_frequencies = [math.log10(f) for f in frequencies]
    log_ranks = [math.log10(r) for r in range(1, len(frequencies) + 1)]
    x_with_const = sm.add_constant(log_ranks)
    est = sm.OLS(log_frequencies, x_with_const)
    est = est.fit()
    c, s = est.params
    sim_frequencies = [10 ** c * r ** s for r in range(1, len(frequencies) + 1)]
    return sim_frequencies, est.params, est.pvalues, est.rsquared, est.rsquared_adj


def wrapper():
    cli = argparse.ArgumentParser("PDF-Zipf model")
    cli.add_argument("fd_freq", type=argparse.FileType('r'))
    cli.add_argument("-f", "--filter", dest="filter", required=False, default=5, type=int,
                     help="remove frequency less than the value")
    args = cli.parse_args()
    freq_list, coverage = read_frequency_list(fd_freq=args.fd_freq, filter_less=args.filter)
    sim, (c, s), pval, r2, r2adj = pdf_fitting(freq_list)
    ks_d, ks_pval = ks_2samp(sim, freq_list)
    print(f"Fitting result: \n"
          f"\tExpression: {c} + {s} * log(r)\n"
          f"\tCoverage: {coverage}\n"
          f"\tp-value: {pval}\n"
          f"\tR^2: {r2}\n"
          f"\tR^2 adj.: {r2adj}\n"
          f"\tKS_D: {ks_d}\n"
          f"\tKS_p-value: {ks_pval}")
    pass


if __name__ == '__main__':
    wrapper()
