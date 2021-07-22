import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

import numpy as np
from typing import List

plt.switch_backend('agg')

labels = [

]

models = [
    # neopets
    [3303472, 1127997, 3858176, 3455],
    [2832232, 1001995, 2370278, 1856],
    [3291593, 1102460, 2344374, 899],
    # cit0day
    [4893697, 71199, 3858176, 1618],
    [5072655, 81216, 4035776, 1004],
    [5138174, 67236, 4099458, 722],
    # youku
    [4184321, 2252341, 3643166, 11463],
    [4251214, 2314692, 3709928, 10224],
    [3568508, 1702144, 3040416, 5454],
    # 178
    [623945, 248863, 443046, 483],
    [629257, 253793, 448414, 469],
    [578187, 210973, 398377, 344]
]

base = [
    # neopets
    [3119922, 1004179, 398377, 344],
    [3318192, 1131757, 2021464, 858],
    [2188543, 73096, 1413318, 0],
    # cit0day
    [4407439, 28377, 3414529, 202],
    [4550423, 129922, 3634608, 569],
    [3549848, 23751, 2739414, 0],
    # youku
    [4013278, 2115670, 3492161, 10229],
    [1831051, 1116799, 1574033, 4759],
    [1545840, 57235, 1177685, 23],
    # 178
    [605461, 235293, 425904, 470],
    [320416, 141640, 204665, 295],
    [320850, 9100, 175419, 2]
]


class CellItem:
    def __init__(self, index, data, bar_width, offset, color, hatch=None):
        self.index = index
        self.data = data
        self.bar_width = bar_width
        self.offset = offset
        self.color = color
        self.hatch = hatch


class Config:
    # Format of data and secondary(types X features): [model1:[1,2,3],model2:[4,5,6],model3:[7,8,9]]
    def __init__(self, feature=1, types=0, data=None, secondary=None, _labels=None):
        if _labels is None:
            _labels = []
        if secondary is None:
            secondary = []
        if data is None:
            data = []
        self.bar_width = 6
        self.feature = feature
        self.types = types
        self.data = data
        self.secondary = secondary
        # 每个特征的颜色
        # self.colors = ["royalblue", "green", "chocolate", "darkorchid"]
        self.colors = ["grey"] * 4
        # self.colors = plt.cm.BuPu(np.linspace(0, 0.5, self.feature))
        # 设置默认颜色
        self.default_color = 'grey'
        # 设置填充符号
        self.cover_hatch = "//"
        self.labels = _labels
        self.tick_direction = "out"
        # self.tick="none"
        self.validation()

    def validation(self):
        assert self.bar_width > 0
        assert self.feature > 0
        assert len(self.data) == self.types
        assert len(self.data) == len(self.secondary)
        # assert self.feature == len(self.labels)
        assert len(self.colors) >= self.feature

    def smooth(self, rate=6, threshold=60):
        data = self.data
        _base = self.secondary
        max_value = [max(row) for row in data]
        for rows in range(len(data) // 3):
            for i in range(len(data[0])):
                flag = False
                for j in range(rows * 3, rows * 3 + 3):
                    if max_value[j] / data[j][i] > threshold:
                        flag = True
                if flag:
                    print("Smooth ", i, ",", rows)
                    for j in range(rows * 3, rows * 3 + 3):
                        data[j][i] *= rate
                        _base[j][i] *= rate

    def parse_bar_item(self, index, index2=None) -> List[CellItem]:
        res = []
        if index2 is None:
            index2 = index
        for i in range(self.types):
            model = self.data[i]
            _base = self.secondary[i]
            offset = 0
            for j in range(self.feature):
                if model[j] <= _base[j]:
                    length = model[j]
                    res.append(CellItem(index[i], length, self.bar_width, offset, self.colors[j]))
                    offset += length
                    length = _base[j] - model[j]
                    res.append(
                        CellItem(index2[i], length, self.bar_width, offset, self.default_color, self.cover_hatch))
                    offset += length
                else:
                    length = _base[j]
                    res.append(CellItem(index[i], length, self.bar_width, offset, self.colors[j]))
                    offset += length
                    length = model[j] - _base[j]
                    res.append(CellItem(index2[i], length, self.bar_width, offset, self.colors[j], self.cover_hatch))
                    offset += length
        return res

    @staticmethod
    def from_arguments():
        return Config()


def plot_bar(items: List[CellItem]):
    handles = []
    plt.rcParams['hatch.linewidth'] = 1.3

    four_subplots = [[], [], [], []]
    for i in range(len(items), 0, -1):
        i -= 1
        idx = (i % 8) // 2
        pre_idx = i - (i % 2)
        base_item = items[pre_idx]
        cur_item = items[i]
        pre_offset = base_item.offset
        cur_offset = cur_item.offset
        cur_offset -= pre_offset
        # cur_item.offset = cur_offset
        cur_item.offset = 0
        cur_item.data += cur_offset
        four_subplots[idx].append(items[i])
        pass
    # figure, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, sharey=True)
    # figure.set_size_inches((6, 4.5))
    # figure.set_tight_layout(True)
    # figure.
    fig = plt.figure(figsize=(5.5, 4.5))
    sub_figs = fig.subfigures(1, 2)
    sub_left, sub_right = sub_figs[0], sub_figs[1]
    gs_left = gridspec.GridSpec(1, 2)
    gs_left.update(left=0, right=0.98, wspace=0)
    # gs_left.figure.
    ax1 = sub_left.add_subplot(gs_left[0, 0])
    ax2 = sub_left.add_subplot(gs_left[0, -1])
    gs_right = gridspec.GridSpec(1, 2)
    gs_right.update(left=0.02, right=1, wspace=0)
    ax3 = sub_right.add_subplot(gs_right[0, 0])
    ax4 = sub_right.add_subplot(gs_right[0, -1])
    sub_left.text(0.5, 0.006, "FLA", ha="center", fontsize=16)
    sub_right.text(0.5, 0.006, "zxcvbn", ha="center", fontsize=16)
    axes = (ax1, ax2, ax3, ax4)
    # print(ax[0])
    ends = [3000000, 1000000, 2000000, 7500]
    # lims = [5500000, 2500000, 4200000, 12000]
    lims = [5600000, 2600000, 4303000, 13000]
    end_labels = [r'$3\times10^{6}$', r'$10^{6}$', r'$2\times10^{6}$', r'$7.5\times10^{3}$']

    # legend = ["Medium", "Strong", "Medium", "Strong", "\n", "FLA", " " ,"zxcvbn"]
    # legend = ["Medium", " (FLA)", "Strong", "Medium", "(zxcvbn)", "Strong"]
    legend = ["Medium", "Strong", "Medium", "Strong"]

    for i, each_subplot in enumerate(four_subplots):
        # axes[i].set_xscale('log')
        # print(axes[i].get_xticks())
        # axes[i].tick_params(axis='both', which='minor', length=0)
        axes[i].tick_params(axis='x', which='major', direction="in", labelsize=14)
        axes[i].tick_params(axis='y', which='major', length=0, labelsize=13)
        axes[i].minorticks_off()
        axes[i].set_xticks([0, ends[i]])
        if i > 0:
            axes[i].set_yticks([])
        axes[i].set_xticklabels(['0', end_labels[i]])
        for j in range(len(each_subplot), 0, -1):
            j -= 1
            item = each_subplot[j]
            axes[i].barh([item.index], [item.data], item.bar_width, left=[item.offset],
                         color=item.color if item.hatch is None else "red",
                         hatch=None)
        pass

        print(axes[i].get_xlim())
        axes[i].set_xlim([0, lims[i]])
        wanted_legend = axes[i].barh([0], [0], 0)
        drew_legend = axes[i].legend([wanted_legend], [legend[i]], loc='lower right', fontsize=13, handlelength=0.0,
                                     handletextpad=0.0,
                                     frameon=False)
        drew_legend.get_frame().set_facecolor('none')
        # axes[i].set_xlabel(f'{legend[i]}', fontsize=16)
        # axes[i].set_xticks([10000, 100000, 500000, 1000000, 1500000, 10000000])
    # plt.subplots_adjust(hspace=0, wspace=0)
    # plt.close(figure)
    legend = ["Medium", "Strong", "Medium", "Strong"]
    # legend = ["Leet","Leet (CKL)","Syllable","Syllable(CKL)","Keyboard","Keyboard(CKL)","Date","Date(CKL)"]
    config = Config(4, 12, models, base, legend)
    index = np.arange(2 * config.types * config.bar_width, 0, -2 * config.bar_width)
    axes[0].set_yticks(index)
    axes[0].set_yticklabels(labels)
    return handles, fig


font = {'family': 'serif',
        'style': 'italic',
        'weight': 'normal',
        'color': 'grey',
        'size': 16
        }


def main():
    # config=Config.from_arguments()
    legend = ["Medium", "Strong", "Medium", "Strong"]
    # legend = ["Leet","Leet (CKL)","Syllable","Syllable(CKL)","Keyboard","Keyboard(CKL)","Date","Date(CKL)"]
    config = Config(4, 12, models, base, legend)
    factor = 1.5
    index = np.arange(factor * 2 * config.types * config.bar_width, 0,
                      factor * -1 * config.bar_width)
    # index2 = np.arange(factor * (2 * config.types - 1) * config.bar_width, 0, factor * -2 * config.bar_width)
    index2 = index[1::2]
    index = index[0::2]
    masks = [-2, 0, 2] * (config.types // 3)
    masks2 = [0.96, 2.96, 4.96] * (config.types // 3)
    index += masks
    index2 += masks2
    # plt.figure(figsize=(10.0, 4.5))
    plt.rcParams['ytick.direction'] = config.tick_direction
    plt.rcParams['xtick.direction'] = config.tick_direction
    # config.smooth()
    lists = config.parse_bar_item(index, index2)
    items, figure = plot_bar(lists)
    # 去除ticks
    # plt.tick_params(bottom=False, top=False, left=False, right=False)
    # plt.yticks(index, labels)
    # plt.xticks([])
    # plt.legend(handles=[items[0], items[2], items[4], items[6]], labels=config.labels, loc="best", prop={'size': 13})
    # plt.legend(handles=[items[0], items[1], items[2], items[3], items[4], items[5], items[6], items[7]],
    # labels=config.labels,loc="best")
    plt.savefig("strength-comparison.pdf", bbox_inches='tight')
    # plt.savefig("./save.pdf", bbox_inches='tight')
    # plt.show(bbox_inches="tight")
    plt.close(figure)

    pass


def draw_legend():
    fig = plt.figure(figsize=(20, 1))
    fig.set_tight_layout(True)
    plt.barh([1], [0], color='grey',
             label="Number (baseline model)")
    plt.barh([2], [0], color='red', label="Extra number (CKL_model)")
    legend = plt.legend(loc='center', fontsize=38, handlelength=2.0, handletextpad=0.1, frameon=False, labelspacing=0.1,
                        ncol=2)
    legend.get_frame().set_facecolor('none')
    ax = plt.gca()
    for direction in ['left', 'top', 'bottom', 'right']:
        ax.spines[direction].set_color('none')

    frame = plt.gca()
    # y 轴不可见
    frame.axes.get_yaxis().set_visible(False)
    # x 轴不可见
    frame.axes.get_xaxis().set_visible(False)
    plt.savefig("/disk/xm/auto-draw/figure/Bar/comparison-legend.pdf", bbox_inches='tight')
    pass


if __name__ == '__main__':
    main()
    # draw_legend()

# Adjust layout to make room for the table:
# plt.subplots_adjust(left=0.2, bottom=0.2)
