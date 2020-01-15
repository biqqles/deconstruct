from setuptools import setup

setup(
    name='deconstruct',
    version='0.4',
    author='biqqles',
    author_email='biqqles@protonmail.com',
    description='Pythonic C-style structs for parsing binary data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/biqqles/deconstruct',
    packages=['deconstruct'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # uses the type annotation syntax defined in PEP 526
)
