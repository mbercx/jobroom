"""Tests for `jobroom.models`."""

from datetime import date

import pytest

from jobroom.models import JobAd, SearchHit, clean_html

# A single record as returned by the search endpoint
# (`POST /jobadservice/api/jobAdvertisements/_search`), trimmed to the fields
# we care about. The response is a JSON list of these records.
SEARCH_RECORD = {
    "jobAdvertisement": {
        "id": "0b1ce0f9-2ce5-4eaa-ae1c-784cd054c100",
        "publication": {"startDate": "2026-07-21"},
        "jobContent": {
            "externalUrl": "https://example.org/jobs/74898",
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
            "company": {"name": "Example Research Institute"},
            "location": {"city": "Villigen", "cantonCode": "AG"},
            "employment": {
                "workloadPercentageMin": "80",
                "workloadPercentageMax": "100",
                "permanent": True,
            },
        },
    },
    "favouriteItem": None,
}

# A record as returned by the detail endpoint
# (`GET /jobadservice/api/jobAdvertisements/{id}`): the same content, but
# without the `jobAdvertisement` envelope and with the complete description.
DETAIL_RECORD = {
    "id": "0b1ce0f9-2ce5-4eaa-ae1c-784cd054c100",
    "publication": {"startDate": "2026-07-21", "endDate": "2026-08-20"},
    "jobContent": {
        "externalUrl": "https://example.org/jobs/74898",
        "jobDescriptions": [
            {
                "languageIsoCode": "en",
                "title": "Scientific Computing Systems Engineer",
                "description": "**Your profile**&nbsp;\n\n *  Bash and <em>Python</em>",
            }
        ],
        "company": {
            "name": "Example Research Institute",
            "street": "Examplestrasse 1",
            "postalCode": "5232",
            "city": "Villigen",
            "countryIsoCode": "CH",
        },
        "location": {"city": "Villigen", "cantonCode": "AG"},
        "employment": {
            "workloadPercentageMin": "80",
            "workloadPercentageMax": "100",
            "permanent": True,
        },
        "applyChannel": {
            "formUrl": "https://example.org/jobs/74898/apply",
            "emailAddress": None,
        },
        "publicContact": {
            "firstName": "Example",
            "lastName": "Person",
            "email": "example.person@example.org",
            "phone": "+41 00 000 00 00",
        },
    },
}


def test_detail_record_to_job_ad():
    """A raw detail record is flattened into a `JobAd`."""
    ad = JobAd.model_validate(DETAIL_RECORD)

    assert ad.id == "0b1ce0f9-2ce5-4eaa-ae1c-784cd054c100"
    assert ad.title == "Scientific Computing Systems Engineer"
    assert ad.city == "Villigen"
    assert ad.canton == "AG"
    assert ad.workload == (80, 100)
    assert ad.permanent is True
    assert ad.published_on == date(2026, 7, 21)
    assert ad.expires_on == date(2026, 8, 20)
    assert ad.external_url == "https://example.org/jobs/74898"
    assert ad.apply_url == "https://example.org/jobs/74898/apply"
    assert ad.apply_email is None
    assert ad.language == "en"
    assert ad.description == "**Your profile**\u00a0\n\n *  Bash and Python"
    assert ad.raw == DETAIL_RECORD


def test_job_ad_sub_models():
    """The employer address and contact person are parsed into sub-models."""
    ad = JobAd.model_validate(DETAIL_RECORD)

    assert ad.company.name == "Example Research Institute"
    assert ad.company.street == "Examplestrasse 1"
    assert ad.company.postal_code == "5232"
    assert ad.company.country == "CH"
    assert ad.contact.first_name == "Example"
    assert ad.contact.last_name == "Person"
    assert ad.contact.email == "example.person@example.org"


def test_job_ad_missing_nested_data():
    """Ads without an apply channel, contact or employment block still validate."""
    ad = JobAd.model_validate(
        {"id": "x", "jobContent": {"applyChannel": None, "publicContact": None}}
    )

    assert ad.id == "x"
    assert ad.apply_url is None
    assert ad.apply_email is None
    assert ad.contact is None
    assert ad.workload is None


def test_search_record_to_hit():
    """A raw search record is flattened into a `SearchHit`."""
    hit = SearchHit.model_validate(SEARCH_RECORD)

    assert hit.id == "0b1ce0f9-2ce5-4eaa-ae1c-784cd054c100"
    assert hit.title == "Scientific Computing Systems Engineer"
    assert hit.company == "Example Research Institute"
    assert hit.city == "Villigen"
    assert hit.canton == "AG"
    assert hit.published_on == date(2026, 7, 21)
    assert hit.external_url == "https://example.org/jobs/74898"
    assert hit.raw == SEARCH_RECORD


def test_snippet_html_is_cleaned():
    """HTML tags and entities are stripped from the snippet, text untouched."""
    hit = SearchHit.model_validate(SEARCH_RECORD)

    assert "<em>" not in hit.snippet
    assert "&nbsp;" not in hit.snippet
    assert "Scripting in Bash and Python" in hit.snippet


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (r"clicca su \<\<Per candidarsi\>\>.", "clicca su <<Per candidarsi>>."),
        (r"Interventionen \<\< best-effort \>\>", "Interventionen << best-effort >>"),
        ("5 < 10 and 20 > 3", "5 < 10 and 20 > 3"),
        ("Bash and <em>Python</em>", "Bash and Python"),
    ],
)
def test_clean_html_keeps_text(raw, expected):
    """Only real tags are stripped: escaped or bare angle brackets are text."""
    assert clean_html(raw) == expected


def test_missing_nested_data():
    """Records with missing or null sub-objects still validate."""
    hit = SearchHit.model_validate(
        {"jobAdvertisement": {"id": "x", "jobContent": {"company": None}}}
    )

    assert hit.id == "x"
    assert hit.title is None
    assert hit.company is None
    assert hit.snippet is None
