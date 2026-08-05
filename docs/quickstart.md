# Quickstart

A job search has two stages, and `jobroom` follows them: scan many ads quickly,
then read the few worth applying to in full.

## Search for jobs

```python
from jobroom import JobRoomClient

client = JobRoomClient()
hits = client.search(keywords=["python"], workload_min=80, online_since=7)

for hit in hits:
    print(f"{hit.published_on}  {hit.canton}  {hit.company}: {hit.title}")
```

`search` returns a list of `SearchHit` objects: one scannable row per ad, with a
`snippet` showing your keyword in context.
Available filters:

| Argument | Meaning |
| --- | --- |
| `keywords` | Terms the ad must match, e.g. `["python", "hpc"]` |
| `workload_min` | Minimum workload ("Pensum") in percent, e.g. `80` |
| `online_since` | Only ads published in the last *n* days, at most 60 |
| `limit` | Stop after this many ads (default 1000) |

## Get the full advertisement

Job-Room does not send the text of an advertisement with the search results,
only an extract of a few hundred characters around your keyword: the `snippet`.
That is enough to decide whether an ad is worth a look, and rarely enough to
judge it on.

Ask for the ones you want to read in full by id:

```python
ad = client.get(hits[0].id)

print(ad.workload)          # a (min, max) pair, e.g. (80, 100)
print(ad.company.name)      # the employer, with its address on the same object
print(ad.description)       # the full text of the advertisement
```

`get` returns a `JobAd`, which adds the full `description` and what you need in
order to apply: the employer and its address (`company`), the contact person
(`contact`), where to send the application (`apply_url`, `apply_email`) and the
date the ad comes down (`expires_on`).

Search hits and advertisements both keep everything Job-Room sent on `raw`, so
a detail this package does not expose is still one lookup away:

```python
ad.raw["jobContent"]["occupations"]
```

!!! tip "Ads expire"

    Advertisements are published for a limited window — typically one or two
    months, given by `expires_on` — after which `get` will not find them again.
    If you want a record of what you applied to, store the ad while it is up:
    `raw` holds everything the API returned.
