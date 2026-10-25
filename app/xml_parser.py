from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class ExportData:
    subdomains: list[str]
    cookies: dict[str, str]


def parse_xml(path: str | Path) -> ExportData:
    xml_path = Path(path)
    if not xml_path.is_file():
        raise FileNotFoundError(f"XML file not found: {xml_path}")

    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML in {xml_path}: {exc}") from exc

    subdomains = [
        element.text.strip()
        for element in root.findall(".//subdomain")
        if element.text and element.text.strip()
    ]

    cookies: dict[str, str] = {}
    for element in root.findall(".//cookie"):
        name = (element.get("name") or "").strip()
        host = (element.get("host") or "").strip()
        if not name:
            raise ValueError("Cookie element is missing its name")
        if not host:
            raise ValueError(f"Cookie '{name}' is missing its host")
        cookies[f"cookie:{name}:{host}"] = (element.text or "").strip()

    if not subdomains and not cookies:
        raise ValueError("No subdomains or cookies found in the XML file")

    return ExportData(subdomains=subdomains, cookies=cookies)
