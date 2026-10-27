# Plan: Verify & submit rep-1792496871149 to meldpuntwegen.be

## Goal
Verify every form step works (with screenshots before each "next" click), confirm
the map is pinned correctly from GPS coordinates, then submit for real.

## Current readiness
- Report `rep-1792496871149` data-complete: GPS (50.9522, 3.6833), impactedGroups
  [voetgangers, fietsers], 1558-char text (<2000), contact info, 2 photos (<2.5MB).
- Container (k8s) has Chromium/Xvfb/ffmpeg/Whisper/Buster? → NO. Needs Phase 1 below.
- k8s pod is running with MELDPUNT_MODE=real, HEADLESS=false, DISPLAY=:99.

## Phase 1 — Container prep (one-time)
1. Update Dockerfile to install: chromium, xvfb, ffmpeg, python3, pip install openai-whisper.
2. Run `npm run setup:buster` during build → copy `.bundler/buster-extension` into image.
3. Set env: BUSTER_EXTENSION_PATH=/app/.bundler/buster-extension, BUSTER_WHISPER_MODEL=tiny.
4. Rebuild image, update helm, redeploy. Verify pod is 1/1 Ready.

## Phase 2 — Dry run with per-step screenshots
Call:
  POST /api/meldpunt/submit { "reportId": "rep-1792496871149", "dryRun": true }
  header X-Meldpunt-Mode: real

The dryRunSubmission already captures screenshots after each step:
  01_initial_page, 02_recaptcha_solved, 03_location_selected,
  04_faq_handled, 05_form_filled, 06_contact_filled

Verify each screenshot shows:
- 02: reCAPTCHA checkbox checked (Buster solved).
- 03: map pin at GPS 50.9522, 3.6833 (not default/center of Flanders).
- 04: FAQ page auto-advanced.
- 05: text (1558 chars), impacted groups (voetgangers, fietsers), 2 photos uploaded.
- 06: contact info (Aldo Fieuw, aldo.fieuw@gmail.com, wants response).

If any step fails, fix the selector/logic in meldpuntBrowser.ts and re-run.

## Phase 3 — Map verification (critical)
The selectLocation() uses Leaflet's setView + synthetic click. Must confirm:
- The map's center moves to [50.9522, 3.6833].
- The click registers the correct AWV road segment.
- The address field is populated (or at least the GPS is accepted).

If the synthetic click doesn't register, fall back to filling the coordinate
input fields directly (if the form has them) or use page.click on the map canvas
at the computed pixel position.

## Phase 4 — Real submission (only after Phase 2+3 pass)
  POST /api/meldpunt/submit { "reportId": "rep-1792496871149", "dryRun": false }
  header X-Meldpunt-Mode: real

Expected: tracking code MWV-YYYY-XXXXX returned, report status → in_behandeling,
timeline event added, automationLogs recorded.

## Phase 5 — Automation for future reports
- Add submissionCron.ts that finds reports with status "verzenden"/"concept" ready
  to send, runs dry-run first, then submits for real on success.
- Retry 3x with backoff on transient failures.
- Log to automationLogs.

## Acceptance
- [ ] Docker image builds with all browser deps.
- [ ] Dry run screenshots confirm all 7 steps.
- [ ] Map pin at correct GPS.
- [ ] Real submission returns tracking code.
- [ ] tsc + lint 0 errors.
