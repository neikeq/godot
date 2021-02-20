#!/usr/bin/python3

import argparse
import os.path
from glob import glob


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='List all the assemblies in the specified directory (not recursive)')
    parser.add_argument('directory', type=str)

    args = parser.parse_args()

    for assembly in glob(os.path.join(args.directory, "*.dll")):
        # Print file base name with extension
        print(os.path.basename(assembly))
