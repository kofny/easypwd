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
    print(f"Make sure that you have installed statsmodels and scipy")
    sys.exit(-1)


def read_frequency_list(fd_freq: TextIO):
    freq_list = []
    for line in fd_freq:
        line = int(line.strip("\r\n"))
        freq_list.append(line)

    return freq_list


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
    args = cli.parse_args()
    freq_list = read_frequency_list(fd_freq=args.fd_freq)
    sim, (c, s), pval, r2, r2adj = pdf_fitting(freq_list)
    ks_d, ks_pval = ks_2samp(sim, freq_list)
    print(f"Fitting result: \n"
          f"\tExpression: {c} + {s} * log(r)\n"
          f"\tp-value: {pval}\n"
          f"\tR^2: {r2}\n"
          f"\tR^2 adj.: {r2adj}\n"
          f"\tKS_D: {ks_d}\n"
          f"\tKS_p-value: {ks_pval}")
    pass


if __name__ == '__main__':
    wrapper()
