# dwyt-docs

Shared documentation of **dwyt** (multi-user successor of the owner's yt-transcribe / yt-transcribe-webui):
the functional plan with its decision log (`docs/terv.md`), the central–runner protocol (`docs/protokoll.md`)
and the architecture diagram (`docs/architektura.svg`/`.png`).

The diagram's source is `tools/architektura_svg.py`; after editing it run it, then `node tools/render_png.js`
(needs playwright) to re-render the PNG. Keep the layout; keep plan, protocol and diagram consistent.

## Conventions

- The owner writes in Hungarian. User-facing docs (`README.md`, `docs/`) and any UI are Hungarian;
  code, comments and this file are English.
- The plan and the decision log live in `dwyt-docs` (`docs/terv.md`, section 20). Read the relevant
  sections before changing anything; when a decision changes, update it there in the same piece of work.
- The central–runner protocol is specified in `dwyt-docs/docs/protokoll.md`; both sides follow it.
- Never commit tokens or keys (API keys, OAuth secrets, runner/MCP tokens). Secrets live in env files or
  the runner's local store, never in the repo.
- Add a test for every behaviour change.
- The old system (`yt-transcribe`, `yt-transcribe-webui`) stays separate and unchanged; code may be
  ported from it, but nothing here may depend on it at runtime.
