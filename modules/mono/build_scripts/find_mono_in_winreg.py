#!/usr/bin/python3

import os
import platform

if os.name == "nt":
    import sys
    import winreg


def _reg_open_key(key, subkey):
    try:
        return winreg.OpenKey(key, subkey)
    except OSError:
        if platform.architecture()[0] == "32bit":
            bitness_sam = winreg.KEY_WOW64_64KEY
        else:
            bitness_sam = winreg.KEY_WOW64_32KEY
        return winreg.OpenKey(key, subkey, 0, winreg.KEY_READ | bitness_sam)


def _reg_open_key_bits(key, subkey, bits):
    sam = winreg.KEY_READ

    if platform.architecture()[0] == "32bit":
        if bits == "64":
            # Force 32bit process to search in 64bit registry
            sam |= winreg.KEY_WOW64_64KEY
    else:
        if bits == "32":
            # Force 64bit process to search in 32bit registry
            sam |= winreg.KEY_WOW64_32KEY

    return winreg.OpenKey(key, subkey, 0, sam)


def _find_mono_in_reg(subkey, bits):
    try:
        with _reg_open_key_bits(winreg.HKEY_LOCAL_MACHINE, subkey, bits) as hKey:
            value = winreg.QueryValueEx(hKey, "SdkInstallRoot")[0]
            return value
    except OSError:
        return None


def _find_mono_in_reg_old(subkey, bits):
    try:
        with _reg_open_key_bits(winreg.HKEY_LOCAL_MACHINE, subkey, bits) as hKey:
            default_clr = winreg.QueryValueEx(hKey, "DefaultCLR")[0]
            if default_clr:
                return _find_mono_in_reg(subkey + "\\" + default_clr, bits)
            return None
    except OSError:
        return None


def find_mono_root_dir(bits):
    root_dir = _find_mono_in_reg(r"SOFTWARE\Mono", bits)
    if root_dir is not None:
        return str(root_dir)
    root_dir = _find_mono_in_reg_old(r"SOFTWARE\Novell\Mono", bits)
    if root_dir is not None:
        return str(root_dir)
    return ""


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Attempts to find the Mono install directory in the Windows Registry')
    parser.add_argument('cpu_family', choices=['x86', 'x86_64'], type=str)

    args = parser.parse_args()

    res = find_mono_root_dir(bits='32' if args.cpu_family == 'x86' else '64')
    if res:
        print(res)
