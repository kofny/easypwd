# import matplotlib.pyplot as plt
# import matplotlib
#
# matplotlib.rcParams['pdf.fonttype'] = 42
#
# plt.rcParams['font.sans-serif'] = ['SimSun']
# plt.rcParams['axes.unicode_minus'] = False
#
# plt.plot([1], [1], label='您好')
#
# plt.legend()
# plt.savefig('this.pdf', font_number=0.1)

# from collections import defaultdict
#
# corpora = [
#     '/home/cw/Documents/Experiments/SegLab/Corpora632/youku-src.txt',
#     '/home/cw/Documents/Experiments/SegLab/Corpora632/dodonew-src.txt',
#     '/home/cw/Documents/Experiments/SegLab/Corpora632/rockyou-src.txt',
#     '/home/cw/Documents/Experiments/SegLab/Corpora632/webhost-src.txt',
# ]
#
# for corpus in corpora:
#     cls_dict = defaultdict(int)
#     all_cls_dict = defaultdict(int)
#     with open(corpus, 'r') as fin:
#         for line in fin:
#             line = line.strip('\r\n')
#             cls_lst = {"upper": 0, "lower": 0, "digit": 0, "other": 0}
#             for c in line:
#                 if c.isalpha():
#                     if c.isupper():
#                         cls_lst['upper'] = 1
#                     else:
#                         cls_lst['lower'] = 1
#                 elif c.isdigit():
#                     cls_lst["digit"] = 1
#                 else:
#                     cls_lst["other"] = 1
#                 pass
#             cls_num = sum(cls_lst.values())
#             has_digit = cls_lst['digit'] > 0
#             all_cls_dict[cls_num] += 1
#             if has_digit:
#                 cls_dict[cls_num] += 1
#         pass
#     for k in sorted(all_cls_dict.keys()):
#         with_digit = cls_dict[k]
#         total = all_cls_dict[k]
#         print(
#             f"Number Classes: {k}, with digits: {with_digit}, total = {total}, "
#             f"percentage = {with_digit / total * 100:5.2f}")
#         pass
import subprocess

# subprocess.run(['mv', '/home/cw/Codes/docs/cw-fduthesis/figures/MonteCarlo/csdn-cmp.pdf',
#                 '/home/cw/Codes/docs/cw-fduthesis/figures/MonteCarlo/csdn-cmp21.pdf'])
# subprocess.run(['ps2pdf', 'this.pdf',
#                 'that.pdf'])
subprocess.run(['rm', 'that.pdf'])
