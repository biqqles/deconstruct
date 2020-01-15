"""
 Copyright (C) 2019, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This module contains the meta-programmatic magic that implements this
 package's special behaviour.
"""
import sys
from typing import Type, List


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
    dimensions: List[int] = []  # elements hold lengths in ascending dimensions

    def __getitem__(cls, length: int) -> Type:
        if length < 0:
            raise TypeError('Size of array cannot be negative')
        # create a new copy of cls with altered dimensions schema
        return type(cls.__name__, cls.__bases__, dict(cls.__dict__, dimensions=[*cls.dimensions, length]))


class OnlyCTypeFieldsPermitted(type):
    """Metaclass: once applied to a class, only permits fields of types which are defined in this module."""
    def __new__(mcs, name, bases, dict_):
        from .types import CType
        if bases:  # if class being created subclasses something - i.e. ignore base class
            annotations = dict_.setdefault('__annotations__', {})  # ensure class has annotations
            for field_name, field_type in annotations.items():
                if type(field_type) is str:  # evaluate string annotations
                    module_vars = vars(sys.modules[dict_['__module__']])
                    field_type = eval(field_type, dict(dict_, **module_vars))
                    annotations[field_name] = field_type
                if not issubclass(field_type, CType):
                    raise TypeError('Only types defined in this package can be used in Structs')
        return super().__new__(mcs, name, bases, dict_)
