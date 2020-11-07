# deconstruct
**deconstruct** provides a Pythonic analogue of C's `struct`, primarily for the purpose of interpreting (i.e. _deconstructing_) contiguous binary data.
  
Internally, deconstruct uses Python's [struct module](https://docs.python.org/3/library/struct.html) and can be considered an abstraction of sorts. struct (the module) can be frustrating to use: its format strings appear arcane and furthermore separate the description of the data from its representation, a definite strength of C's struct.
  
In contrast, deconstruct allows structs to be defined and used using a syntax that is Pythonic while maintaining close correspondence to C.  
  
### Usage  
With deconstruct, the struct definition (adapted from [input.h](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input.h)):

```C
#include <stdint.h>

struct input_event {  
    uint64_t time[2];
    int16_t type;
    int16_t code;
    int32_t value;
};
```

can be represented as:

```Python
import deconstruct as c

class InputEvent(c.Struct):
    time: c.uint64[2]
    type: c.int16
    code: c.int16
    value: c.int32
```

This definition can be used to interpret and then access binary data:

```Python
>>> buffer = b'Some  arbitrary  buffer!'
>>> event = InputEvent(buffer)
>>> event.code
26229
>>> event.time
(8241904116577431379, 2340027244253309282)
>>> print(event)
struct InputEvent [ByteOrder.NATIVE, TypeWidth.STANDARD] {
    time: uint64 = (8241904116577431379, 2340027244253309282)
    type: int16 = 25120
    code: int16 = 26229
    value: int32 = 561145190
}
```

Of course, in reality the buffer passed in is more likely to come from something more useful, like a file. Notice that fixed-size, n-dimensional arrays can be specified using the syntax `type[length]`, a further improvement on Python's struct.

### Installation
deconstruct is now on PyPI:

```sh
pip install deconstruct
```

Alternatively you can install straight from this repository:

```sh
pip install https://github.com/biqqles/deconstruct/archive/master.zip
```

Built wheels are also available under [Releases](https://github.com/biqqles/deconstruct/releases), as is a changelog. The latest release is version 0.5.

deconstruct has no dependencies but requires Python >= 3.6 as it makes use of the class annotation syntax added in that release (see [PEP 526](https://www.python.org/dev/peps/pep-0526/)).

## API listing

### Struct(buffer: bytes)
Subclass this to define your own structs. Subclasses should only declare fields of C types defined in this package.

When you instantiate your Struct with a [bytes-like object](https://docs.python.org/3/glossary.html#term-bytes-like-object), deconstruct creates a format string and uses it to unpack that buffer. In the instance, C types will be replaced with their equivalent Python types for use (e.g. `bytes` for `char`, `int` for `schar` and `float` for `double`). All types available for use in struct field definitions and their details are documented in the table [below](#c-types).

#### Attributes
|Name            |Type       |Description   |
|----------------|-----------|--------------|
|`__byte_order__`|`ByteOrder`|Set this in your subclass definition to define the byte order used when unpacking the struct. One of:<ul><li>`ByteOrder.NATIVE` (default value)</li><li>`ByteOrder.BIG_ENDIAN`</li><li>`ByteOrder.LITTLE_ENDIAN`</li></ul>|
|`__type_width__`|`TypeWidth`|Set this in your subclass definition to define the type width and padding used for the struct. One of:<ul><li>`TypeWidth.NATIVE`</li><li>`TypeWidth.STANDARD` (default value)</li></ul>When `TypeWidth.NATIVE` is set, the struct will use native type widths and alignment. When `TypeWidth.STANDARD` is used, the struct will use Python's struct's "standard" widths<sup>[1](#f_st)</sup> and no padding.|

Note that `TypeWidth.NATIVE` can only be used with `ByteOrder.NATIVE`. This is a limitation of Python's struct.

#### Class methods
|Signature       |Return type|Description   |
|----------------|-----------|--------------|
|`new(*args)`    |`Struct`   |Construct a new struct instance with field values specified as positional arguments, passed in order of definition. Note that arguments are not type checked.|

#### Class properties
|Name            |Type       |Description   |
|----------------|-----------|--------------|
|`format_string` |`str`      |The struct.py-compatible format string for this struct|
|`sizeof`        |`int`      |The total size in bytes of the struct. Equivalent to C's `sizeof`|

#### Instance methods
|Signature       |Return type|Description   |
|----------------|-----------|--------------|
|`to_bytes()`    |`bytes`    |Returns the in-memory ("packed") representation of this struct instance|
|`_require()`    |`bool`     |Override this method to specify your own instance validation logic. This method is called each time the struct is initialised; a `ValueError` will be raised if it returns false.|

You can also `print` Struct instances for easier debugging and compare them using the `==` operator.

### C types
deconstruct defines the following special types for use in Struct definitions:<sup>[2](#f_ty)</sup>

|deconstruct type|C99 type            |Python format character|"Standard" width (bytes)<sup>[1](#f_st)</sup>|Resolves to Python type|
|----------------|--------------------|-----------------------|------------------------|--------------------------------------------|
|`char`          |`char`              |`c`                    |1                       |`bytes` of length 1                         |
|`schar`         |`signed char`       |`b`                    |1                       |`int`                                       |
|`uchar`         |`unsigned char`     |`B`                    |1                       |`int`                                       |
|`short`         |`short`             |`h`                    |2                       |`int`                                       |
|`ushort`        |`unsigned short`    |`H`                    |2                       |`int`                                       |
|`int`           |`int`               |`i`                    |2                       |`int`                                       |
|`uint`          |`unsigned int`      |`I`                    |2                       |`int`                                       |
|`long`          |`long`              |`l`                    |4                       |`int`                                       |
|`ulong`         |`unsigned long`     |`L`                    |4                       |`int`                                       |
|`longlong`      |`long long`         |`q`                    |8                       |`int`                                       |
|`ulonglong`     |`unsigned long long`|`Q`                    |8                       |`int`                                       |
|`bool`          |`bool` (`_Bool`)    |`?`                    |1                       |`bool`                                      |
|`float`         |`float`             |`f`                    |4                       |`float`                                     |
|`double`        |`double`            |`d`                    |8                       |`float`                                     |
|`int8`          |`int8_t`            |`b`*                   |1                       |`int`                                       |
|`uint8`         |`uint8_t`           |`B`*                   |1                       |`int`                                       |
|`int16`         |`int16_t`           |`h`*                   |2                       |`int`                                       |
|`uint16`        |`uint16_t`          |`H`*                   |2                       |`int`                                       |
|`int32`         |`int32_t`           |`l`*                   |4                       |`int`                                       |
|`uint32`        |`uint32_t`          |`L`*                   |4                       |`int`                                       |
|`int64`         |`int64_t`           |`q`*                   |8                       |`int`                                       |
|`uint64`        |`uint64_t`          |`Q`*                   |8                       |`int`                                       |
|`ptr`           |`void*`/`intptr_t`/`uintptr_t`|`P`          |N/A**                   |`int`                                       |
|`size`          |`size_t`            |`n`                    |N/A**                   |`int`                                       |
|`ssize`         |`ssize_t`           |`N`                    |N/A**                   |`int`                                       |

<sup>
* format character with <code>__type_width__ = TypeWidth.STANDARD</code> - platform specific otherwise.<br>
** only available with <code>__type_width__ = TypeWidth.NATIVE</code>.
</sup>

### Arrays
As mentioned earlier, all the types above support a `type[length]` syntax to define arrays. Multidimensional arrays work as you would expect, with `int[2][2]` declaring a 2-D array of type `int` and total length 4. When a Struct is used to unpack a buffer, each array will resolve to a tuple (or in the case of a multidimensional array, a nested tuple) of their equivalent Python types, as documented in the table above. The only exception to this is `char`, an array of which will be automatically concatenated to a single `bytes` object (if this behaviour is undesirable, use `schar` or `uchar` instead).

### Pointers
`ptr` uniquely supports an optional notation format using the `>` operator, allowing you to denote the type it points to. This notation is purely for programmer convenience - it, for example, has no effect on the size of the struct as all pointers are assumed to be of the size of `void*` (which is guaranteed to be able to hold any pointer).

To illustrate this syntax, `f: c.ptr > c.double` denotes a pointer to double (`double* f;`). Arrays of pointers *and* pointers to arrays are supported. For example, `c.ptr[2] > c.int` indicates an array of `int*`, while `c.ptr > c.int[2]` indicates a pointer to an `int` array.

You can also use `Struct` subtypes as the pointed-to type.

---

<b id="f_st">1.</b> Python's struct has the concept of "standard" type sizes. This is somewhat confusing coming from C as its standards go to some length not to define a standard ABI. However, as this terminology is so fundamental to the documentation of Python's struct it is replicated here for simplicity's sake. These sizes correspond with the *minimum* sizes [implied](https://en.wikipedia.org/wiki/C_data_types#Basic_types) for C's types.	

<b id="f_ty">2.</b> Because some of these conflict with Python's primitives, it is not recommended to `import * from deconstruct` as this will severely pollute your namespace (in fact this is a bad idea in general). I like to `import deconstruct as c` as shown above.
