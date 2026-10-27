# Plan: Fix MeldpuntWegen.be submission gaps & enable automatic reporting

## Goal
Make `rep-1792496871149` (and future reports) submittable to meldpuntwegen.be via
real browser automation, fully automatically, with verified form filling.

## Current state
- Report `rep-1792496871149` is in `concept` status, data-complete (GPS, impactedGroups,
  1558-char text, contact info, 2 photos <2.5MB).
- Two older reports closed (`opgelost`).
- Meldpunt browser automation exists (`meldpuntBrowser.ts`) but container lacks
  Chromium/Xvfb/ffmpeg/Whisper/Buster extension.

## Phase 1 — Container image: install browser automation deps
Update `Dockerfile` (builder + runtime stages) to install:
- `chromium` (or `playwright install chromium`)
- `xvfb`
- `ffmpeg`
- `python3` + `pip install openai-whisper`
- Buster extension: run `npm run setup:buster` during build, copy `.bundler/buster-extension` into image.
- Set `ENV DISPLAY=:99`, `ENV HEADLESS=false` (already in helm values, but bake into image too).

Also add to `charts/urbanfix/values*.yaml` env (already present: HEADLESS=false, DISPLAY=:99, MELDPUNT_MODE=real).

## Phase 2 — Verify Buster extension path
- Confirm `/app/.bundler/buster-extension` exists in the image.
- Set `BUSTER_EXTENSION_PATH=/app/.bundler/buster-extension` in helm values.
- Set `BUSTER_WHISPER_MODEL=tiny`.

## Phase 3 — Dry-run verification (form filling check)
Before real submission, run a dry run to confirm all form fields are filled:
```
POST /api/meldpunt/submit { "reportId": "rep-1792496871149", "dryRun": true }
  with X-Meldpunt-Mode: real
```
Verify screenshots/logs show:
1. reCAPTCHA solved (Buster audio challenge).
2. GPS location pinned on map.
3. Impacted groups selected.
4. Report text (<2000 chars) entered.
5. Contact info filled (name, email, wants response).
6. Photos uploaded (<2.5MB each).
7. Form submitted (dry-run stops before final POST).

If any field is missing/incorrect, fix the browser agent selectors.

## Phase 4 — Real submission
Only after dry run succeeds with all fields verified:
```
POST /api/meldpunt/submit { "reportId": "rep-1792496871149", "dryRun": false }
```
Capture the returned tracking code (MWV-YYYY-XXXXX) and update the report status
to `in_behandeling` with the tracking code.

## Phase 5 — Automation for future reports
Make submission fully automatic:
- Add a cron/queue in `reminderCron.ts` or a new `submissionCron.ts` that:
  - Finds reports with status `verzenden` or `concept` (ready to send).
  - Runs dry-run first; if successful, submits for real.
  - Updates report status + tracking code + timeline event.
- Trigger via `/api/meldpunt/submit` or a new `/api/meldpunt/auto-submit` endpoint.
- Add retry logic (3 attempts with exponential backoff) for transient failures.
- Log all automation steps to `automationLogs` on the report.

## Phase 6 — Backfill missing images
- The 7 assets missing on disk (including rep-1792496871149's 2 photos) need
  re-upload from source or be marked `broken` (placeholder UI).
- Run `verifyAndHealAllMedia` to reconcile.

## Acceptance criteria
- [ ] Docker image builds with Chromium/Xvfb/ffmpeg/Whisper/Buster.
- [ ] Dry run succeeds with all form fields filled (screenshots confirm).
- [ ] Real submission returns a valid tracking code.
- [ ] Report status updated to `in_behandeling` with tracking code.
- [ ] Future reports auto-submit without manual intervention.
- [ ] tsc + lint pass (0 errors).

## Files to touch
- `Dockerfile` — add system deps + buster setup
- `server/services/meldpuntBrowser.ts` — verify selectors (if needed)
- `server/services/meldpuntBot.ts` — add auto-submit helper
- `server/services/submissionCron.ts` (new) — cron for auto-submission
- `server.ts` — add `/api/meldpunt/auto-submit` endpoint (optional)
- `charts/urbanfix/values*.yaml` — add BUSTER_EXTENSION_PATH
- `src/components/IncidentDetailPage.tsx` — add "Auto-submit" button (optional)
