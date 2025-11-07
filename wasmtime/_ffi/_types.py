import ctypes
import typing


class wasm_ref_t(ctypes.Structure):
    pass


class wasm_val_union(ctypes.Union):
    _fields_ = [
        ("i32", ctypes.c_int32),
        ("i64", ctypes.c_int64),
        ("f32", ctypes.c_float),
        ("f64", ctypes.c_double),
        ("ref", ctypes.POINTER(wasm_ref_t)),
    ]

    i32: int
    i64: int
    f32: float
    f64: float
    ref: "typing.Union[ctypes._Pointer[wasm_ref_t], None]"


class wasm_val_t(ctypes.Structure):
    _fields_ = [("kind", ctypes.c_uint8), ("of", wasm_val_union)]

    kind: int
    of: wasm_val_union
