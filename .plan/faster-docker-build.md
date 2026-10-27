# Plan: Make the Docker build faster

## Current state (measured)
- `urbanfix:dev` image: **1.72 GB**
- Build time: **~1.5 hours** (mostly apt + npm + playwright + node_modules copy)
- Build is NOT running now (server restart killed the background build).
- `node_modules`: 670 MB, `dist`: 3.8 MB
- **No `.dockerignore`** → `COPY . .` copies the entire repo (incl. `node_modules`, `dist`, `.git`) into the build context.

## Why it's slow (root causes)
1. **`COPY . .` copies 670 MB node_modules + dist + .git** into the build context (no .dockerignore). Then the builder's node_modules is copied again into the runner.
2. **Two separate `apt-get install` layers** (builder + runner) re-download/reinstall the same base packages.
3. **`apt-get install chromium`** pulls ~300 packages on arm64 (the single biggest step).
4. **`npx playwright install chromium`** downloads another ~111 MB Chromium (redundant with #3).
5. **`COPY --from=builder /app/node_modules ./node_modules`** copies 670 MB.
6. **No BuildKit layer caching** for apt/npm between builds.

## Options (ranked by impact)

### Option A — Add `.dockerignore` (highest impact, trivial)
Create `.dockerignore` excluding: `node_modules`, `dist`, `.git`, `.slim`, `data`, `.env`, `graphify-out`, `playwright-report`, `test-results`, `screenshots`, `.bundler`.
- Cuts the build context from ~700 MB to ~10 MB.
- `COPY . .` becomes fast.
- **Effort: 5 min. Impact: high.**

### Option B — Remove redundant `apt-get install chromium` (high impact, trivial)
Playwright installs its own Chromium via `npx playwright install chromium`. The apt `chromium` package is redundant and pulls ~300 packages.
- Remove `chromium \` from the runner apt list.
- Rely on Playwright's bundled Chromium (already at `/root/.cache/ms-playwright`).
- **Effort: 2 min. Impact: high (saves ~5-10 min + ~300 MB).**

### Option C — Single apt layer (medium impact, low effort)
Do all apt installs in the builder stage, then copy the runtime libs to the runner (or just install runtime libs in runner and build libs in builder). Actually simpler: install everything needed in the builder, and in the runner only install the runtime libs (`libcairo2`, `libpango-1.0-0`, etc.) which are small.
- Merge the two apt-get blocks.
- **Effort: 10 min. Impact: medium.**

### Option D — Use BuildKit cache mounts for apt (medium impact, low effort)
Add `--mount=type=cache,target=/var/cache/apt` to apt-get commands so package downloads are cached across builds.
- **Effort: 10 min. Impact: medium.**

### Option E — Pre-built base image (highest impact for repeat builds, medium effort)
Build a `urbanfix-base:<arch>` image once with all system deps (chromium, xvfb, ffmpeg, python3, canvas libs, playwright chromium). Then the app Dockerfile just `FROM urbanfix-base` and does npm ci + build.
- Repeat builds become ~2-3 min.
- **Effort: 30 min. Impact: very high for CI/repeat builds.**

### Option F — Remote BuildKit cache (high impact for CI, medium effort)
Add `--cache-to type=registry,ref=...` and `--cache-from type=registry,ref=...` to `docker buildx build`. Requires a registry (GitHub Container Registry works).
- **Effort: 20 min. Impact: very high for CI.**

### Option G — `npm ci --omit=dev` in runner (medium impact, low effort)
If the server bundle is pre-built (`dist/server.js`), the runner doesn't need devDependencies. Run `npm ci --omit=dev` in the runner instead of copying the full node_modules.
- **Effort: 10 min. Impact: medium (saves ~400 MB + copy time).**

### Option H — Alpine base (medium impact, medium risk)
Switch from `node:22-bookworm-slim` to `node:22-alpine`. Smaller image, but native modules (sharp, canvas) may need recompilation and musl compatibility testing.
- **Effort: 1-2 hours + testing. Impact: medium (size), risky.**

## Recommended combination
**A + B + C + D** for immediate improvement (low risk, ~15 min total), then **E** for long-term repeat-build speed.

Expected result: build time from ~1.5 h → ~10-15 min; image size from 1.72 GB → ~900 MB.

## Implementation steps
1. Create `.dockerignore`.
2. Remove `chromium` from runner apt list (keep `xvfb`, `ffmpeg`, `python3`).
3. Merge apt layers (install build libs in builder only; runtime libs in runner).
4. Add apt cache mounts.
5. Rebuild and measure.
6. (Optional) Create `urbanfix-base` image.

## Verification
- `time docker build -t urbanfix:dev .` — compare before/after.
- `docker images urbanfix:dev` — confirm size reduction.
- Verify `npx playwright install chromium` still works and the pod runs the meldpunt dry-run.
