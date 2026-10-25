import json

from app.exporter import export_to_redis
from app.xml_parser import ExportData


class FakePipeline:
    def __init__(self, store):
        self.store = store
        self.pending = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def set(self, key, value):
        self.pending.append((key, value))
        return self

    def execute(self):
        self.store.update(self.pending)
        return [True] * len(self.pending)


class FakeRedis:
    def __init__(self):
        self.store = {}

    def pipeline(self, transaction=True):
        assert transaction is True
        return FakePipeline(self.store)


def test_writes_subdomains_and_cookie_values():
    client = FakeRedis()
    data = ExportData(
        subdomains=["http://secureline.tools.avast.com", "http://gf.tools.avast.com"],
        cookies={"cookie:dlp-avast:amazon": "mmm_amz_dlp_777_ppc_m"},
    )

    keys = export_to_redis(client, data)

    assert keys == ["subdomains", "cookie:dlp-avast:amazon"]
    assert json.loads(client.store["subdomains"]) == data.subdomains
    assert client.store["cookie:dlp-avast:amazon"] == "mmm_amz_dlp_777_ppc_m"


def test_writes_an_empty_subdomain_array_when_there_are_no_values():
    client = FakeRedis()

    keys = export_to_redis(client, ExportData(subdomains=[], cookies={}))

    assert keys == ["subdomains"]
    assert client.store["subdomains"] == "[]"
