# jobroom

A small, polite Python client for the public [Job-Room](https://www.job-room.ch)
job board, the job-search platform of the Swiss public employment service
([arbeit.swiss](https://www.arbeit.swiss/)).
It turns the nested records of the site's JSON API into typed objects you can
read, filter and store from a script or a notebook.

It is written for anyone looking for work in Switzerland.

## Install

The package is not on PyPI, so install it from the repository:

```bash
pip install git+https://github.com/mbercx/jobroom
```

The [quickstart](quickstart.md) walks through a search from there.

## Fair use

The search API this package talks to is public, but unofficial: only the
employer-facing publishing API is
[documented](https://test-api.job-room.ch/api-docs/jobAdvertisements/v1/index.html).
It is a service paid for by Swiss taxpayers to help people find work, and it
should be used that way.

!!! warning "Please keep it in the spirit of a job search"

    The client identifies itself with a descriptive `User-Agent` and pauses
    between paginated requests, and `search` stops after 1000 ads unless you
    ask for more. Those defaults are there to keep an ordinary search polite.

    Pulling down the entire corpus of live advertisements is a different
    activity, and no default in this package makes that appropriate. If you
    need bulk data, ask SECO rather than this API.

??? note "How the client tries to be polite"

    - Sends a `User-Agent` naming the package and linking its repository, so the
      operator can see what the traffic is and get in touch.
    - Sleeps half a second between page requests, so a large search spreads out
      instead of arriving as a burst.
    - Requests only as many records as the `limit` you asked for.
