"""
 Copyright (C) 2019 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This module contains the meta-programmatic magic that implements this
 package's special behaviour.
"""
from typing import Type


class classproperty:
    """A class property decorator, similar to the builtin @classmethod."""
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        return self.fget(owner)


class ArrayLengthSpecifiable(type):
    """Metaclass: repurposes square-bracket syntax to allow the definition of fixed-size N-D arrays of a type - just
    like in C! (Though strictly speaking the syntax is more like C#'s.)
    E.g. char[10].length == 10; int[5][5].length == 25."""
    length: int = 1

    def __getitem__(cls, length: int) -> Type:
        if length < 1:
            raise TypeError('Arrays of length < 1 are not permitted')
        # create a new copy of cls with altered length - the product of antecedents' lengths
        return type(cls.__name__, cls.__bases__, dict(cls.__dict__, length=(cls.length * length)))


class OnlyCTypeFieldsPermitted(type):
    """Metaclass: once applied to a class, only permits fields of types which are defined in this module."""
    def __new__(mcs, name, bases, dict_):
        if bases:  # if class being created subclasses something - i.e. ignore base class
            from .types import CType
            for field_type in dict_['__annotations__'].values():
                if not issubclass(field_type, CType):
                    raise TypeError('Only types defined in this package can be used in Structs')
        return super().__new__(mcs, name, bases, dict_)
