# Vercel review deployment

Published and verified on 4 November 2026.

- Team: Jordan's projects (`jordans-projects-95de7c5c`).
- Project: `cleoa-preview` (`prj_XaxZAE7jDB30BlTotForw1vXrZ6A`).
- Preview deployment: `dpl_Ccngj6VvB9eAqm7Ay94nA1dpMJNP`.
- Preview origin: https://cleoa-preview-9tec64t9e-jordans-projects-95de7c5c.vercel.app.
- State: READY. Environment: Preview.
- A guest share link was created and delivered in the chat. The share key is not stored in this repository. It has no automatic expiry; it can be revoked from Vercel.
- The initial deployment required by Vercel was made with the user's explicit approval. Its separate Vercel project alias is https://cleoa-preview.vercel.app. No custom domains are attached or modified.

The deploy contains the static build output only. Source files, migration caches, local credentials and raw website captures are excluded. Every response has `X-Robots-Tag: noindex, nofollow`. Social preview images use the public Vercel project origin so shared links can load their image.

## Verification

A new cookie session opened the guest share link without a Vercel login and fetched the actual home page. All 110 page routes returned 200. The custom missing-page route returned 404. CSS, JavaScript and the portrait loaded with the correct content types. Sample audio and video requests returned 206 with the requested byte ranges. The social image was also accessible without login.

Browser checks confirmed portfolio filtering, opening and closing the image gallery, and article search on the hosted Preview. See `vercel-preview-verification.json` for the HTTP results and `screenshots/vercel-preview.jpg` for the published homepage.

## Future Preview uploads

The local `.vercel/project.json` links this folder to the project. Vercel CLI 65.11.0 is installed locally in `.tools/vercel-cli` and uses the existing authenticated local session. The connected Vercel app did not have access to this team; deployment used the local CLI with the explicit team scope.

Build and check the source first. Then, in PowerShell:

```powershell
npm run build
npm run check
$env:VERCEL_PREVIEW_ORIGIN='https://cleoa-preview.vercel.app'
npm run vercel:prepare
node .tools/vercel-cli/node_modules/vercel/dist/index.js project inspect --non-interactive --scope jordans-projects-95de7c5c
node .tools/vercel-cli/node_modules/vercel/dist/index.js deploy --prebuilt --environment preview --yes --scope jordans-projects-95de7c5c --json
```

Confirm the inspected project is `cleoa-preview` before deploying. Each new protected deployment needs its own guest share link. The earlier ZIP downloads remain the portable self-hosting build from 3 November; this deployment setup is an additional local change.

## LinkedIn section update

The latest Preview replaces the update numbers with verified publication dates and adds a dedicated More on LinkedIn block below the cards. Its button fills the available width on phone layouts. Build/content checks passed. Phone layouts were checked at 320px and 390px, and the published guest link was checked without a Vercel login. Source metadata is in `linkedin-publication-dates.json`; this update’s verification is in `linkedin-section-update.json`. The earlier 110-route HTTP verification is retained in `vercel-preview-verification.json`.
