import glob
import os

from cffi import FFI

#TODO: configure this better
samver="1.9"
htslib_dir = os.path.join('src', 'samtools-{}'.format(samver), 'htslib-{}'.format(samver))
brilib_dir = os.path.join('src', 'bri', 'src')

libraries=['m', 'z', 'lzma', 'bz2', 'pthread', 'curl', 'crypto']
library_dirs=[htslib_dir, brilib_dir]
src_dir='src'

bri_h = ['src/bri/src/bri_index.h', 'src/bri/src/bri_get.h']
bri_c = ['src/bri/src/bri_index.c', 'src/bri/src/bri_get.c']

headers = \
    '#include "htslib/sam.h"\n' + \
    '#include "htslib/kstring.h"\n' + \
    '\n'.join('#include "{}"'.format(os.path.basename(x)) for x in bri_h)

ffibuilder = FFI()
ffibuilder.set_source("libbripy",
    headers,
    libraries=libraries,
    library_dirs=library_dirs,
    include_dirs=[src_dir, htslib_dir, brilib_dir],
    sources=bri_c,
    extra_compile_args=['-std=c99', '-msse3', '-O3'],
    extra_objects=['libhts.a']
)

cdef = [
r"""

// basic htslib objects
typedef struct {
    ...;
} bam1_t;

typedef struct bam_hdr_t {
    ...;
} bam_hdr_t;
typedef bam_hdr_t sam_hdr_t;

typedef struct {
    ...;
} htsFile;
typedef htsFile samFile;

typedef struct __kstring_t {
    size_t l, m;
    char *s;
} kstring_t;
static inline char *ks_release(kstring_t *s);
int sam_format1(const bam_hdr_t *h, const bam1_t *b, kstring_t *str);

bam1_t* bam_init1();
void bam_destroy1(bam1_t* b);
htsFile *hts_open(const char *fn, const char *mode);
void hts_close(htsFile *);
bam_hdr_t *sam_hdr_read(samFile *fp);
static inline void bam_hdr_destroy(sam_hdr_t *h);
int sam_write1(htsFile *fp, const sam_hdr_t *h, const bam1_t *b);


// bam_read types
typedef struct bam_read_idx_record {
    ...;
} bam_read_idx_record;

typedef struct bam_read_idx {
    ...;
} bam_read_idx;

// from bri_index
bam_read_idx* bam_read_idx_build(const char* filename);
bam_read_idx* bam_read_idx_load(const char* input_bam);
void bam_read_idx_save(bam_read_idx* bri, const char* filename);
void bam_read_idx_destroy(bam_read_idx* bri);
char* generate_index_filename(const char* input_bam);

// from bri_get
void bam_read_idx_get_range(const bam_read_idx* bri, const char* readname, bam_read_idx_record** start, bam_read_idx_record** end);
void bam_read_idx_get_by_record(htsFile* fp, bam_hdr_t* hdr, bam1_t* b, bam_read_idx_record* bri_record);



"""
]
for header in []: #bri['h']:
    with open(header, 'r') as fh:
        cdef.append(fh.read())

ffibuilder.cdef('\n\n'.join(cdef))


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
