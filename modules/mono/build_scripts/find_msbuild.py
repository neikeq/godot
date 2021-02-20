#!/usr/bin/python3

import os
import os.path


def find_dotnet_cli():
    import os.path

    if os.name == "nt":
        for hint_dir in os.environ["PATH"].split(os.pathsep):
            hint_dir = hint_dir.strip('"')
            hint_path = os.path.join(hint_dir, "dotnet")
            if os.path.isfile(hint_path) and os.access(hint_path, os.X_OK):
                return hint_path
            if os.path.isfile(hint_path + ".exe") and os.access(hint_path + ".exe", os.X_OK):
                return hint_path + ".exe"
    else:
        for hint_dir in os.environ["PATH"].split(os.pathsep):
            hint_dir = hint_dir.strip('"')
            hint_path = os.path.join(hint_dir, "dotnet")
            if os.path.isfile(hint_path) and os.access(hint_path, os.X_OK):
                return hint_path


def find_msbuild_standalone_windows():
    msbuild_tools_path = find_msbuild_tools_path_reg()

    if msbuild_tools_path:
        return os.path.join(msbuild_tools_path, "MSBuild.exe")

    return None


def find_msbuild_mono_windows(mono_prefix):
    assert(mono_prefix is not None)

    mono_bin_dir = os.path.join(mono_prefix, "bin")
    msbuild_mono = os.path.join(mono_bin_dir, "msbuild.bat")

    if os.path.isfile(msbuild_mono):
        return msbuild_mono

    return None


def find_msbuild_mono_unix():
    import os.path
    import sys

    hint_dirs = []
    if sys.platform == "darwin":
        hint_dirs[:0] = [
            "/Library/Frameworks/Mono.framework/Versions/Current/bin",
            "/usr/local/var/homebrew/linked/mono/bin",
        ]

    for hint_dir in hint_dirs:
        hint_path = os.path.join(hint_dir, "msbuild")
        if os.path.isfile(hint_path):
            return hint_path
        elif os.path.isfile(hint_path + ".exe"):
            return hint_path + ".exe"

    for hint_dir in os.environ["PATH"].split(os.pathsep):
        hint_dir = hint_dir.strip('"')
        hint_path = os.path.join(hint_dir, "msbuild")
        if os.path.isfile(hint_path) and os.access(hint_path, os.X_OK):
            return hint_path
        if os.path.isfile(hint_path + ".exe") and os.access(hint_path + ".exe", os.X_OK):
            return hint_path + ".exe"

    return None


def find_msbuild_tools_path_reg():
    import subprocess

    vswhere = os.getenv("PROGRAMFILES(X86)")
    if not vswhere:
        vswhere = os.getenv("PROGRAMFILES")
    vswhere += r"\Microsoft Visual Studio\Installer\vswhere.exe"

    vswhere_args = ["-latest", "-products", "*", "-requires", "Microsoft.Component.MSBuild"]

    try:
        lines = subprocess.check_output([vswhere] + vswhere_args).splitlines()

        for line in lines:
            parts = line.decode("utf-8").split(":", 1)

            if len(parts) < 2 or parts[0] != "installationPath":
                continue

            val = parts[1].strip()

            if not val:
                raise ValueError("Value of `installationPath` entry is empty")

            # Since VS2019, the directory is simply named "Current"
            msbuild_dir = os.path.join(val, "MSBuild\\Current\\Bin")
            if os.path.isdir(msbuild_dir):
                return msbuild_dir

            # Directory name "15.0" is used in VS 2017
            return os.path.join(val, "MSBuild\\15.0\\Bin")

        raise ValueError("Cannot find `installationPath` entry")
    except ValueError as e:
        print("Error reading output from vswhere: " + e.message)
    except OSError:
        pass  # Fine, vswhere not found
    except (subprocess.CalledProcessError, OSError):
        pass


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='Prints the specified environment variable')
    parser.add_argument('tool', choices=['dotnet_cli', 'msbuild_standalone', 'msbuild_mono'], type=str)
    parser.add_argument('--mono-prefix', type=str)

    args = parser.parse_args()

    if args.tool == 'dotnet_cli':
        # Find dotnet CLI
        dotnet_cli = find_dotnet_cli()
        if dotnet_cli:
            print(dotnet_cli)
            sys.exit(0)
    elif args.tool == 'msbuild_standalone':
        # Find standalone MSBuild
        if os.name == "nt":
            msbuild_standalone = find_msbuild_standalone_windows()
            if msbuild_standalone:
                print(msbuild_standalone)
                sys.exit(0)
    else:
        assert(args.tool == 'msbuild_mono')

        if not args.mono_prefix:
            parser.error('\'--mono-prefix\' is required with \'--tool=msbuild_mono\'.')

        # Find Mono's MSBuild
        if os.name == "nt":
            msbuild_mono = find_msbuild_mono_windows(args.mono_prefix)
            if msbuild_mono:
                print(msbuild_mono)
                sys.exit(0)
        else:
            msbuild_mono = find_msbuild_mono_unix()
            if msbuild_mono:
                print(msbuild_mono)
                sys.exit(0)

    sys.exit(1)
