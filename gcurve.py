"""
Easy toolkit for Guess-Crack Curve
Note that this method need support of matplotlib, make sure that you have installed it.
"""
import sys
from typing import TextIO, List, Tuple


class File:
    def __init__(self, tag: str, file: TextIO, col: int = 0, splitter: str = "\t"):
        self.tag = tag
        self.file = file
        self.col = col
        self.splitter = splitter

    pass


class FileGroup:
    def __init__(self, group_tag, target: TextIO, stat_files: List[File]):
        """

        :param group_tag: tag for this group of files
        :param target: testing set
        :param stat_files: cracked passwords, in format shown in TargetStat.cpp
        """

        self.group_tag = group_tag
        self.target = target
        self.stat_files = stat_files

    pass


def read_cfg(cfg_file: TextIO):
    pass


def main():
    argv = sys.argv

    pass
