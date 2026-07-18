
import xml.etree.ElementTree as ET

from src.ingest.parse_disruptions import _situation_to_record

FIXTURE_XML = """
<PtSituationElement xmlns="http://www.siri.org.uk/siri">
    <SituationNumber>test-123</SituationNumber>
    <CreationTime>2024-08-30T09:07:04.813Z</CreationTime>
    <Progress>open</Progress>
    <MiscellaneousReason>roadworks</MiscellaneousReason>
    <Planned>true</Planned>
    <Summary>Test disruption</Summary>
    <Affects>
        <Operators>
            <AllOperators/>
        </Operators>
        <Places>
            <AffectedPlace>
                <PlaceName>Testville</PlaceName>
            </AffectedPlace>
        </Places>
    </Affects>
    <Consequences>
        <Consequence>
            <Severity>normal</Severity>
        </Consequence>
    </Consequences>
</PtSituationElement>
"""


def test_situation_to_record_extracts_all_operators():
    element = ET.fromstring(FIXTURE_XML)
    record = _situation_to_record(element)

    assert record["situation_number"] == "test-123"
    assert record["reason"] == "roadworks"
    assert record["operators"] == "ALL"
    assert record["places"] == "Testville"
    assert record["severity"] == "normal"


FIXTURE_XML_NO_OPERATOR = """
<PtSituationElement xmlns="http://www.siri.org.uk/siri">
    <SituationNumber>test-456</SituationNumber>
    <MiscellaneousReason>roadworks</MiscellaneousReason>
    <Affects>
        <Operators></Operators>
        <Places>
            <AffectedPlace>
                <PlaceName>Testville</PlaceName>
            </AffectedPlace>
        </Places>
    </Affects>
</PtSituationElement>
"""


def test_situation_to_record_handles_missing_operator():
    element = ET.fromstring(FIXTURE_XML_NO_OPERATOR)
    record = _situation_to_record(element)

    assert record["operators"] is None
