from contextlib import contextmanager
import subprocess
import tempfile
import os
import shutil
from termcolor import colored


def log(*text):
    print(colored(" ".join(text), "green"))


@contextmanager
def temp_dir():
    d = tempfile.mkdtemp()
    try:
        yield d
    finally:
        shutil.rmtree(d)


@contextmanager
def mount(dev, mountpoint, opts=[]):
    subprocess.run(["mount"] + opts + [dev, mountpoint], check=True)
    try:
        yield
    finally:
        subprocess.run(["umount", mountpoint], check=True)


def write_to_file(filename, contents, newline=True):
    with open(filename, "w") as fi:
        fi.write(contents)
        if newline:
            fi.write("\n")


def replace_lines_matching(filename, replacements, newline=True):
    def maybe_replace(line):
        for k, v in replacements.items():
            if k in line:
                return v
        return line

    with open(filename, "r") as fi:
        lines = [li.strip() for li in fi.readlines()]
    with open(filename, "w") as fi:
        fi.write("\n".join(maybe_replace(line) for line in lines))
        if newline:
            fi.write("\n")


def get_part_uuid(dev):
    return (
        subprocess.check_output(["blkid", "-o", "value", "-s", "UUID", dev])
        .decode()
        .strip()
    )
