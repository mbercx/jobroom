"""Typed representation of a Job-Room job advertisement."""

from __future__ import annotations

import html
import re
from datetime import date
from typing import Any

from pydantic import (
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

HTML_TAG = re.compile(r"<[^>]+>")


def clean_html(text: str) -> str:
    """Strip HTML tags and decode HTML entities, leaving the text content untouched."""
    return html.unescape(HTML_TAG.sub("", text))


class Company(BaseModel):
    """The employer, with the address details of its head office."""

    name: str | None = None
    street: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country: str | None = None


class Contact(BaseModel):
    """Contact person for the position, when the ad names one."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None


class SearchHit(BaseModel):
    """A single row of a search result: enough to decide if an ad is interesting.

    The full advertisement — including the complete `description` — is a `JobAd`,
    obtained via `JobRoomClient.get`.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "jobDescriptions", 0, "title")
    )
    company: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "company", "name")
    )
    city: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "location", "city")
    )
    canton: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "location", "cantonCode")
    )
    published_on: date | None = Field(
        None, validation_alias=AliasPath("publication", "startDate")
    )
    snippet: str | None = Field(
        None,
        validation_alias=AliasPath("jobContent", "jobDescriptions", 0, "description"),
    )
    external_url: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "externalUrl")
    )
    raw: dict[str, Any] = Field(default_factory=dict, repr=False)

    @model_validator(mode="before")
    @classmethod
    def unwrap_envelope(cls, data: Any) -> Any:
        """Unwrap the `jobAdvertisement` envelope of a search record, keeping it on `raw`."""
        if isinstance(data, dict) and "jobAdvertisement" in data:
            return {**data["jobAdvertisement"], "raw": data}
        return data

    @field_validator("snippet")
    @classmethod
    def strip_markup(cls, value: str | None) -> str | None:
        return clean_html(value) if value else value


class JobAd(BaseModel):
    """A single job advertisement, normalized for reading.

    The untouched API payload is kept on `raw`.
    """

    id: str
    title: str | None = None
    company: Company | None = None
    city: str | None = None
    canton: str | None = None
    workload: tuple[int, int] | None = None
    permanent: bool | None = None
    published_on: date | None = None
    expires_on: date | None = None
    external_url: str | None = None
    apply_url: str | None = None
    apply_email: str | None = None
    contact: Contact | None = None
    description: str | None = None
    language: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict, repr=False)
