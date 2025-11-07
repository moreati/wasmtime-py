import ctypes
import typing

from . import wasm_byte_vec_new_uninitialized
from . import wasm_byte_vec_t


def to_bytes(vec: wasm_byte_vec_t) -> bytearray:
    ty = ctypes.c_uint8 * vec.size
    return bytearray(ty.from_address(ctypes.addressof(vec.data.contents)))


def to_str(vec: wasm_byte_vec_t) -> str:
    return to_bytes(vec).decode("utf-8")


def to_str_raw(ptr: "ctypes._Pointer", size: int) -> str:
    return ctypes.string_at(ptr, size).decode("utf-8")


def str_to_capi(s: str) -> wasm_byte_vec_t:
    if not isinstance(s, str):
        raise TypeError("expected a string")
    return bytes_to_capi(s.encode("utf8"))


def bytes_to_capi(s: typing.Union[bytes, bytearray]) -> wasm_byte_vec_t:
    if not isinstance(s, (bytes, bytearray)):
        raise TypeError("expected bytes or bytearray")
    vec = wasm_byte_vec_t()

    wasm_byte_vec_new_uninitialized(ctypes.byref(vec), len(s))
    buf = (ctypes.c_uint8 * len(s)).from_buffer_copy(s)
    ctypes.memmove(vec.data, buf, len(s))
    return vec


def take_pointer(structure: ctypes._Pointer, field_name: str) -> ctypes._Pointer:
    """
    Moral equivalent of `mem::replace(&mut structure.field_name, NULL)`

    Ctypes explicitly documents "Surprises" which includes, for example:

            import ctypes

            class A(ctypes.Structure):
                _fields_ = [("x", ctypes.POINTER(ctypes.c_int))]

            x_p = ctypes.pointer(ctypes.c_int(3))
            a = A(x_p)
            x = a.x

            print(x.contents)
            a.x = None
            print(x.contents)

    This program will segfault on the second access. It turns out that `x = a.x`
    is still actually a pointer into the original structure, and `a.x`
    overwrites that field so accessing `x` later accesses null memory. This
    method is an attempt to work around this surprising behavior and actually
    read the field from a structure and replace it with null.

    I'll be honest I just sat through a 3 hour flight, a 5 hour layover, a 9
    hour flight, 1 hour train ride, and I'm sitting in a hotel lobby for
    another 5 hours. That's my state of mind writing this up, so please
    draw conclusions about this method as appropriate.
    """
    field = getattr(structure, field_name)
    assert isinstance(field, ctypes._Pointer)
    ret = ctypes.cast(ctypes.addressof(field.contents), ctypes.POINTER(field._type_))
    setattr(structure, field_name, None)
    return ret
