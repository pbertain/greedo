# OPERATIONS.md — Holonet Timestamp System

## Purpose

This document describes how to operate, deploy, and use the Holonet Timestamp System
in real-world environments (CLI, APIs, logs, and production services).

---

## Installation

### Local development

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Direct execution

```bash
python holonet_stamp.py --sw-time
```

---

## Runtime modes

### Web UI / human-facing output

```bash
holonet-stamp --sw-time
```

- Pretty output
- Banner + color
- Auto RID prefix: `web-`

### API responses

```bash
holonet-stamp --sw-time --json
```

- Structured JSON
- Auto RID prefix: `api-`

### Logs / systemd / cron

```bash
holonet-stamp --sw-time --quiet
```

- One-line output
- Stable field order
- Auto RID prefix: `curl-`

---

## Request ID handling

### Inbound

If running behind a proxy or gateway, pass through `X-Request-ID` as an environment variable:

```bash
export HTTP_X_REQUEST_ID=api-abc123
holonet-stamp --json --sw-time
```

### Outbound

All outbound HTTP calls (e.g. quote API) automatically include:

```
X-Request-ID: <request_id>
```

---

## Logging recommendations

- Prefer `--quiet` for production logs
- Prefer `--json --one-line` for log aggregation systems
- Always log `request_id` as a top-level field

Example systemd unit snippet:

```ini
ExecStart=/usr/bin/holonet-stamp --sw-time --quiet
```

---

## Monitoring & observability

This system is intentionally lightweight and does not include metrics.

Recommended practices:
- Use `request_id` for correlation
- Emit timestamps alongside application logs
- Let your logging platform handle aggregation

---

## Failure modes

- Quote API unavailable:
  - Safe fallback (no quote output)
  - No impact on exit code
- Invalid timezone:
  - Python exception (fail fast)
- Invalid CLI flags:
  - argparse usage output

---

## Security considerations

- No secrets are stored
- No user input is executed
- Network access is optional and outbound-only
- Safe for untrusted log contexts

---

## Upgrades & compatibility

- CGT math is stable and versioned by epoch mode
- New flags should be additive
- Existing output fields should not be removed

---

## Operational checklist

Before deploying:

- [ ] Tests passing (`python -m unittest -v`)
- [ ] Correct timezone configured
- [ ] Desired output mode selected
- [ ] RID prefix strategy decided (`api-`, `curl-`, `web-`)

---

## Final note

This tool is meant to *augment* your logs, not replace observability tooling.

It adds clarity, context, and just enough fun to keep engineers engaged.

Han shot first.
