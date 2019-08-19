##   LICENSE
# Copyright (c) 2018-2019 Genome Research Ltd.
# Author: Cancer Genome Project cgphelp@sanger.ac.uk
#
#
# This file is part of vcf_flag_modifier.
#
# vcf_flag_modifier is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#    1. The usage of a range of years within a copyright statement contained within
#    this distribution should be interpreted as being equivalent to a list of years
#    including the first and last year specified and all consecutive years between
#    them. For example, a copyright statement that reads ‘Copyright (c) 2005, 2007-
#    2009, 2011-2012’ should be interpreted as being identical to a statement that
#    reads ‘Copyright (c) 2005, 2007, 2008, 2009, 2011, 2012’ and a copyright
#    statement that reads ‘Copyright (c) 2005-2012’ should be interpreted as being
#    identical to a statement that reads ‘Copyright (c) 2005, 2006, 2007, 2008,
#    2009, 2010, 2011, 2012’."
#
#

"""
Python module for methods reading/parsing VCF
"""
import os
import re
import gzip
import datetime

import vcfpy

base_vcf_process_key = "vcfProcessLog"
r_proc_key = re.compile(base_vcf_process_key)
base_vcf_process_log = "<InputVCF=<{}>,InputVCFSource=<{}>,InputVCFParam=<{}>>"


def bedline_2kv_alleles(line):
    """
    Receives a line in bed format (tsv, 0-based start). In the format
    contig\tstart\tstop line also contains allele changes as extra
    trailing columns:
    \tref_allele\talt_allele
    Returns a key->value pairing where the key is a tuple of contig,start,stop
    and value is a tuple of ref/alt change
    """
    if isinstance(line, bytes):
        line = line.decode("utf8")
    # line is (contig\tstart\tstop[\tref_allele\talt_allele]\n)
    split_items = line.strip().split("\t")
    return (
        (split_items[0], (str(int(split_items[1]) + 1)), split_items[2]),
        (split_items[3], split_items[4]),
    )


def bedline_2kv(line):
    """
    Receives a line in bed format (tsv, 0-based start). In the format
    contig\tstart\tstop
    Returns a key->value pairing where the key is a tuple of contig,start,stop
    and value is None
    """
    if isinstance(line, bytes):
        line = line.decode("utf8")
    # line is (contig\tstart\tstop[\tref_allele\talt_allele]\n)
    split_items = line.strip().split("\t")
    return (split_items[0], (str(int(split_items[1]) + 1)), split_items[2]), None


def get_last_vcf_process_index(header_lines, key_prefix):
    """
    Find all header lines matching the prefix key_prefix.
    Where they do match, find the greatest index, so we can increment
    when generating a new header line for this process.
    Returns greatest index found in the header key.
    """
    matching_head_keys = set(
        line.key
        for line in (
            line
            for line in header_lines
            if isinstance(line, vcfpy.header.HeaderLine)
            and line.key.startswith(key_prefix)
        )
    )
    # Now find the maximum indices of the keys found
    indices = [
        int(key_part[1])
        for key_part in (key.rsplit(".", 1) for key in matching_head_keys)
        if len(key_part) == 2 and key_part[1].isdigit
    ]
    if indices:
        return max(indices)
    else:
        return None


class VcfParse:
    """
    Class containing VCF parsing code
    """

    def __init__(self, vcfIn, vcfOut, run_script, arg_str, bedfile=None, alleles=False):
        self.vcfinname = os.path.basename(vcfIn)
        self.vcfin = vcfpy.Reader.from_path(vcfIn)
        self.vcfout = vcfOut
        self.bed = bedfile
        self.alleles = alleles
        self.flagremove = set()
        self.filters = dict()
        self.run_script = run_script
        self.arg_str = arg_str

    def print_header_flags(self):
        """
        Print the given dict of FILTER header lines.
        """
        for head in self.filters:
            print(
                "{}\t{}".format(
                    self.filters[head]["ID"], self.filters[head]["Description"]
                )
            )

    def get_header_flags(self):
        """
        Read VCF header, retaoin all FILTER header lines as a list of
        dicts. id = Filtername, description
        """
        reader = self.vcfin
        self.filters.update(
            (head_line.id, {"ID": head_line.id, "Description": head_line.description})
            for head_line in reader.header.get_lines("FILTER")
            if head_line.id != "PASS"
        )

    def check_filters_against_flaglist(self, flagremove):
        """
        Compare the list of flags to remove against the VCF header.
        Throw an exception if the flag is not in the FILTER headers.
        """
        for flag in flagremove:
            if flag not in self.filters:
                err = "Flag {} was not found in the header of the VCF file. Try running with the -t option to see a list of flags in the VCF file provided.".format(
                    flag
                )
                raise ValueError(err)
            else:
                self.flagremove.add(flag)

    def filter_variant(self, var_filters):
        """
        Remove self.flagremove filters from the passed filter list
        """
        new_filters = [x for x in var_filters if x not in self.flagremove]
        if not new_filters:
            new_filters = ["PASS"]

        return new_filters

    def get_process_header_line(self, existing_head):
        """
        Generates a new vcfProvcess header line for this process. 
        Uses the existing header to check whether we require an index
        and (UTC) date appended to the key
        """
        head_key = base_vcf_process_key
        index = get_last_vcf_process_index(existing_head.lines, head_key)
        # Test for key without date - gives all lines
        if index is not None and index > 0:
            now = datetime.datetime.utcnow()
            date_str = now.strftime("%Y%m%d")
            head_key += "_{}".format(date_str)
            # Test for key with current date to get precise index
            index = get_last_vcf_process_index(existing_head.lines, head_key)
            if index is None:
                index = 0
            head_key = head_key + "." + str(index + 1)
        new_process_line = vcfpy.HeaderLine(
            key=head_key,
            value=base_vcf_process_log.format(
                self.vcfinname, self.run_script, self.arg_str
            ),
        )
        return new_process_line

    def parse_bed_file(self):
        """
        Parse a bed file of locations into a dict
        """
        with gzip.open(self.bed, "r") if self.bed.endswith(".gz") else open(
            self.bed
        ) as bed_f:
            if self.alleles:
                return dict(map(bedline_2kv_alleles, bed_f))
            else:
                return dict(map(bedline_2kv, bed_f))

    def refilter_vcf(self):
        """
        Iterate through VCF records. Outputting a new VCF with
        requested filters removed.
        """
        reader = self.vcfin
        # Make a copy of the header
        writer_header = reader.header.copy()
        # Add a headerline to say this was refiltered with this tool
        process_head_line = self.get_process_header_line(writer_header)
        writer_header.add_line(process_head_line)
        writer = vcfpy.Writer.from_path(self.vcfout, writer_header)

        if self.bed:
            bed_dict = self.parse_bed_file()
            if self.alleles:
                for variant in reader:
                    key = (str(variant.CHROM), str(variant.POS), str(variant.POS))
                    if (
                        key in bed_dict
                        and variant.ALT[0].serialize() == bed_dict[key][1]
                        and variant.REF == bed_dict[key][0]
                    ):
                        variant.FILTER = self.filter_variant(variant.FILTER)
                    writer.write_record(variant)
            else:
                for variant in reader:
                    key = (str(variant.CHROM), str(variant.POS), str(variant.POS))
                    if key in bed_dict:
                        variant.FILTER = self.filter_variant(variant.FILTER)
                    writer.write_record(variant)
        else:
            for variant in reader:
                variant.FILTER = self.filter_variant(variant.FILTER)
                writer.write_record(variant)

        writer.close()
