#!/usr/bin/python3

import argparse
import shutil
import sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Prints the file contents')
    parser.add_argument('file', type=str)

    args = parser.parse_args()

    with open(args.file, 'r') as file:
        shutil.copyfileobj(file, sys.stdout)
