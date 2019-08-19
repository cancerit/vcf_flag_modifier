# vcf_flag_modifier

Python utility to remove flags from a VCF file. IT can be used to filter a whole file or optionally only positions
in a bed file.

<!-- TOC depthFrom:2 -->

- [Usage](#usage)
- [Package Dependencies](#package-dependencies)
- [Development Environment](#development-environment)
  - [Setup VirtualEnv](#setup-virtualenv)
  - [Testing/Coverage (`./run_tests.sh`)](#testingcoverage-runtestssh)
- [Installation](#installation)
- [Cutting a Release](#cutting-a-release)
- [LICENCE](#licence)

<!-- /TOC -->

## Usage

```bash
$ python vcf_flag_modifier.py -h
usage: vcf_flag_modifier.py [-h] -f input.vcf[.gz] [-o output.vcf]
                            [-b positions.bed[.gz]] [-a] [-t | -l UMV]

Modify a VCF file, removing provided flags.

optional arguments:
  -h, --help            show this help message and exit
  -f input.vcf[.gz], --vcfin input.vcf[.gz]
                        Path to input VCF file
  -o output.vcf, --vcfout output.vcf
                        path to write output VCF file
  -b positions.bed[.gz], --bedfile positions.bed[.gz]
                        Path to bed file of positions to consider for flag
                        modification Bed file can be `contig start stop` or
                        can include specific changes for each coordinate
                        `contig start stop ref alt`
  -a, --alleles         Path to bed file of positions to consider for flag
                        modification Bed file can be `contig start stop` or
                        can include specific changes for each coordinate
                        `contig start stop ref alt`
  -t, --listflags       Instead of modifying a VCF, list flags avaialble from
                        header
  -l UMV, --flagremove UMV
                        Flag(s) to remove from the passed VCF file
                        (repeatable)
```

## Package Dependencies

`pip` will install the relevant python dependancies, listed here for convenience:

- [vcfpy](https://pypi.org/project/vcfpy/)

## Development Environment

You can run checks manually without a commit by executing the following
in the base of the clone:

```bash
./run_all_tests.sh
```

### Setup VirtualEnv

```bash
cd $PROJECTROOT
hash virtualenv || pip3 install virtualenv
virtualenv -p python3 venv
source venv/bin/activate

python setup.py develop # so bin scripts can find module
```

### Testing/Coverage (`./run_tests.sh`)

```bash
source venv/bin/activate # if not already in venv
pip install pytest
pip install pytest-cov
run_tests.sh
```

## Installation

__Assuming setup of virtualenv as per [Setup VirtualEnv](#setup-virtualenv)__

```bash
git clone vcf_flag_modifier
source venv/bin/activate # if not already in venv
python setup.py install
python flag_modifier.py -h
```

## Cutting a Release

__Ensure you increment the version number in `setup.py`__

## LICENCE

Copyright (c) 2018-2019 Genome Research Ltd.

Author: CancerIT <cgpit@sanger.ac.uk>

This file is part of vcf_flag_modifier.

flag_modifier is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
