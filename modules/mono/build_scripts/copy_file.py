#!/usr/bin/python3

import argparse
from shutil import copy2


# Only needed for the stamp file
def touch(path):
    import os
    with open(path, 'a'):
        os.utime(path, None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Prints the specified environment variable')
    parser.add_argument('src', type=str)
    parser.add_argument('dst', type=str)
    parser.add_argument('--stamp', type=str)

    args = parser.parse_args()

    # Only check if directory exists if copy fails

    try:
        copy2(args.src, args.dst)
    except (IOError, FileNotFoundError) as e:
        import errno
        if isinstance(e, IOError) and e.errno != errno.ENOENT:
            raise
        import os.path
        dst_dir = os.path.dirname(args.dst)
        if os.path.isdir(dst_dir):
            raise
        import os
        os.makedirs(dst_dir, exist_ok=True)
        copy2(args.src, args.dst)

    if args.stamp:
        touch(args.stamp)
