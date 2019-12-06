"""Bam read index in python."""

__version__ = '0.0.1-alpha.1'

import argparse

from libbripy import lib, ffi

def main():
    parser = argparse.ArgumentParser('bripy',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(
        title='subcommands', description='valid commands',
        help='additional help', dest='command')
    subparsers.required = True

    parser.add_argument('--version', action='version',
        version='%(prog)s {}'.format(__version__))

    p = subparsers.add_parser('index',
        help='Index a .bam file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('input_bam', help='Bam file to index.')
    p.set_defaults(func=bri_index)

    p = subparsers.add_parser('get',
        help='Get a read from a .bam file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('input_bam', help='Bam file to fetch read.')
    p.add_argument('read_name', help='Read name.')
    p.set_defaults(func=bri_get)

    args = parser.parse_args()
    args.func(args)


def bri_index(args):
    bri = lib.bam_read_idx_build(args.input_bam.encode())
    out_fn = lib.generate_index_filename(args.input_bam.encode())
    lib.bam_read_idx_save(bri, out_fn)
    lib.bam_read_idx_destroy(bri)


def bri_get(args):
    bri = BamReadIndex(args.input_bam)
    print(bri.get_alignments(args.read_name))


class BamReadIndex(object):
    def __init__(self, bam):
        self.bri = lib.bam_read_idx_load(bam.encode())
        self.bam_fp = lib.hts_open(bam.encode(), b"r")
        self.h = lib.sam_hdr_read(self.bam_fp)

    def get_alignments(self, read_name):
        p_start = ffi.new('bam_read_idx_record **')
        p_end = ffi.new('bam_read_idx_record **')

        lib.bam_read_idx_get_range(self.bri, read_name.encode(), p_start, p_end)
        b = lib.bam_init1()
        while p_start[0] != p_end[0]:
            lib.bam_read_idx_get_by_record(self.bam_fp, self.h, b, p_start[0])
            #TODO: we can do better than this
            string = ffi.new('kstring_t *')
            lib.sam_format1(self.h, b, string)
            data = ffi.string(string.s).decode()
            lib.ks_release(string)
            p_start[0] += 1
        lib.bam_destroy1(b)
        return data

    def __del__(self):
        lib.bam_hdr_destroy(self.h)
        lib.hts_close(self.bam_fp)
        lib.bam_read_idx_destroy(self.bri)

