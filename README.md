[![Templated from python-copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/mbercx/python-copier/refs/heads/main/docs/img/badge.json)](https://github.com/mbercx/python-copier)

# `jobroom`

A polite Python client for the public [Job-Room](https://www.job-room.ch) (arbeit.swiss) job-search API.

## Fair use

The search API is public but unofficial — only the employer-facing publishing API is [officially documented](https://test-api.job-room.ch/api-docs/jobAdvertisements/v1/index.html).
This client identifies itself via its `User-Agent` and rate-limits paginated requests; please keep your usage in the spirit of a job search rather than bulk harvesting.
