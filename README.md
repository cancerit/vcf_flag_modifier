# vcf_flag_modifier

Python utility to remove flags from a VCF file. IT can be used to filter a whole file or optionally only positions
in a bed file.

[![Quay Badge][quay-status]][quay-repo]

| Master                                        | Develop                                         |
| --------------------------------------------- | ----------------------------------------------- |
| [![Master Badge][travis-master]][travis-base] | [![Develop Badge][travis-develop]][travis-base] |

Contents:
<!-- TOC depthFrom:2 -->

- [Docker, Singularity and Dockstore](#docker-singularity-and-dockstore)
- [Dependencies/Install](#dependenciesinstall)
  - [Package Dependencies](#package-dependencies)
  - [Installation](#installation)
- [Usage](#usage)
- [Development Environment](#development-environment)
  - [Setup VirtualEnv](#setup-virtualenv)
  - [Testing/Coverage (`./run_tests.sh`)](#testingcoverage-runtestssh)
- [Cutting a Release](#cutting-a-release)
- [Creating a release](#creating-a-release)
  - [Preparation](#preparation)
  - [Release process](#release-process)
    - [Code changes](#code-changes)
    - [Docker image](#docker-image)
    - [Cutting the release](#cutting-the-release)
- [LICENCE](#licence)

<!-- /TOC -->

## Docker, Singularity and Dockstore

There is a pre-built images containing this codebase on quay.io.
The docker image is known to work correctly after import into a singularity image.

## Dependencies/Install

### Package Dependencies

`pip` will install the relevant python dependancies, listed here for convenience:

- [vcfpy](https://pypi.org/project/vcfpy/)


### Installation

__Assuming setup of virtualenv as per [Setup VirtualEnv](#setup-virtualenv)__

```bash
git clone vcf_flag_modifier
source venv/bin/activate # if not already in venv
python setup.py install
python flag_modifier.py -h
```


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

## Development Environment

This project uses git pre-commit hooks. As these will execute on your system it is entirely up to you if you activate them.
If you want tests, coverage reports and lint-ing to automatically execute before a commit you can activate them by running:

```bash
git config core.hooksPath git-hooks
```

Only a test failure will block a commit, lint-ing is not enforced (but please consider following the guidance).

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

## Cutting a Release

__Ensure you increment the version number in `setup.py`__

## Creating a release

### Preparation

* Commit/push all relevant changes.
* Pull a clean version of the repo and use this for the following steps.

### Release process

This project is maintained using HubFlow.

#### Code changes

1. Make appropriate changes
2. Update `setup.py` to the correct version (adding rc/beta to end if applicable).
3. Update `CHANGES.md` to show major items.
4. Check all tests and coverage reports are acceptable.
5. Commit the updated docs and updated module/version.
6. Push commits.

#### Docker image

1. Use the GitHub tools to draft a release.
2. Build image locally
3. Run example inputs and verify any changes are acceptable
4. Bump version in `Dockerfile`
5. Push changes

#### Cutting the release

1. Check state on Travis
2. Generate the release (add notes to GitHub)
3. Confirm that image has been built on [quay.io][quay-builds]

## LICENCE

Copyright (c) 2018-2019 Genome Research Ltd.

Author: CancerIT <cgphelp@sanger.ac.uk>

This file is part of vcf_flag_modifier.

vcf_flag_modifier is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

<!-- Travis -->
[travis-base]: https://travis-ci.org/cancerit/vcf_flag_modifier
[travis-master]: https://travis-ci.org/cancerit/vcf_flag_modifier.svg?branch=master
[travis-develop]: https://travis-ci.org/cancerit/vcf_flag_modifier.svg?branch=dev

<!-- Quay.io -->
[quay-status]: https://quay.io/repository/wtsicgp/vcf_flag_modifier/status
[quay-repo]: https://quay.io/repository/wtsicgp/vcf_flag_modifier
[quay-builds]: https://quay.io/repository/wtsicgp/vcf_flag_modifier?tab=builds


