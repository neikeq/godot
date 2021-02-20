#!/usr/bin/python3

import argparse
import subprocess
import sys
import os
import os.path
import shlex
from dataclasses import dataclass


@dataclass
class MSBuildResult:
    exit_code: int = 0
    deplist: [str] = None


@dataclass
class ToolsLocation:
    dotnet_cli: str = ''
    msbuild_standalone: str = ''
    msbuild_mono: str = ''
    mono_bin_dir: str = ''


def read_file_to_deplist(file: str) -> [str]:
    with open(file, 'r', encoding='utf-8-sig') as f:
        files = f.readlines()

    # Strip entries
    files = [f.strip() for f in files]
    # Remove empty entries
    files = filter(None, files)
    # Remove duplicate entries
    files = list(dict.fromkeys(files))

    return files


def deplist_to_rules(output: str, deplist: [str]) -> str:
    quoted_deplist = [f.replace(' ', r'\ ') for f in deplist]
    return '%s: %s\n' % (output, ' '.join(quoted_deplist))


def run_msbuild(tools: ToolsLocation, sln: str, depfile: str,
        stamp: str, targets: [str], msbuild_args: [str] = []) -> MSBuildResult:
    using_msbuild_mono = False

    # Preference order: dotnet CLI > Standalone MSBuild > Mono's MSBuild
    if tools.dotnet_cli:
        args = [tools.dotnet_cli, 'msbuild']
    elif tools.msbuild_standalone:
        args = [tools.msbuild_standalone]
    elif tools.msbuild_mono:
        args = [tools.msbuild_mono]
        using_msbuild_mono = True
    else:
        raise RuntimeError('Path to MSBuild or dotnet CLI not provided.')

    args += [sln]

    if depfile:
        deplist_file = os.path.abspath(depfile) + '.list.txt'
        targets += ['WriteMesonDepList']
        msbuild_args += ['/p:MesonDepListPath=' + deplist_file]

        if os.path.exists(deplist_file):
            os.remove(deplist_file) # Raises IsADirectoryError if depfile is a directory

    if len(targets) > 0:
        args += ['/t:' + ','.join(targets)]

    if len(msbuild_args) > 0:
        args += msbuild_args

    print('Running MSBuild: ', ' '.join(shlex.quote(arg) for arg in args), flush=True)

    result = MSBuildResult()

    msbuild_env = os.environ.copy()

    # Needed when running from Developer Command Prompt for VS
    if "PLATFORM" in msbuild_env:
        del msbuild_env["PLATFORM"]

    if using_msbuild_mono:
        # The (Csc/Vbc/Fsc)ToolExe environment variables are required when
        # building with Mono's MSBuild. They must point to the batch files
        # in Mono's bin directory to make sure they are executed with Mono.
        msbuild_env.update({
            "CscToolExe": os.path.join(tools.mono_bin_dir, "csc.bat"),
            "VbcToolExe": os.path.join(tools.mono_bin_dir, "vbc.bat"),
            "FscToolExe": os.path.join(tools.mono_bin_dir, "fsharpc.bat"),
        })

    result.exit_code = subprocess.call(args, env=msbuild_env)

    if depfile and result.exit_code == 0:
        result.deplist = read_file_to_deplist(deplist_file)

        deprules = deplist_to_rules(stamp, result.deplist)
        save = True

        if os.path.exists(depfile):
            with open(depfile, 'r') as f:
                prev_deprules = f.read()
                save = deprules.strip() != prev_deprules.strip()

        if save:
            with open(depfile, 'w') as f:
                f.write(deprules)

    return result


def run_msbuild_with_args(args) -> MSBuildResult:
    msbuild_args = args.msbuild_args or []
    targets = args.targets or []

    tools = ToolsLocation(
        dotnet_cli=args.tool_dotnet_cli or '',
        msbuild_standalone=args.tool_msbuild_standalone or '',
        msbuild_mono=args.tool_msbuild_mono or '',
        mono_bin_dir=args.mono_bin_dir or '')

    return run_msbuild(tools, args.solution, args.depfile, args.stamp, targets, msbuild_args)


# Only needed for the stamp file
def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def add_arguments_to_parser(parser: argparse.ArgumentParser):
    parser.add_argument('solution', type=str)
    parser.add_argument('--tool-dotnet-cli', type=str)
    parser.add_argument('--tool-msbuild-standalone', type=str)
    parser.add_argument('--tool-msbuild-mono', type=str)
    parser.add_argument('--mono-bin-dir', type=str)
    parser.add_argument('--depfile', type=str, required=True)
    # TODO: stamp is only a thing while we're stuck with https://github.com/mesonbuild/meson/issues/2320
    parser.add_argument('--stamp', type=str, required=True)
    parser.add_argument('--targets', nargs='+')
    parser.add_argument('msbuild_args', nargs=argparse.REMAINDER)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run MSBuild')

    add_arguments_to_parser(parser)

    args = parser.parse_args()

    result = run_msbuild_with_args(args)

    if result.exit_code == 0:
        touch(args.stamp)

    sys.exit(result.exit_code)
