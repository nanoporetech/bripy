OS := $(shell uname)
ifeq ($(OS), Darwin)
SEDI=sed -i '.bak'
else
SEDI=sed -i
endif


SAMVER=1.9
src/samtools-$(SAMVER)/Makefile:
	cd src; \
		curl -L -o samtools-${SAMVER}.tar.bz2 https://github.com/samtools/samtools/releases/download/${SAMVER}/samtools-${SAMVER}.tar.bz2; \
		tar -xjf samtools-${SAMVER}.tar.bz2; \
		rm samtools-${SAMVER}.tar.bz2


libhts.a: src/samtools-$(SAMVER)/Makefile
	# this is required only to add in -fpic so we can build python module
	@echo Compiling $(@F)
	cd src/samtools-${SAMVER}/htslib-${SAMVER}/ && CFLAGS=-fpic ./configure && make
	cp src/samtools-${SAMVER}/htslib-${SAMVER}/$@ $@


src/bri/Makefile:
	@echo Fetching bri
	cd src && git clone https://github.com/jts/bri.git


.PHONY: clean_htslib
clean_htslib:
	cd src/samtools-${SAMVER} && make clean || exit 0
	cd src/samtools-${SAMVER}/htslib-${SAMVER} && make clean || exit 0


venv: venv/bin/activate
IN_VENV=. ./venv/bin/activate

venv/bin/activate:
	test -d venv || virtualenv venv --python=python3 --prompt "(bripy) "
	${IN_VENV} && pip install pip --upgrade


.PHONY: develop
develop: venv libhts.a src/bri/Makefile
	${IN_VENV} && pip install -r requirements.txt
	${IN_VENV} && python setup.py develop


.PHONY: clean
clean:
	(${IN_VENV} && python setup.py clean) || echo "Failed to run setup.py clean"
	rm -rf src/samtools-${SAMVER} src/bri libhts.a libbripy.* venv build dist/ bripy.egg-info/ __pycache__
	find . -name '*.pyc' -delete


.PHONY: wheels
wheels:
	docker run -v `pwd`:/io quay.io/pypa/manylinux1_x86_64 /io/build-wheels.sh /io 5 6


.PHONY: build
build: pypi_build/bin/activate
IN_BUILD=. ./pypi_build/bin/activate
pypi_build/bin/activate:
	test -d pypi_build || virtualenv pypi_build --python=python3 --prompt "(pypi) "
	${IN_BUILD} && pip install pip --upgrade
	${IN_BUILD} && pip install --upgrade pip setuptools twine wheel readme_renderer[md]


.PHONY: sdist
sdist: pypi_build/bin/activate src/samtools-$(SAMVER)/Makefile src/bri/Makefile
	${IN_BUILD} && python setup.py sdist

