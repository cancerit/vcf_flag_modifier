import pytest
import os
import collections
from pytest_mock import mocker

from vcfflagmodifier.VcfParse import VcfParse
from vcfflagmodifier.VcfParse import get_last_vcf_process_index
import vcfpy

input_vcf = "test_data/test_input.vcf.gz"
output_vcf = "test_data/test_output.vcf"
exp_output_vum_vcf = "test_data/test_exp_output.VUM.vcf"
exp_output_vum_mn_vcf = "test_data/test_exp_output.VUM_MN.vcf"
exp_output_vum_mn_bed_vcf = "test_data/test_exp_output.VUM_MN_bed.vcf"
exp_output_vum_mn_alleles_bed_vcf = "test_data/test_exp_output.VUM_MN_alleles_bed.vcf"
filter_pos_only_bed = "test_data/filter_locs_noallelechange.bed"
filter_pos_only_bed_zip = "test_data/filter_locs_noallelechange.bed.gz"
filter_alleles_bed = "test_data/filter_locs_allele.bed"
filter_alleles_bed_zip = "test_data/filter_locs_allele.bed.gz"


heads = list()
heads.append(
    vcfpy.FilterHeaderLine(
        "FILTER",
        '<ID=DTH,Description="Less than 1/3 mutant alleles were >= 25 base quality">',
        {
            "ID": "DTH",
            "Description": '"Less than 1/3 mutant alleles were >= 25 base quality"',
        },
    )
)
heads.append(
    vcfpy.FilterHeaderLine(
        "FILTER",
        '<ID=MQ,Description="Mean mapping quality of the mutant allele reads was < 21">',
        {
            "ID": "MQ",
            "Description": '"Mean mapping quality of the mutant allele reads was < 21"',
        },
    )
)

exp_head = {
    "MQ": {
        "Description": '"Mean mapping quality of the mutant allele reads was < 21"',
        "ID": "MQ",
    },
    "DTH": {
        "Description": '"Less than 1/3 mutant alleles were >= 25 base quality"',
        "ID": "DTH",
    },
}

run_script = "pytest_vcf_flag_modifier"
arg_str = "x=test_Arg_str"

EXP_LOCS = {
    ("1", "10438", "10438"): None,
    ("1", "10583", "10583"): None,
    ("1", "12719", "12719"): None,
    ("1", "13012", "13012"): None,
}

EXP_LOCS_ALL = {
    ("1", "10438", "10438"): ("T", "C"),
    ("1", "10583", "10583"): ("G", "A"),
    ("1", "12719", "12719"): ("G", "C"),
    ("1", "13012", "13012"): ("G", "A"),
}


def compare_variants(vcf1, vcf2):
    """
    Utility method for comparison of VCF variants in the cyvcf2 format
    """
    for var1, var2 in zip(vcf1, vcf2):
        assert var1.CHROM == var2.CHROM
        assert var1.POS == var2.POS
        assert var1.REF == var2.REF
        assert var1.ALT == var2.ALT
        assert var1.ID == var2.ID
        assert var1.QUAL == var2.QUAL
        assert var1.FILTER == var2.FILTER
        assert var1.FORMAT == var2.FORMAT
        assert dict(var1.INFO) == dict(var2.INFO)


def compare_vcf_header(vcf1, vcf2):
    """
    Utility method for comparison of VCF headers in the cyvcf2 format
    """
    # assert vcf1.header.lines == vcf2.header.lines

    assert list(vcf1.header.get_lines("contig")) == list(
        vcf2.header.get_lines("contig")
    )
    assert list(vcf1.header.get_lines("INFO")) == list(vcf2.header.get_lines("INFO"))
    assert list(vcf1.header.get_lines("FORMAT")) == list(
        vcf2.header.get_lines("FORMAT")
    )
    assert list(vcf1.header.get_lines("FILTER")) == list(
        vcf2.header.get_lines("FILTER")
    )


def compare_vcf_files(vcf_a, vcf_b):
    """
    Utility method for comparison of VCF files in the vcfpy format
    """
    if vcf_a == vcf_b:
        return True
    vcf1 = vcfpy.Reader.from_path(vcf_a)
    vcf2 = vcfpy.Reader.from_path(vcf_b)
    compare_vcf_header(vcf1, vcf2)
    compare_variants(vcf1, vcf2)
    return True


def test_get_header_flags(mocker):
    """
    Unit tests over the get_header_flags method
    """
    parser = VcfParse(input_vcf, output_vcf, run_script, arg_str)
    mock_vcf = mocker.patch("vcfpy.Reader")
    parser.vcfin = mock_vcf
    mock_vcf.header.get_lines.return_value = heads
    parser.get_header_flags()
    mock_vcf.header.get_lines.called_once()
    assert parser.filters == exp_head


def test_check_filters_against_flaglist(mocker):
    """
    Unit tests over the check_filters_against_flaglist method
    """
    # Try passing
    parser = VcfParse(input_vcf, output_vcf, run_script, arg_str)
    mock_vcf = mocker.patch("vcfpy.Reader")
    parser.vcfin = mock_vcf
    mock_vcf.header.get_lines.return_value = heads
    parser.get_header_flags()
    mock_vcf.header.get_lines.called_once()
    assert parser.filters == exp_head
    parser.check_filters_against_flaglist(["MQ"])
    assert parser.flagremove == {"MQ"}

    # Try multiple
    parser.check_filters_against_flaglist(["MQ", "DTH"])
    assert parser.flagremove == {"MQ", "DTH"}

    # Try multiple overwrite repeats
    parser.check_filters_against_flaglist(["MQ", "DTH", "MQ"])
    assert parser.flagremove == {"MQ", "DTH"}

    # Ensure error where flag not contained in header
    with pytest.raises(ValueError):
        parser.check_filters_against_flaglist(["VUM"])

    # Ensure exception where some pass, some fail
    with pytest.raises(ValueError):
        parser.check_filters_against_flaglist(["MQ", "DTH", "VUM"])


def test_filter_variant(mocker):
    """
    Unit tests over the filter_variant method
    """
    test_filters = ["VUM", "MQ", "DTH"]
    parser = VcfParse(input_vcf, output_vcf, run_script, arg_str)
    mock_vcf = mocker.patch("vcfpy.Reader")
    parser.vcfin = mock_vcf
    mock_vcf.header.get_lines.return_value = heads
    parser.get_header_flags()
    mock_vcf.header.get_lines.called_once()
    assert parser.filters == exp_head
    parser.check_filters_against_flaglist(["MQ", "DTH"])
    assert parser.flagremove == {"MQ", "DTH"}

    # Try one filter to PASS
    result = parser.filter_variant(["MQ"])
    assert result == ["PASS"]

    # Try multi, one filter left
    result = parser.filter_variant(test_filters)
    assert result == ["VUM"]

    # Try multi, multi filter left
    test_filters.append("NP")
    result = parser.filter_variant(test_filters)
    assert result == ["VUM", "NP"]

    # Try multi to PASS
    result = parser.filter_variant(["MQ", "DTH"])
    assert result == ["PASS"]

    # Try PASS stays PASS
    result = parser.filter_variant(["PASS"])
    assert result == ["PASS"]


@pytest.mark.parametrize(
    "flaglist, exp_res_vcf, bed, alleles",
    [
        (["VUM"], exp_output_vum_vcf, None, False),
        (["VUM", "MN"], exp_output_vum_mn_vcf, None, False),
        (["VUM", "MN"], exp_output_vum_mn_bed_vcf, filter_pos_only_bed, False),
        (
            ["VUM", "MN"],
            exp_output_vum_mn_alleles_bed_vcf,
            filter_alleles_bed_zip,
            True,
        ),
    ],
)
def test_refilter_vcf(flaglist, exp_res_vcf, bed, alleles):
    """
    Unit tests over the refilter_vcf method
    """
    # Filter
    parser = VcfParse(
        input_vcf, output_vcf, run_script, arg_str, bedfile=bed, alleles=alleles
    )
    parser.get_header_flags()
    parser.check_filters_against_flaglist(flaglist)
    parser.refilter_vcf()
    # Ensure that the output and exp output are equal
    assert compare_vcf_files(output_vcf, exp_res_vcf)
    os.remove(output_vcf)


def test_print_header_flags(mocker, capsys):
    """
    Unit tests over the print_header_flags method
    """
    parser = VcfParse(input_vcf, output_vcf, run_script, arg_str)
    mock_vcf = mocker.patch("vcfpy.Reader")
    parser.vcfin = mock_vcf
    mock_vcf.header.get_lines.return_value = heads
    parser.get_header_flags()
    mock_vcf.header.get_lines.called_once()
    assert parser.filters == exp_head
    parser.print_header_flags()
    captured = capsys.readouterr()
    assert captured.out == "{}\t{}\n{}\t{}\n".format(
        exp_head["DTH"]["ID"],
        exp_head["DTH"]["Description"],
        exp_head["MQ"]["ID"],
        exp_head["MQ"]["Description"],
    )


@pytest.mark.parametrize(
    "bed,alleles,exp_locs",
    [
        (filter_pos_only_bed, False, EXP_LOCS),
        (filter_pos_only_bed_zip, False, EXP_LOCS),
        (filter_alleles_bed, True, EXP_LOCS_ALL),
        (filter_alleles_bed_zip, True, EXP_LOCS_ALL),
    ],
)
def test_parse_bed_file(bed, alleles, exp_locs):
    """
    Unit tests over the parse_bed_file method
    """
    parser = VcfParse(input_vcf, output_vcf, run_script, arg_str)
    # Try no allele bed file
    # Try non gzipped file
    parser.bed = bed
    parser.alleles = alleles
    assert parser.parse_bed_file() == exp_locs


@pytest.mark.parametrize(
    "in_head,key_prefix,exp_idx",
    [
        ([vcfpy.HeaderLine("vcfProcessLog", "BLAH")], "vcfProcessLog", None),
        (
            [
                vcfpy.HeaderLine("vcfProcessLog_20160212.1", "BLAH1"),
                vcfpy.HeaderLine("vcfProcessLog_20160212.2", "BLAH2"),
            ],
            "vcfProcessLog",
            2,
        ),
        (
            [
                vcfpy.HeaderLine("vcfProcessLog_20151218.1", "BLAH1"),
                vcfpy.HeaderLine("vcfProcessLog_20160212.1", "BLAH2"),
            ],
            "vcfProcessLog",
            1,
        ),
        ([], "vcfProcessLog", None),
    ],
)
def test_get_last_vcf_process_index(in_head, key_prefix, exp_idx):
    parser = VcfParse(input_vcf, output_vcf, run_script, arg_str)
    assert get_last_vcf_process_index(in_head, key_prefix) == exp_idx
