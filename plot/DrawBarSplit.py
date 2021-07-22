from typing import List

import matplotlib.pyplot as plt
import numpy as np

plt.switch_backend('agg')

labels = [
    "CL_B",
    "$Neopets$  CL_P",
    "CL_F",
    "CL_B",
    "$Cit0day$   CL_P",
    "CL_F",
    "CL_B",
    "$Youku$     CL_P",
    "CL_F",
    "CL_B",
    "$178$         CL_P",
    "CL_F"
]

models = [
    # neopets
    [78273, 459568, 133818, 138039],
    [80409, 461318, 132062, 1004722],
    [82023, 456158, 128686, 137777],
    # cit0day
    [125077, 612544, 120446, 280449],
    [147153, 632120, 121348, 280807],
    [157076, 629200, 121186, 287611],
    # youku
    [22666, 841284, 172051, 993717],
    [28010, 854951, 173769, 1004722],
    [14899, 716419, 145423, 852270],
    # 178
    [2823, 114813, 47323, 118091],
    [5285, 115603, 47374, 118265],
    [1728, 109063, 44548, 111524]
]

base = [
    # neopets
    [66096, 437594, 126362, 134710],
    [70917, 439934, 109830, 46006],
    [53284, 304393, 67351, 105514],
    # cit0day
    [95533, 582586, 109874, 270456],
    [148984, 605459, 103998, 137766],
    [108325, 471554, 62722, 191462],
    # youku
    [15458, 822562, 163471, 981933],
    [25739, 675102, 92585, 390032],
    [3538, 191392, 45215, 380947],
    # 178
    [1819, 113470, 46462, 117604],
    [4921, 105699, 34047, 50715],
    [983, 39180, 28652, 63740]
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
        self.default_color = 'purple'
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
        cur_item.offset = 0
        cur_item.data += cur_offset
        four_subplots[idx].append(items[i])

        pass
    figure, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, sharey='row')
    figure.set_size_inches((6, 4.5))
    # figure.set_tight_layout(True)
    # figure.
    axes = (ax1, ax2, ax3, ax4)
    # print(ax[0])
    ends = [100000, 500000, 100000, 1000000]
    lims = [210000, 980000, 210000, 1070000]
    end_labels = [r'$10^{5}$', r'$5\times10^{5}$', r'$10^{5}$', r'$10^{6}$']
    legend = ["Leet", "Syllable", "Keyboard", "Date"]
    for i, each_subplot in enumerate(four_subplots):
        # axes[i].set_xscale('log')
        # print(axes[i].get_xticks())
        # axes[i].tick_params(axis='both', which='minor', length=0)
        axes[i].tick_params(axis='x', which='major', direction="in", labelsize=14)
        axes[i].tick_params(axis='y', which='major', length=0, labelsize=14)
        axes[i].minorticks_off()
        axes[i].set_xticks([0, ends[i]])
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
        axes[i].set_xlabel(f'{legend[i]}', fontsize=16)
        # axes[i].set_xticks([10000, 100000, 500000, 1000000, 1500000, 10000000])
    plt.subplots_adjust(hspace=0, wspace=0)
    # plt.close(figure)
    return handles, figure


font = {'family': 'serif',
        'style': 'italic',
        'weight': 'normal',
        'color': 'grey',
        'size': 16
        }


def main():
    # config=Config.from_arguments()
    legend = ["Leet", "Syllable", "Keyboard", "Date"]
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
    config.smooth()
    lists = config.parse_bar_item(index, index2)
    items, figure = plot_bar(lists)
    # 去除ticks
    # plt.tick_params(bottom=False, top=False, left=False, right=False)
    adjust = [-2, -2, -2] * (config.types // 3)
    plt.yticks(index + adjust, labels)
    # plt.xticks([])
    # plt.legend(handles=[items[0], items[2], items[4], items[6]], labels=config.labels, loc="best", prop={'size': 13})
    # plt.legend(handles=[items[0], items[1], items[2], items[3], items[4], items[5], items[6], items[7]],
    # labels=config.labels,loc="best")
    plt.savefig("./pattern-comparison.pdf", bbox_inches='tight')
    plt.close(figure)

    pass


def draw_legend():
    fig = plt.figure(figsize=(20, 1))
    fig.set_tight_layout(True)
    plt.barh([1], [0], color='grey',
             label="Both number (baseline model and CKL_model)")
    plt.barh([2], [0], color='red', label="Extra number (CKL_model)")
    legend = plt.legend(loc='center', fontsize=30, handlelength=2.0, handletextpad=0.1, frameon=False, labelspacing=0.2,
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
    plt.savefig("./comparison-legend.pdf", bbox_inches='tight')
    pass


if __name__ == '__main__':
    main()
    # draw_legend()

# Adjust layout to make room for the table:
# plt.subplots_adjust(left=0.2, bottom=0.2)
