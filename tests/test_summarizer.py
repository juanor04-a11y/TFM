import json
from types import SimpleNamespace
import pytest

from ott_ticket_intelligence.genai.IncidentSummarizer import IncidentSummarizer


VALID_RESPONSE = {
    "generated_title": "Playback issue",
    "generated_summary": "Several tickets report playback failures.",
    "probable_issue": "Possible playback service degradation.",
    "affected_scope": "OTT playback",
    "recommended_action": "Review playback telemetry.",
    "warning": "The group may contain heterogeneous symptoms.",
}


def make_client(payload):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
    )

    class FakeCompletions:
        def create(self, **kwargs):
            return response

    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=FakeCompletions()
        )
    )


def test_rejects_invalid_max_tickets():
    with pytest.raises(ValueError, match="max_tickets"):
        IncidentSummarizer(make_client(VALID_RESPONSE), "fake-model", max_tickets=0)


def test_sample_tickets_respects_limit():
    summarizer = IncidentSummarizer(make_client(VALID_RESPONSE), "fake-model", max_tickets=3)

    sample = summarizer.sample_tickets(["a", "b", "c", "d", "e"], cluster_id=1)

    assert len(sample) == 3


def test_sample_tickets_is_reproducible():
    summarizer = IncidentSummarizer(make_client(VALID_RESPONSE), "fake-model", max_tickets=3, random_seed=42)
    tickets = ["a", "b", "c", "d", "e"]

    assert summarizer.sample_tickets(tickets, 5) == summarizer.sample_tickets(tickets, 5)


def test_parse_response_rejects_missing_fields():
    summarizer = IncidentSummarizer(make_client(VALID_RESPONSE), "fake-model")

    with pytest.raises(ValueError, match="Missing fields"):
        summarizer._parse_response(json.dumps({"generated_title": "Only one field"}))


def test_summarize_returns_expected_structure():
    summarizer = IncidentSummarizer(make_client(VALID_RESPONSE), "fake-model", max_tickets=2)

    result = summarizer.summarize(
        cluster_id=7,
        ticket_count=4,
        ticket_texts=["Playback fails", "Video freezes", "Player error", "Cannot start video"],
    )

    assert result["cluster_id"] == 7
    assert result["ticket_count"] == 4
    assert result["tickets_used_for_context"] == 2
    for field in IncidentSummarizer.EXPECTED_FIELDS:
        assert field in result
