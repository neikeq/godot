#!/usr/bin/python3

import argparse
import sys

# Whatever...
try:
    import run_msbuild
except:
    from . import run_msbuild


def generate_header(version_header_dst: str, deplist: [str]):
    import os

    latest_mtime = 0
    for filepath in deplist:
        mtime = os.path.getmtime(filepath)
        latest_mtime = mtime if mtime > latest_mtime else latest_mtime

    glue_version = int(latest_mtime)  # The latest modified time will do for now

    with open(version_header_dst, "w") as version_header:
        version_header.write("/* THIS FILE IS GENERATED DO NOT EDIT */\n")
        version_header.write("#ifndef CS_GLUE_VERSION_H\n")
        version_header.write("#define CS_GLUE_VERSION_H\n\n")
        version_header.write("#define CS_GLUE_VERSION UINT32_C(" + str(glue_version) + ")\n")
        version_header.write("\n#endif // CS_GLUE_VERSION_H\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate C# glue version header')

    run_msbuild.add_arguments_to_parser(parser)

    args = parser.parse_args()

    result = run_msbuild.run_msbuild_with_args(args)

    if result.exit_code != 0:
        sys.exit(result.exit_code)

    generate_header(args.stamp, result.deplist)
