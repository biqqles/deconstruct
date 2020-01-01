"""
 Copyright (C) 2019, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
import struct
from enum import Enum
from itertools import chain
from typing import Any, List
from .meta import OnlyCTypeFieldsPermitted, classproperty


class ByteOrder(Enum):
    NATIVE = '='
    BIG_ENDIAN = '>'
    LITTLE_ENDIAN = '<'


class TypeWidth(Enum):
    NATIVE = '@'
    STANDARD = ''


class Struct(metaclass=OnlyCTypeFieldsPermitted):
    __byte_order__: ByteOrder = ByteOrder.NATIVE
    __type_width__: TypeWidth = TypeWidth.STANDARD

    def __init__(self, buffer: bytes):
        """On instantiation, unpack the provided buffer and replace instance fields with their respective values."""
        # instantiating this class directly is nonsensical; it must be subclassed to be used
        if self.__class__ is Struct:
            raise TypeError('This class must be subclassed to be used')

        # TypeWidth.NATIVE can only be used with ByteOrder.NATIVE
        if (self.__type_width__ is TypeWidth.NATIVE) and (self.__byte_order__ is not ByteOrder.NATIVE):
            raise AttributeError('Native type widths cannot be used with non-native byte order. This is a limitation of'
                                 ' Python\'s struct')

        # unpack buffer
        unpacked: List[Any] = list(reversed(struct.unpack(self.format_string, buffer)))

        # and set fields
        for field_name, field_type in self.__annotations__.items():  # type: str, 'CType'
            if field_type.length > 1:
                field_value = tuple(unpacked.pop() for i in range(field_type.length))
            else:
                field_value = unpacked.pop()
            setattr(self, field_name, field_type.value_of(field_value))

    def __repr__(self) -> str:
        """Return a textual representation of this struct instance."""
        return f'struct {type(self).__name__} [{self.__byte_order__}, {self.__type_width__}] {{\n' + \
            '\n'.join(f'    {n}: {t.__name__} = {getattr(self, n)}' for n, t in self.__annotations__.items()) + \
            '\n}'

    def to_bytes(self) -> bytes:
        """Return the in-memory (packed) representation of this struct instance."""
        attr_values = [getattr(self, name) for name in self.__annotations__]
        flat_values = chain(*(v if isinstance(v, tuple) else [v] for v in attr_values))  # flatten arrays for packing
        return struct.pack(self.format_string, *flat_values)

    @classproperty
    def format_string(cls) -> str:
        """A struct.py-compatible format string, calculated from this struct's definition.
        This works because, according to the source for dataclasses.py in the standard library, __annotations__ "is
        guaranteed to be ordered" (thanks to the new dict implementation in Python 3.6)."""
        prefix = cls.__type_width__.value or cls.__byte_order__.value
        return prefix + ''.join(t.format_string(cls.__type_width__) for t in cls.__annotations__.values())

    @classproperty
    def sizeof(cls) -> int:
        """The total size in bytes of the struct. Equivalent to C's sizeof."""
        return struct.calcsize(cls.format_string)
