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

HTML_TAG = re.compile(r"(?<!\\)</?[a-zA-Z][^>]*>|<!--.*?-->", re.DOTALL)
ESCAPED_BRACKET = re.compile(r"\\([<>])")


def clean_html(text: str) -> str:
    """Strip HTML tags and decode HTML entities, leaving the text content untouched.

    Angle brackets that the API escaped for markdown (`\\<\\< ... \\>\\>`) are text,
    not markup: they are left in place and unescaped.
    """
    return ESCAPED_BRACKET.sub(r"\1", html.unescape(HTML_TAG.sub("", text)))


class Company(BaseModel):
    """The employer, with the address details of its head office."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    street: str | None = None
    postal_code: str | None = Field(None, validation_alias="postalCode")
    city: str | None = None
    country: str | None = Field(None, validation_alias="countryIsoCode")


class Contact(BaseModel):
    """Contact person for the position, when the ad names one."""

    model_config = ConfigDict(populate_by_name=True)

    first_name: str | None = Field(None, validation_alias="firstName")
    last_name: str | None = Field(None, validation_alias="lastName")
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

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "jobDescriptions", 0, "title")
    )
    company: Company | None = Field(
        None, validation_alias=AliasPath("jobContent", "company")
    )
    city: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "location", "city")
    )
    canton: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "location", "cantonCode")
    )
    workload: tuple[int, int] | None = None
    permanent: bool | None = Field(
        None, validation_alias=AliasPath("jobContent", "employment", "permanent")
    )
    published_on: date | None = Field(
        None, validation_alias=AliasPath("publication", "startDate")
    )
    expires_on: date | None = Field(
        None, validation_alias=AliasPath("publication", "endDate")
    )
    external_url: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "externalUrl")
    )
    apply_url: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "applyChannel", "formUrl")
    )
    apply_email: str | None = Field(
        None, validation_alias=AliasPath("jobContent", "applyChannel", "emailAddress")
    )
    contact: Contact | None = Field(
        None, validation_alias=AliasPath("jobContent", "publicContact")
    )
    description: str | None = Field(
        None,
        validation_alias=AliasPath("jobContent", "jobDescriptions", 0, "description"),
    )
    language: str | None = Field(
        None,
        validation_alias=AliasPath(
            "jobContent", "jobDescriptions", 0, "languageIsoCode"
        ),
    )
    raw: dict[str, Any] = Field(default_factory=dict, repr=False)

    @model_validator(mode="before")
    @classmethod
    def collect_workload(cls, data: Any) -> Any:
        """Combine the separate workload percentages into one range, and keep the record on `raw`."""
        if not isinstance(data, dict) or "jobContent" not in data:
            return data
        employment = data["jobContent"].get("employment") or {}
        workload = (
            employment.get("workloadPercentageMin"),
            employment.get("workloadPercentageMax"),
        )
        return {**data, "workload": None if None in workload else workload, "raw": data}

    @field_validator("description")
    @classmethod
    def strip_markup(cls, value: str | None) -> str | None:
        return clean_html(value) if value else value
