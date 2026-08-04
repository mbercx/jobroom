"""Typed representation of a Job-Room job advertisement."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


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

    id: str
    title: str | None = None
    company: str | None = None
    city: str | None = None
    canton: str | None = None
    published_on: date | None = None
    snippet: str | None = None
    external_url: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict, repr=False)


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
