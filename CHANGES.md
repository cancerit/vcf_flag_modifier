# CHANGES

## 1.2.2

* Use vcfpy version 1.13.0 which fixes the problem when writing colons in the INFO field

## 1.2.1

* Fix to version code

## 1.2.0

* First github release
* Includes Dockerfile
* Travis testing for Docker image added
* Use [vcfpy](https://vcfpy.readthedocs.io/en/stable/) rather than cyvcf2

## 1.1.0

* Changed to use vcfpy. Minor loss in performance, much easier install
* Added ability to filter using a bed file of positions
* Bed file of positions can also include specific allele changes

## 1.0.1

* Downgrade cyvcf2 to 0.9.0 to remove installation errors

## 1.0.0

* First release - simply runs over a whole VCF file
