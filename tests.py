"""
 Copyright (C) 2019, 2020 biqqles.

 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.

 This file contains tests for deconstruct.
"""
import copy
import math
import unittest
import deconstruct as c

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        class ThreeShort(c.Struct):
            one: c.int16
            two: c.int16[2]
        cls.ThreeShort = ThreeShort

    def test_type_reuse(self):
        """Demonstrates multiple uses of a types and using types with different lengths."""
        self.assertEqual(self.ThreeShort.sizeof, 6)
        self.assertEqual(self.ThreeShort.format_string, '=1h2h')

        self.assertEqual(self.ThreeShort.__annotations__['one'].length, 1)
        self.assertEqual(self.ThreeShort.__annotations__['two'].length, 2)

    def test_array_types(self):
        """Demonstrates n-dimensional type morphing and calculations."""
        self.assertEqual(c.int[1][2][3].dimensions, [1, 2, 3])
        self.assertEqual(c.int[1][2][3].length, math.factorial(3))
        self.assertEqual(c.ptr[0][2][3].length, 0)

    def test_pointer_notation(self):
        """Tests ptr's destination notation."""
        simple = c.ptr > c.double
        array_of_ptr = c.ptr[2] > c.int
        ptr_to_array = c.ptr > c.int[2]

        # check all returned types are still pointers
        self.assertTrue(simple.type_code == array_of_ptr.type_code == ptr_to_array.type_code == c.ptr.type_code)

    def test_array_length_check(self):
        """Detects detection and rejection of invalid array sizes."""
        with self.assertRaises(TypeError):
            bad = c.int[-1]

    def test_native_only_check(self):
        """Detects detection and rejection of native-only types in non-native structs."""
        class Bad(c.Struct):
            l: c.ptr

        with self.assertRaises(TypeError):
            Bad(b'\0' * Bad.sizeof)

    def test_require(self):
        """Tests correct handling of the _require() method."""
        class Requirement(c.Struct):
            operand: c.uchar

            def _require(self) -> bool:
                return self.operand == 4

        Requirement(b'\4')
        with self.assertRaises(ValueError):
            Requirement(b'\0')

    def test_field_type_restriction(self):
        """Detects detection and rejection of non-deconstruct types in structs."""
        with self.assertRaises(TypeError):
            class Bad(c.Struct):
                test: str

    def test_inversion(self):
        """Tests struct inversion (conversion from and to bytes)."""
        class ComplexStruct(c.Struct):
            __type_width__ = c.TypeWidth.NATIVE
            a: c.int8[20][5][4]
            b: c.bool

        s = ComplexStruct(ComplexStruct.sizeof * b'@')
        self.assertEqual(s, ComplexStruct(s.to_bytes()))

    def test_future_annotations(self):
        """Tests struct definition using string (aka future) annotations."""
        class ThreeShort(c.Struct):
            one: 'c.int16'
            two: 'c.int16[2]'

        self.assertEqual(ThreeShort.format_string, '=1h2h')

    def test_empty_struct(self):
        """Tests acceptability of structs with no annotations."""
        class Empty(c.Struct):
            pass

        Empty(Empty.sizeof * b'0')

    def test_struct_comparison(self):
        """Tests struct comparison."""
        a = self.ThreeShort(0xdec0de.to_bytes(6, 'big'))
        b = self.ThreeShort(0xdec0de.to_bytes(6, 'little'))

        self.assertEqual(a, copy.deepcopy(a))
        self.assertNotEqual(a, b)

    def test_new(self):
        """Tests Struct.new."""
        new = self.ThreeShort.new(32_767, (0, -32_768))
        self.assertEqual(new.to_bytes(), b'\xff\x7f\x00\x00\x00\x80')

        # test insufficient arguments
        with self.assertRaises(AssertionError):
            self.ThreeShort.new(2)


if __name__ == '__main__':
    unittest.main()
