"""Tests for `jobroom.models`."""

from datetime import date

from jobroom.models import SearchHit

# A single record as returned by the search endpoint
# (`POST /jobadservice/api/jobAdvertisements/_search`), trimmed to the fields
# we care about. The response is a JSON list of these records.
SEARCH_RECORD = {
    "jobAdvertisement": {
        "id": "0b1ce0f9-2ce5-4eaa-ae1c-784cd054c100",
        "publication": {"startDate": "2026-07-21"},
        "jobContent": {
            "externalUrl": "https://www.psi.ch/en/hr/job-opportunities/74898",
            "jobDescriptions": [
                {
                    "languageIsoCode": "en",
                    "title": "Scientific Computing Systems Engineer",
                    "description": (
                        "## Your profile ##&nbsp;\n\n"
                        " *  Scripting in Bash and <em>Python</em>"
                    ),
                }
            ],
            "company": {"name": "Paul Scherrer Institut (PSI)"},
            "location": {"city": "Villigen PSI", "cantonCode": "AG"},
            "employment": {
                "workloadPercentageMin": "80",
                "workloadPercentageMax": "100",
                "permanent": True,
            },
        },
    },
    "favouriteItem": None,
}


def test_search_record_to_hit():
    """A raw search record is flattened into a `SearchHit`."""
    hit = SearchHit.model_validate(SEARCH_RECORD)

    assert hit.id == "0b1ce0f9-2ce5-4eaa-ae1c-784cd054c100"
    assert hit.title == "Scientific Computing Systems Engineer"
    assert hit.company == "Paul Scherrer Institut (PSI)"
    assert hit.city == "Villigen PSI"
    assert hit.canton == "AG"
    assert hit.published_on == date(2026, 7, 21)
    assert hit.external_url == "https://www.psi.ch/en/hr/job-opportunities/74898"
    assert hit.raw == SEARCH_RECORD


def test_snippet_html_is_cleaned():
    """HTML tags and entities are stripped from the snippet, text untouched."""
    hit = SearchHit.model_validate(SEARCH_RECORD)

    assert "<em>" not in hit.snippet
    assert "&nbsp;" not in hit.snippet
    assert "Scripting in Bash and Python" in hit.snippet


def test_missing_nested_data():
    """Records with missing or null sub-objects still validate."""
    hit = SearchHit.model_validate(
        {"jobAdvertisement": {"id": "x", "jobContent": {"company": None}}}
    )

    assert hit.id == "x"
    assert hit.title is None
    assert hit.company is None
    assert hit.snippet is None
