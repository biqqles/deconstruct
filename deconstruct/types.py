"""
 Copyright (C) 2019 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This module defines Python analogues of C's data types for use in Structs.

 Todo: add support for stdint.
"""
from typing import Any, List
from .meta import ArrayLengthSpecifiable, classproperty


class CType(metaclass=ArrayLengthSpecifiable):
    """A type representing a C data type supported by the built-in struct module.

    Subclasses should:
        a) additionally subclass a Python builtin type*, and
        b) define a format character as defined in <https://docs.python.org/3/library/struct.html#format-strings>.

        * When a class which subclasses Struct is instantiated, these types are replaced by this
          built-in type in the resulting instance. This therefore assists with type hinting.

    Todo: consider backwards compatibility: it would be fairly trivial to backport this library to much earlier Python
     versions by overriding __new__ and incrementing some counter on each class definition
    """
    type_code: str
    length: int = 1

    @classproperty
    def format_string(cls) -> str:
        """Forms a struct.py-compliant format string comprising of the length and type code."""
        assert cls.type_code
        return f'{cls.length}{cls.type_code}'

    @classmethod
    def value_of(cls, unpacked: Any):
        """Subclasses may override this method to define special conversion logic (after unpacking) if required."""
        return unpacked


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

class ssize_t(int, CType): type_code = 'n'

class size_t(int, CType): type_code = 'N'

class ptr(int): type_code = 'P'

# types that shadow built-ins below here

class bool(int, CType): type_code = '?'  # bool can't be subclassed but it's just int in disguise anyway

class float(float, CType): type_code = 'f'

class int(int, CType): type_code = 'i'

class uint(int): type_code = 'I'

