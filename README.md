
![Oxford Nanopore Technologies logo](https://github.com/nanoporetech/medaka/raw/master/images/ONT_logo_590x106.png)


Bripy
======

Bripy is a python library for extracting reads from a bam by read name. It
uses the [bri](https://github.com/jts/bri) library from Jared Simpson.

© 2019 Oxford Nanopore Technologies Ltd.

Installation
------------

`bripy` can be installed using pip:

    pip install bripy

For python3.5 and python3.6 under linux this will download precompiled
binaries, in other environments a source distribution will be downloaded
and compiled. Compilation from source requires the same libraries as
[htslib](https://github.com/samtools/htslib):

    'm', 'z', 'lzma', 'bz2', 'pthread', 'curl', 'crypto'

since htslib is built from source as part of the process.

Usage
-----

The library contains a single class interface and two example programs. To
index a bam file for later retrieval of reads run:

    bripy index <bamfile>

This program is analogous to the `bri index <bamfile`. The second program
will retrieve reads from a bam by name:

    bripy get <bamfile> <read name>

Again this program is analogous to running `bri get <bamfile> <read name>`.

The `bripy` API is simple, the following will return a string containing
sam formatted alignments:

    bri = BamReadIndex(bam_file)
    sam_data = bri.get_alignments(read_name)

This API is likely to change in future to provide a more useful data structure
akin to a `pysam.AlignedSegment`.


License
-------

**Licence and Copyright**

© 2019 Oxford Nanopore Technologies Ltd.

`bripy` is distributed under the terms of the Mozilla Public License 2.0.

**Research Release**

Research releases are provided as technology demonstrators to provide early
access to features or stimulate Community development of tools. Support for
this software will be minimal and is only provided directly by the developers.
Feature requests, improvements, and discussions are welcome and can be
implemented by forking and pull requests. However much as we would
like to rectify every issue and piece of feedback users may have, the
developers may have limited resource for support of this software. Research
releases may be unstable and subject to rapid iteration by Oxford Nanopore
Technologies.
