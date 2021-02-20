#!/usr/bin/python3

import argparse
from os import environ


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Prints the specified environment variable')
    parser.add_argument('var_name', type=str)

    args = parser.parse_args()

    print(environ[args.var_name])
