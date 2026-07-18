"""
parse_disruptions.py
---------------------
Parses a BODS SIRI-SX disruptions XML file into a flat pandas
DataFrame. SIRI-SX is XML, not CSV, so this uses Python's built-in
xml.etree.ElementTree rather than a DataFrame reader.

Note (documented limitation, see docs/architecture.md and the report's
"Known Limitations" section): the vast majority of disruption records
do not specify a particular operator (AffectedOperator), so this data
is used as regional/national context rather than joined to individual
operators.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from src.config import resolve_path

_NAMESPACE = {"siri": "http://www.siri.org.uk/siri"}


def parse_disruptions(config: dict) -> pd.DataFrame:
    """Parse the configured SIRI-SX XML file into a flat DataFrame,
    one row per <PtSituationElement> (disruption record)."""
    disruptions_dir = resolve_path(config["data"]["disruptions_dir"])
    file_path = disruptions_dir / config["data"]["disruptions_file"]

    tree = ET.parse(file_path)
    root = tree.getroot()
    situations = root.findall(".//siri:PtSituationElement", _NAMESPACE)

    records = [_situation_to_record(sit) for sit in situations]
    return pd.DataFrame(records)


def _get_text(element: ET.Element, tag: str) -> str | None:
    found = element.find(tag, _NAMESPACE)
    return found.text if found is not None else None


def _situation_to_record(situation: ET.Element) -> dict:
    all_operators = situation.find(
        ".//siri:Affects/siri:Operators/siri:AllOperators", _NAMESPACE
    )
    operator_refs = situation.findall(
        ".//siri:Affects/siri:Operators/siri:AffectedOperator/siri:OperatorRef",
        _NAMESPACE,
    )
    if all_operators is not None:
        operators = "ALL"
    elif operator_refs:
        operators = ",".join(o.text for o in operator_refs)
    else:
        operators = None

    place_names = situation.findall(
        ".//siri:Affects/siri:Places/siri:AffectedPlace/siri:PlaceName", _NAMESPACE
    )
    places = ",".join(p.text for p in place_names) if place_names else None

    severity_el = situation.find(
        ".//siri:Consequences/siri:Consequence/siri:Severity", _NAMESPACE
    )

    return {
        "situation_number": _get_text(situation, "siri:SituationNumber"),
        "creation_time": _get_text(situation, "siri:CreationTime"),
        "progress": _get_text(situation, "siri:Progress"),
        "reason": _get_text(situation, "siri:MiscellaneousReason"),
        "planned": _get_text(situation, "siri:Planned"),
        "severity": severity_el.text if severity_el is not None else None,
        "operators": operators,
        "places": places,
        "summary": _get_text(situation, "siri:Summary"),
    }
