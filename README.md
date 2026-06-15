# prufa-mcp — the QA agent for your vibe-coded app

> "Median 5 hours from vulnerability disclosure to mass automated exploitation."
> — [Patchstack 2026 State of WordPress Security](https://www.propellermediaworks.com/blog/web-security-ai-hackers-risk-vibe-coding)

Vibe-coded apps ship faster than humans can review. Prufa is the agent that
audits them — tracking pixels, broken flows, consent violations, console errors —
before the 5-hour window opens.

## 30-second demo

![Prufa running on a vibe-coded Next.js app](assets/demo.gif)

> The demo GIF will land in v0.2. Until then, see "What you get" below for
> the live call shape, and `examples/` for runnable scripts.

## Quickstart

```bash
pip install prufa-mcp
# or
npm install -g prufa-mcp  # (npm mirror — not yet published, see Task 1.11)
```

Then in your `.mcp.json` (Claude Code, Cursor, Cline, Continue, etc.):

```json
{
  "mcpServers": {
    "prufa": {
      "command": "prufa-mcp",
      "env": {
        "PRUFA_API_TOKEN": "your-prufa-api-key"
      }
    }
  }
}
```

Get a free API key at [prufa.dev](https://prufa.dev) — the first audit is free, no card required.

Then in your agent:

```
> audit https://my-vibe-coded-app.com
> run prufa on my staging deploy and show me the criticals
> check my landing page for broken tracking pixels
```

## What you get (the OSS surface)

| Tool | What it does |
|---|---|
| `prufa_run_audit` | One call → runs a public-page audit, returns findings JSON |
| `prufa_get_report` | Fetches a shareable report for a completed audit |

That's it. The audit primitive is small. The hosted product at
[prufa.dev](https://prufa.dev) is where the value compounds — scheduling,
alerting, team workflows, and the human-readable HTML report.

## Why open source

Same shape as [Stagehand](https://github.com/browserbase/stagehand) (free) →
[Browserbase](https://www.browserbase.com) (paid). Open the primitive. The
hosted tier earns the right to be paid by being the thing that scales.

## Examples

- `examples/nextjs-app/` — audit a deployed Next.js app
- `examples/vite-spa/` — audit a Vite SPA
- `examples/stripe-checkout/` — audit a Stripe-checkout page (focuses on payment-flow verification)

Each example is a copy-pasteable demo. Clone, set `PRUFA_API_TOKEN`, run.

## GitHub Action

Add PR-time audits to any repo:

```yaml
# .github/workflows/prufa-scan.yml
name: Prufa scan
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install prufa-mcp
      - name: Run audit
        env:
          PRUFA_API_TOKEN: ${{ secrets.PRUFA_API_TOKEN }}
        run: |
          python -c "
          import asyncio, json, sys
          from prufa_mcp.audit import run_audit
          result = asyncio.run(run_audit(url='${{ secrets.STAGING_URL }}', wait=True))
          print(json.dumps(result, indent=2))
          criticals = [f for f in result.get('findings', []) if f.get('severity') == 'critical']
          if criticals:
              print(f'::error::Prufa found {len(criticals)} critical finding(s)', file=sys.stderr)
              sys.exit(1)
          "
```

See `examples/prufa-scan.yml` for the full template.

## SLO

The hosted audit API targets a 30-second p95 for `wait=true` on public pages.
The OSS server is a thin client — it does no audit work itself, so its only
SLO is "responds to MCP `list_tools` and `call_tool` within 1 second."

## License

Apache-2.0. See [LICENSE](LICENSE).
