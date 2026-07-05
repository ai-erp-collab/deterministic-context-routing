# <TABLE>

kind: table
source: <artifact path>
aliases: <business names>
status: confirmed|partial|uncertain
confidence: confirmed|inferred|runtime-unverified|blocked-by-access

## Purpose

- <what this table represents>; confidence: <label>

## Keys

- `<FIELD>`: key role

## Fields

- `<FIELD>` <type>(len,dec) key|null|required: meaning; codes if known; confidence: <label>.

## Evidence

- <artifact, source example, user document, or runtime observation>

## Verification Gaps

- <runtime behavior, business meaning, or access-limited source still unverified>

## Links

- used-by: [[usage/...]]
- related: [[tables/...]]
