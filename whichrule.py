"""
hashcat --debug-mode 3 or 4 will output origin-word and corresponding rule,
this code is to count how many passwords are cracked by a rule
"""
import re
from typing import TextIO


def read_debug(hashcat_debug: TextIO, mode: int):
    if mode == 3:
        re_find_rule = re.compile(r".+:(.+):.+")
        for line in hashcat_debug:
            line = line.strip("\r\n")
            rules = re_find_rule.findall(line)
            pass
    elif mode == 4:
        for line in hashcat_debug:
            pass
    else:
        raise Exception("Receive 3 or 4 only")
    pass


if __name__ == '__main__':
    test = "hell:$1:he:0:llo"
    find_rule = re.compile(r"(:.+:)")
    for fff in find_rule.findall(test):
        print(fff)
        # print(fff.group())
        pass
