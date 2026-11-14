import llvmlite.binding as llvm # type: ignore[import-not-found]
from llvmlite import ir
from typing import Any



class TypeTable(dict[str, ir.Type]):
    """ Maps a typename -> type"""

class FuncSigTable(dict[str, ir.FunctionType]):
    """ Maps a function signature (as a string) to its structured FunctionType"""

class FunctionTable(dict[ir.FunctionType, ir.Function]):
    """ Maps a function signature to its function module"""


compiler_primitive_types: TypeTable = TypeTable({
    "void": ir.VoidType(),

    "bool": ir.IntType(1),
    "char": ir.IntType(8),

    "i8": ir.IntType(8),
    "i16": ir.IntType(16),
    "i32": ir.IntType(32),
    "i64": ir.IntType(64),

    "u8": ir.IntType(8),
    "u16": ir.IntType(16),
    "u32": ir.IntType(32),
    "u64": ir.IntType(64),
    "f32": ir.FloatType(),
    "f64": ir.DoubleType(),

})


from __future__ import annotations
import ctypes
from _ctypes import _SimpleCData


interpreter_primitive_types: dict[str, Any] = {
    "bool": ctypes.c_bool,
    "char": ctypes.c_char,

    "i8": ctypes.c_int8,
    "i16": ctypes.c_int16,
    "i32": ctypes.c_int32,
    "i64": ctypes.c_int64,

    "u8": ctypes.c_uint8,
    "u16": ctypes.c_uint16,
    "u32": ctypes.c_uint32,
    "u64": ctypes.c_uint64,

    "f32": ctypes.c_float,
    "f64": ctypes.c_double,
}# e