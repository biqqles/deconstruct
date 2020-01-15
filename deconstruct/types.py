"""
 Copyright (C) 2019, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This module defines Python types representing C data types, for use
 in Structs.
"""
import ctypes
from functools import reduce
from operator import mul
from typing import Any, List
from .meta import ArrayLengthSpecifiable, classproperty
from .struct import TypeWidth


class CType(metaclass=ArrayLengthSpecifiable):
    """A type representing a C data type supported by the built-in struct module.

    Subclasses should:
        a) additionally subclass a Python builtin type*, and
        b) define a format character as defined in <https://docs.python.org/3/library/struct.html#format-strings>.

        * When a class which subclasses Struct is instantiated, these types are replaced by this
          built-in type in the resulting instance. This therefore assists with type hinting.
    """
    type_code: str
    native_only: bool = False

    @classmethod
    def format_string(cls, type_width: TypeWidth) -> str:
        """Form a struct.py-compliant format string comprising of the length and type code."""
        assert cls.type_code
        if cls.native_only and type_width is not TypeWidth.NATIVE:
            raise TypeError(f"'{cls.__name__}' can only be used in Structs using '{TypeWidth.NATIVE}'")
        return f'{cls.length}{cls.type_code}'

    @classmethod
    def value_of(cls, unpacked: Any):
        """Subclasses may override this method to define special conversion logic (after unpacking) if required."""
        return unpacked

    @classproperty
    def length(cls):
        """The total length of this array, calculated by the product of its lengths in each dimension."""
        return reduce(mul, cls.dimensions, 1)


class StdInt(int, CType):
    """A type representing a fixed-width integer type from <stdint.h>."""
    native_type_code: str  # determined with ctypes

    @classmethod
    def format_string(cls, type_width: TypeWidth) -> str:
        """Form a struct.py-compliant format string comprising of the length and type code."""
        assert cls.native_type_code
        super().format_string(type_width)
        return f'{cls.length}{cls.native_type_code if type_width is TypeWidth.NATIVE else cls.type_code}'


class char(bytes, CType):
    type_code = 'c'

    @classmethod
    def value_of(cls, unpacked: List[bytes]):
        return b''.join(unpacked)

class schar(int, CType): type_code = 'b'

class uchar(schar): type_code = 'B'

class short(int, CType): type_code = 'h'

class ushort(short): type_code = 'H'

class long(int, CType): type_code = 'l'

class ulong(long): type_code = 'L'

class longlong(int, CType): type_code = 'q'

class ulonglong(longlong): type_code = 'Q'

class double(float, CType): type_code = 'd'

# exact-width types from stdint

class int8(StdInt): type_code = schar.type_code; native_type_code = ctypes.c_int8._type_

class uint8(int8): type_code = uchar.type_code; native_type_code = ctypes.c_uint8._type_

class int16(StdInt): type_code = short.type_code; native_type_code = ctypes.c_int16._type_

class uint16(int16): type_code = ushort.type_code; native_type_code = ctypes.c_uint16._type_

class int32(StdInt): type_code = long.type_code; native_type_code = ctypes.c_int32._type_

class uint32(int32): type_code = ulong.type_code; native_type_code = ctypes.c_uint32._type_

class int64(StdInt): type_code = longlong.type_code; native_type_code = ctypes.c_int64._type_

class uint64(int64): type_code = ulonglong.type_code; native_type_code = ctypes.c_uint64._type_

# native-only types

class ssize(int, CType): type_code = 'n'; native_only = True

class size(int, CType): type_code = 'N'; native_only = True

class ptr(int, CType): type_code = 'P'; native_only = True

# types that shadow built-ins below here

class bool(int, CType): type_code = '?'  # bool can't be subclassed but it's just int in disguise anyway

class float(float, CType): type_code = 'f'

class int(int, CType): type_code = 'i'

class uint(int): type_code = 'I'

