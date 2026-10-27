# Plan: Fix image availability across servers (imgbb)

## Problem
Images uploaded via UrbanFix are stored as local files on the originating machine
(`data/uploads/masters/...`, `data/uploads/thumbs/...`) and a remote backup is
attempted via Imgur. When the app runs on a different server (k8s pod), the local
files are absent, and Imgur uploads have been failing with "Content not available
in your region." Result: images are unrecoverable on the deployment server.

Constraints: Firebase Storage is NOT viable (images too large for the bucket/quota).
Use imgbb.com instead (free tier allows up to 32 MB per image).

## imgbb API (reference)
- Endpoint: `POST https://api.imgbb.com/1/upload?key=API_KEY`
- Body (multipart/form-data): `image` (base64 or file), optional `expiration` (seconds)
- Response: `{ data: { id, url, display_url, delete_url, thumb: { url }, ... } }`
- API key: `e5fb5891ef74397a7b27c56922c200c3` (store in env `IMGBB_API_KEY`, never hardcode)
- No region block observed; serves as the Tier-1 CDN.

## Proposed fix (3 phases)

### Phase 1 — Add imgbb as Tier-1 (replacing Imgur as primary)
In `server/services/mediaService.ts`:
- Add `uploadToImgbb(imageBuffer, filename, expiration?)` → returns
  `{ success, data: { id, url, delete_url, thumb_url } }`.
- In `saveImageDualStorage`, after the local write, attempt imgbb upload
  (parallel to/instead of Imgur). Update ledger with `imgbb.url` + `imgbb.delete_url`.
- Add `imgbb` block to `MediaAsset` (mirroring the `imgur` block).
- Keep Imgur as a fallback (or remove to simplify). Prefer imgbb first.

### Phase 2 — Add imgbb fallback to read paths
- View/thumb endpoints and `PhotoItem.url`/`thumbUrl`: if local file missing,
  redirect/serve from the imgbb URL (or proxy it).
- `checkImgurAvailability` → generalize to `checkRemoteAvailability(url)`.

### Phase 3 — Backfill existing assets
- For the 7 assets currently missing on disk (including rep-1791968019547's 2
  images), re-upload from the original source if available; otherwise mark them
  `broken` so the UI shows a placeholder instead of 404s.
- Optionally seed the PVC from a backup of `/data/uploads` for the dev node.

## Env / config
- Add `IMGBB_API_KEY` to `.env.example`, Dockerfile, helm values (env), and
  `getImgbbApiKey()` helper (default to the provided key only as a fallback,
  prefer env).

## Files to touch
- `server/services/mediaService.ts` — imgbb upload + ledger + fallback
- `src/types.ts` — add `imgbb` block to `MediaAsset`
- `src/components/PhotoLightbox.tsx`, `ReportCard.tsx`, `MapView.tsx` — prefer imgbb URL
- `server.ts` — view/thumb endpoints fallback to imgbb URL
- `.env.example`, `Dockerfile`, `charts/urbanfix/values*.yaml` — add `IMGBB_API_KEY`

## Out of scope
- Migrating existing imgur URLs (leave as-is; new uploads use imgbb).
- Changing the local-disk Tier 0 (keep for fast reads on the node that has them).
