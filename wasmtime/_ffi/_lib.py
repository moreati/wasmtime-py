import ctypes
import pathlib
import platform
import sys

if sys.maxsize <= 2**32:
    raise RuntimeError("wasmtime only works on 64-bit platforms right now")


def _platform() -> str:
    # For Python versions <=3.12. 3.13+ supports PEP 738 and uses sys.platform
    if hasattr(sys, 'getandroidapilevel'):
        return 'android'
    return sys.platform


def _libname() -> str:
    platform = _platform()
    if platform in ('linux', 'android'):
        return '_libwasmtime.so'
    if platform == 'win32':
        return '_wasmtime.dll'
    if platform == 'darwin':
        return '_libwasmtime.dylib'
    raise RuntimeError(f'unsupported platform `{platform}` for wasmtime')


def _machine() -> str:
    machine = platform.machine()
    if machine == 'AMD64':
        return 'x86_64'
    if machine in ('arm64', 'ARM64'):
        return 'aarch64'
    raise RuntimeError(f'unsupported architecture for wasmtime: {machine}')


filename = pathlib.Path(__file__).parent.parent / f'{_platform()}-{_machine()}' / f'{_libname()}'
dll = ctypes.cdll.LoadLibrary(str(filename))
