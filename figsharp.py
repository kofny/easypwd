"""
Reduce the size of pdf figures
"""
import os
import sys
import subprocess


def sharp(root_folder: str):
    for root, dirs, files in os.walk(root_folder):
        for name in files:
            real_name = os.path.join(root, name)
            print(f"Parsing {real_name}...", end='', flush=True, file=sys.stderr)
            subprocess.run(['ps2pdf', real_name, real_name], shell=True)
            print(f"Done", file=sys.stderr, flush=True)
            pass
        pass


def wrapper():
    figure_folder = 'figures'
    sharp(figure_folder)
    pass
