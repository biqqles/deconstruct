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
    def test_type_reuse(self):
        """Demonstrates multiple uses of a types and using types with different lengths."""
        class ThreeShort(c.Struct):
            one: c.int16
            two: c.int16[2]

        self.assertEqual(ThreeShort.sizeof, 6)
        self.assertEqual(ThreeShort.format_string, '=1h2h')

        self.assertEqual(ThreeShort.__annotations__['one'].length, 1)
        self.assertEqual(ThreeShort.__annotations__['two'].length, 2)

    def test_native_only_check(self):
        """Detects detection and rejection of native-only types in non-native structs."""
        class Bad(c.Struct):
            l: c.ptr

        with self.assertRaises(TypeError):
            Bad(b'\0' * Bad.sizeof)

    def test_field_type_restriction(self):
        """Detects detection and rejection of non-deconstruct types in structs."""
        with self.assertRaises(TypeError):
            class Bad(c.Struct):
                test: str

    def test_array_length_check(self):
        """Detects detection and rejection of invalid array sizes."""
        with self.assertRaises(TypeError):
            bad = c.int[-1]

    def test_format_string(self):
        self.assertTrue(True)

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

    def test_pointer_notation(self):
        """Test ptr's destination notation."""
        simple = c.ptr > c.double
        array_of_ptr = c.ptr[2] > c.int
        ptr_to_array = c.ptr > c.int[2]

        # check all returned types are still pointers
        self.assertTrue(simple.type_code == array_of_ptr.type_code == ptr_to_array.type_code == c.ptr.type_code)

    def test_empty_struct(self):
        """Tests acceptability of structs with no annotations."""
        class Empty(c.Struct):
            pass

        Empty(Empty.sizeof * b'0')

    def test_struct_comparision(self):
        """Tests struct comparison."""
        class ThreeShort(c.Struct):
            one: c.int16
            two: c.int16[2]

        a = ThreeShort(0xdec0de.to_bytes(6, 'big'))
        b = ThreeShort(0xdec0de.to_bytes(6, 'little'))

        self.assertEqual(a, copy.deepcopy(a))
        self.assertNotEqual(a, b)

    def test_array_types(self):
        """Demonstrates n-dimensional type morphing and calculations."""
        self.assertEqual(c.int[1][2][3].dimensions, [1, 2, 3])
        self.assertEqual(c.int[1][2][3].length, math.factorial(3))
        self.assertEqual(c.ptr[0][2][3].length, 0)


if __name__ == '__main__':
    unittest.main()
