from pathlib import Path

import pytest

from app.xml_parser import parse_xml


HOST_CODES = {
    "amazon": "amz",
    "baixaki": "bxk",
    "computerbuild": "cbd",
    "chip": "cip",
    "comss": "cms",
    "cnet": "cnt",
    "dobreprogramy": "dbp",
    "donwloaden": "dld",
    "facebook": "fcb",
    "filehippo": "fhp",
    "forest": "for",
    "html": "htm",
    "homepate": "htr",
    "naver": "nav",
    "01net": "net",
    "softpedia": "sfp",
    "softonic": "sft",
    "slunecnice": "slc",
    "stahuj": "sth",
    "tamindir": "tam",
    "ultradownloads": "uld",
    "uptodown": "utd",
    "vector": "vct",
}


def test_reads_the_supplied_config():
    path = Path(__file__).parents[1] / "sample" / "config.xml"

    data = parse_xml(path)

    assert len(data.subdomains) == 38
    assert data.subdomains[0] == "http://secureline.tools.avast.com"
    assert data.subdomains[-1] == "https://bits.avcdn.net"
    assert len(data.cookies) == 46
    assert data.cookies["cookie:dlp-avast:amazon"] == "mmm_amz_dlp_777_ppc_m"
    assert data.cookies["cookie:dlp-avg:filehippo"] == "Mmm_fhp_dlp_779_ppc_m"

    for host, code in HOST_CODES.items():
        assert data.cookies[f"cookie:dlp-avast:{host}"] == f"mmm_{code}_dlp_777_ppc_m"
        avg_value = f"mmm_{code}_dlp_779_ppc_m"
        if host == "filehippo":
            avg_value = "Mmm_fhp_dlp_779_ppc_m"
        assert data.cookies[f"cookie:dlp-avg:{host}"] == avg_value


def test_keeps_subdomains_in_file_order_and_skips_blank_entries(tmp_path):
    path = tmp_path / "config.xml"
    path.write_text(
        "<config><subdomains><subdomain> https://a.test </subdomain>"
        "<subdomain> </subdomain><subdomain>https://b.test</subdomain>"
        "</subdomains></config>",
        encoding="utf-8",
    )

    assert parse_xml(path).subdomains == ["https://a.test", "https://b.test"]


def test_last_cookie_with_the_same_key_wins(tmp_path):
    path = tmp_path / "config.xml"
    path.write_text(
        '<config><cookies><cookie name="sid" host="shop">old</cookie>'
        '<cookie name="sid" host="shop">new</cookie></cookies></config>',
        encoding="utf-8",
    )

    assert parse_xml(path).cookies == {"cookie:sid:shop": "new"}


def test_cookie_value_whitespace_is_preserved(tmp_path):
    path = tmp_path / "config.xml"
    path.write_text(
        '<config><cookies><cookie name="sid" host="shop">  abc  </cookie></cookies></config>',
        encoding="utf-8",
    )

    assert parse_xml(path).cookies == {"cookie:sid:shop": "  abc  "}


def test_cookie_without_a_name_is_rejected(tmp_path):
    path = tmp_path / "config.xml"
    path.write_text('<config><cookie host="shop">abc</cookie></config>', encoding="utf-8")

    with pytest.raises(ValueError, match="missing its name"):
        parse_xml(path)


def test_cookie_without_a_host_is_rejected(tmp_path):
    path = tmp_path / "config.xml"
    path.write_text('<config><cookie name="sid">abc</cookie></config>', encoding="utf-8")

    with pytest.raises(ValueError, match="missing its host"):
        parse_xml(path)


def test_invalid_xml_is_reported(tmp_path):
    path = tmp_path / "config.xml"
    path.write_text("<config>", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid XML"):
        parse_xml(path)


def test_missing_file_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError, match="XML file not found"):
        parse_xml(tmp_path / "missing.xml")
