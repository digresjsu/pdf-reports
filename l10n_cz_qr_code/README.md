# Czech QR Payment Code (QR Platba)

**Author:** Digital Resources a.s.
**Website:** https://www.digres.cz
**Depends:** `base`, `account`

## Overview

Generates Czech **QR Platba** payment codes on invoices. The QR code is computed and stored on the invoice record.

## Features

- QR code generated automatically on posted invoices
- Encodes account number, amount due, variable symbol, due date, and message
- Two rendering modes: standard (with border) and borderless
- Default - standard, can be changed in settings

## Requirements

The following Python libraries must be installed on the Odoo server:

| Library | Purpose |
|---------|---------|
| `qrplatba` | Generates the QR Platba string and SVG image |
| `cairosvg` | Converts SVG to PNG (used in standard mode) |
| `qrcode` | Generates borderless PNG directly (used in borderless mode) |

## Configuration

Go to **Settings → Accounting** and enable:

- **Enable QR Code for Czech payments** — turns on QR generation globally
- **Generate without border** — uses `qrcode` library to produce a borderless PNG instead of the default bordered output via `cairosvg`

### Generation conditions

A QR code is only generated when all of the following are true:

- Feature is enabled in Settings
- Move type is `out_invoice` or `out_refund`
- Invoice is in `posted` state
- Payment state is not `paid`, `in_payment`, or `reversed`
- Currency is `CZK`
- A partner bank account is set on the invoice

### QR data

| Field | Source |
|-------|--------|
| Account number | `partner_bank_id.acc_number` |
| Amount | `amount_residual` |
| Variable symbol | Digits extracted from `payment_reference` or invoice name (max 10 digits) |
| Due date | `invoice_date_due` |
| Message | `ref` (max 60 characters) |
