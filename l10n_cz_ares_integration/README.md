# DIG ARES Integration

**Author:** Digital Resources a.s.
**Website:** https://www.digres.cz
**Depends:** `base`, `contacts`

## Overview

Integrates the Czech [ARES](https://ares.gov.cz) (Administrative Register of Economic Subjects) into Odoo contacts. Automatically enriches partner records with official business data fetched from the ARES REST API.

## Features

- **Contact enrichment** — button on the partner form to fetch data from ARES on demand

## How It Works

### IČO extraction

The module extracts an 8-digit IČO from the VAT/DIČ field. Both formats are supported:
- `CZ12345678`
- `12345678`

### Manual fetch

A **Fetch from ARES** button is available on the partner form. Clicking it calls the ARES API and updates the partner with the returned data.

## ARES API

```
GET https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/{ico}
```

