import json
from typing import Any

from app.xml_parser import ExportData


def export_to_redis(client: Any, data: ExportData) -> list[str]:
    keys = ["subdomains", *data.cookies]
    with client.pipeline(transaction=True) as pipe:
        pipe.set("subdomains", json.dumps(data.subdomains))
        for key, value in data.cookies.items():
            pipe.set(key, value)
        pipe.execute()
    return keys
