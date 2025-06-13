'''
Download and unpack a precompiled wasmtime shared library & C headers.
'''

import argparse
import io
import platform
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

# set to "dev" to download the latest or pick a tag from
# https://github.com/bytecodealliance/wasmtime/tags
WASMTIME_VERSION = "v33.0.0"


def main(platform, arch):
    is_zip = False
    version = WASMTIME_VERSION

    if arch == 'AMD64':
        arch = 'x86_64'
    if arch == 'arm64' or arch == 'ARM64':
        arch = 'aarch64'
    dirname = '{}-{}'.format(platform, arch)
    if platform == 'linux' or platform == 'musl':
        filename = 'wasmtime-{}-{}-{}-c-api.tar.xz'.format(version, arch, platform)
        libname = '_libwasmtime.so'
        dirname = 'linux-{}'.format(arch)
    elif platform == 'win32':
        filename = 'wasmtime-{}-{}-windows-c-api.zip'.format(version, arch)
        is_zip = True
        libname = '_wasmtime.dll'
    elif platform == 'mingw':
        filename = 'wasmtime-{}-{}-mingw-c-api.zip'.format(version, arch)
        is_zip = True
        libname = '_wasmtime.dll'
    elif platform == 'darwin':
        filename = 'wasmtime-{}-{}-macos-c-api.tar.xz'.format(version, arch)
        libname = '_libwasmtime.dylib'
    elif platform == 'android':
        filename = 'wasmtime-{}-{}-android-c-api.tar.xz'.format(version, arch)
        libname = '_libwasmtime.so'
        dirname = 'android-{}'.format(arch)
    else:
        raise RuntimeError("unknown platform: " + sys.platform)

    url = 'https://github.com/bytecodealliance/wasmtime/releases/download/{}/'.format(version)
    url += filename
    print('Download', url)
    dst = Path('wasmtime') / dirname / libname
    try:
        shutil.rmtree(dst.parent)
    except Exception:
        pass
    try:
        shutil.rmtree(Path('wasmtime/include'))
    except Exception:
        pass

    with urllib.request.urlopen(url) as f:
        contents = f.read()

    def final_loc(name):
        parts = name.split('include/')
        if '/min/' in name:
            return None
        elif len(parts) > 1 and name.endswith('.h'):
            return Path('wasmtime') / 'include' / parts[1]
        elif name.endswith('.dll') or name.endswith('.so') or name.endswith('.dylib'):
            if '-min.' in name:
                return None
            return dst
        else:
            return None

    if is_zip:
        t = zipfile.ZipFile(io.BytesIO(contents))
        for member in t.namelist():
            loc = final_loc(member)
            if not loc:
                continue
            loc.parent.mkdir(parents=True, exist_ok=True)
            print(f'{member} => {loc}')
            contents = t.read(member)
            with open(loc, "wb") as f:
                f.write(contents)
    else:
        t = tarfile.open(fileobj=io.BytesIO(contents))
        for member in t.getmembers():
            loc = final_loc(member.name)
            if not loc:
                continue
            loc.parent.mkdir(parents=True, exist_ok=True)
            print(f'{member.name} => {loc}')
            contents = t.extractfile(member).read()
            with open(loc, "wb") as f:
                f.write(contents)

    if not dst.exists():
        raise RuntimeError("failed to find dynamic library")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        'platform', default=sys.platform, nargs='?',
        help='Platform to download for (default: %(default)s)',
    )
    parser.add_argument(
        'arch', default=platform.machine(), nargs='?',
        help='Architecture to download for (default: %(default)s)',
    )
    args = parser.parse_args()

    main(args.platform, args.arch)
