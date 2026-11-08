from app import hris
from app.rag import knowledge
from app.rag.text import chunk_markdown, strip_accents, tokenize


def test_accent_free_query_matches():
    assert strip_accents("Nghỉ phép đường biển") == "Nghi phep duong bien"
    assert "nghi_phep" in tokenize("nghỉ phép")
    a = knowledge.search("chuyển phép năm sang năm sau", ["people_policy"], 1)
    b = knowledge.search("chuyen phep nam sang nam sau", ["people_policy"], 1)
    assert a and b and a[0]["chunk_id"] == b[0]["chunk_id"]


def test_chunker_keeps_heading_path():
    chunks = chunk_markdown("# A\n\n## B\n\ntext one\n\n## C\n\ntext two", size=100, overlap=10)
    assert [c.heading for c in chunks] == ["A > B", "A > C"]


def test_payslip_math_is_consistent():
    s = hris.build_payslip(40_000_000, 2_000_000, 0, 0, dependants=1)
    assert s["gross"] == 42_000_000
    assert s["net"] == s["gross"] - s["social_insurance"] - s["health_insurance"] - s["unemployment_insurance"] - s["pit"]
    capped = hris.build_payslip(200_000_000, 0, 0, 0, 0)
    assert capped["social_insurance"] == int(hris.INSURANCE_CAP * hris.SI_RATE)


def test_org_tree():
    org = hris.get_org()
    assert org.bu_of("SMG-ALPHA") == "SMG"
    assert "SMG-ALPHA" in org.descendants("SMG")
    assert org.ancestors("SMG-ALPHA")[0] == hris.GROUP_UNIT
