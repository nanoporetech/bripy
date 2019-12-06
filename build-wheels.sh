#!/bin/bash
# Usage: ./build-wheels.sh <workdir> <pyminorversion1> <pyminorversion2> ...
set -e -x
export MANYLINUX=1

PACKAGE_NAME='bripy'

workdir=$1
shift

echo "Changing cwd to ${workdir}"
cd ${workdir}

yum install -y zlib-devel bzip2 bzip2-devel xz-devel curl-devel openssl-devel ncurses-devel git
rm -rf libhts.a 

# two patches for crusty gcc
make clean libhts.a src/bri/Makefile
sed -i 's/qsort_r(/sort_r_simple(/' src/bri//src/bri_index.c
sed -i '1s/^/#import "sort_r.h";/' src/bri//src/bri_index.c


# Compile wheels
for minor in $@; do
    PYBIN="/opt/python/cp3${minor}-cp3${minor}m/bin"
    # auditwheel/issues/102
    "${PYBIN}/pip" install --upgrade cffi setuptools pip wheel==0.31.1
    "${PYBIN}/pip" wheel . -w ./wheelhouse/
done


# Bundle external shared libraries into the wheels
for whl in "wheelhouse/${PACKAGE_NAME}"*.whl; do
    auditwheel repair "${whl}" -w ./wheelhouse/
done


# Install packages
for minor in $@; do
    PYBIN="/opt/python/cp3${minor}-cp3${minor}m/bin"
    "${PYBIN}/pip" install "${PACKAGE_NAME}" --no-index -f ./wheelhouse
    "${PYBIN}/bripy" index reads.bam
    "${PYBIN}/bripy" get reads.bam MINICOL242_20170206_FNFAE01663_MN18550_sequencing_throughput_DanS_E_coli_38212_ch155_read7024_strand 
done

cd wheelhouse && ls | grep -v "${PACKAGE_NAME}.*manylinux" | xargs rm
