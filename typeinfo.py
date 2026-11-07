
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


# signed integer types
from ctypes import c_int8 as i8
from ctypes import c_int16 as i16
from ctypes import c_int32 as i32
from ctypes import c_int64 as i64

# unsigned integer types
from ctypes import c_uint8 as u8
from ctypes import c_uint16 as u16
from ctypes import c_uint32 as u32
from ctypes import c_uint64 as u64

# floating point types
from ctypes import c_float as f32
from ctypes import c_double as f64

# boolean type
from ctypes import c_bool as u1

# char type
from ctypes import c_char as char

# void*
from ctypes import c_void_p as void_ptr




# Assembly pneumonic generation, interpreter actions...your pick
class IBackendImplementation(ABC):
    @abstractmethod
    def generate(self, *args, **kwargs):
        pass

class TACGenerator(IBackendImplementation):
    def __init__(self, template: str):
        self.template = template
    def __call__(self, *args, **kwargs):
        return self.template.format(*args, **kwargs)

@dataclass
class MemberNode:
    name: str
    type: 'TypeMetadata'
    offset: int = 0


@dataclass
class TypeMetadata:
    type_name: str
    size_bytes: int | None = None
    padding_bytes: int | None = None
    alignment_bytes: int | None = None

    members: dict[str, MemberNode] = field(default_factory=dict)
    operators: dict[str, IBackendImplementation] = field(default_factory=dict)

base_operators = {
    # push to stack / ctor
    "push": TACGenerator('PUSH_{type} {count} {initial_value}'),
    "pop": TACGenerator('POP_{type} {count}'),
    "cast": TACGenerator('CAST_{src_type}_TO_{dest_type} {src} -> {dest}'),

}


# Intermediate representation of the type system, including primitive types and their associated metadata
integral_operators = {
    '+': TACGenerator('ADD_{type} {src1} {src2} -> {dest}'),
    '-': TACGenerator('SUB_{type} {src1} {src2} -> {dest}'),
    '*': TACGenerator('MUL_{type} {src1} {src2} -> {dest}'),
    '/': TACGenerator('DIV_{type} {src1} {src2} -> {dest}'),
    '%': TACGenerator('MOD_{type} {src1} {src2} -> {dest}'),
    '==': TACGenerator('EQ_{type}  {src1} {src2} -> {dest}'),
    '!=': TACGenerator('NE_{type}  {src1} {src2} -> {dest}'),
    '<': TACGenerator('LT_{type}  {src1} {src2} -> {dest}'),
    '<=': TACGenerator('LE_{type}  {src1} {src2} -> {dest}'),
    '>': TACGenerator('GT_{type}  {src1} {src2} -> {dest}'),
    '>=': TACGenerator('GE_{type}  {src1} {src2} -> {dest}'),
    "&": TACGenerator('AND_{type} {src1} {src2} -> {dest}'),
    "|": TACGenerator('OR_{type} {src1} {src2} -> {dest}'),
    "^": TACGenerator('XOR_{type} {src1} {src2} -> {dest}'),
    "<<": TACGenerator('SHL_{type} {src1} {src2} -> {dest}'),
    ">>": TACGenerator('SHR_{type} {src1} {src2} -> {dest}'),
    "~": TACGenerator('NOT_{type} {src1} -> {dest}'),
    "&&": TACGenerator('LAND_{type} {src1} {src2} -> {dest}'),
    "||": TACGenerator('LOR_{type} {src1} {src2} -> {dest}'),
    "!": TACGenerator('LNOT_{type} {src1} -> {dest}'),

    # Pushes an instance on the stack



    # casting

} + base_operators
# doesn't handle epsilon, NaN, or infinity
float_operators = {
    '+': TACGenerator('ADD_{type} {src1} {src2} -> {dest}'),
    '-': TACGenerator('SUB_{type} {src1} {src2} -> {dest}'),
    '*': TACGenerator('MUL_{type} {src1} {src2} -> {dest}'),
    '/': TACGenerator('DIV_{type} {src1} {src2} -> {dest}'),
    '==': TACGenerator('EQ_{type}  {src1} {src2} -> {dest}'),
    '!=': TACGenerator('NE_{type}  {src1} {src2} -> {dest}'),
    '<': TACGenerator('LT_{type}  {src1} {src2} -> {dest}'),
    '<=': TACGenerator('LE_{type}  {src1} {src2} -> {dest}'),
    '>': TACGenerator('GT_{type}  {src1} {src2} -> {dest}'),
    '>=': TACGenerator('GE_{type}  {src1} {src2} -> {dest}'),

} + base_operators

bool_operators = {
    '==': TACGenerator('EQ_{type}  {src1} {src2} -> {dest}'),
    '!=': TACGenerator('NE_{type}  {src1} {src2} -> {dest}'),
    '&&': TACGenerator('LAND_{type} {src1} {src2} -> {dest}'),
    '||': TACGenerator('LOR_{type} {src1} {src2} -> {dest}'),
    '!': TACGenerator('LNOT_{type} {src1} -> {dest}'),
}  + base_operators

T_ref_operators = base_operators


    





primitive_types = {
    'i8': TypeMetadata('i8', size_bytes=1, alignment_bytes=1, operators=integral_operators),
    'i16': TypeMetadata('i16', size_bytes=2, alignment_bytes=2, operators=integral_operators),
    'i32': TypeMetadata('i32', size_bytes=4, alignment_bytes=4, operators=integral_operators),
    'i64': TypeMetadata('i64', size_bytes=8, alignment_bytes=8, operators=integral_operators),
    'u8': TypeMetadata('u8', size_bytes=1, alignment_bytes=1, operators=integral_operators),
    'u16': TypeMetadata('u16', size_bytes=2, alignment_bytes=2, operators=integral_operators),
    'u32': TypeMetadata('u32', size_bytes=4, alignment_bytes=4, operators=integral_operators),
    'u64': TypeMetadata('u64', size_bytes=8, alignment_bytes=8, operators=integral_operators),
    'f32': TypeMetadata('f32', size_bytes=4, alignment_bytes=4, operators=float_operators),
    'f64': TypeMetadata('f64', size_bytes=8, alignment_bytes=8, operators=float_operators),
    'bool': TypeMetadata('bool', size_bytes=1, alignment_bytes=1, operators=bool_operators),
    'char': TypeMetadata('char', size_bytes=1, alignment_bytes=1, operators=integral_operators),
    'T&': TypeMetadata('T&', size_bytes=8, alignment_bytes=8, operators=T_ref_operators),  # Assuming 64-bit architecture for pointer size
}


