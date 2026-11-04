# Cleo Anderson — self-hosted website

A complete, editable rebuild of [cleoa.co.uk](https://www.cleoa.co.uk), retaining its pastel colours, dark borders, photography and original content. The live website and Cleo's public LinkedIn activity were reviewed on **3 November 2026**.

Source: [JustJordan96/cleoa-website](https://github.com/JustJordan96/cleoa-website) (private repository).

## Preview

Requires Node.js 20 or later. There are **no npm dependencies to install**.

```sh
npm run build
npm run dev
```

Open **http://127.0.0.1:4173**. On Windows, you can instead double-click **Start website preview.cmd**. If a preview is already running, reuse it; do not start another server on the same port. Set `PORT` to use another port.

After editing, run `npm run build` and refresh the browser. The local server binds only to your computer. It is a preview server; use a web server or static host for the public site.

## Included

- Home, About me, Portfolio, Services and Writing.
- All **28 complete articles**, their original dates, links, images and four categories.
- **22 portfolio entries**, the full events history, galleries, film players and radio audio.
- All **72 tag/hashtag archive URLs**. Every original sitemap route and every additional internal archive found during the audit is retained.
- Three linked updates from Cleo's public LinkedIn profile, including the recent Bodrum tourism campaign.
- Responsive navigation, keyboard-operated work tabs, portfolio filters, article search, incremental archive loading, image galleries, native audio/video, and click-to-load YouTube players.
- Search metadata, structured data, canonical URLs, sitemap, robots.txt, favicon and a real 404 page.
- **121 local assets**: 116 images, three MP4s, one MP3 and one research PDF. Images are optimised WebP; the Going Green article image retains its original resolution.

The output has **110 pages plus a 404 page**: 109 original public routes and a convenient `/services` alias. `/services-9` remains available for existing links.

## Hosting on your own domain

1. Run `npm run build` and `npm run check`.
2. Upload the **contents** of `dist/` to your hosting account's document root (often `public_html`). `index.html`, `assets/`, `about-me/`, `projects/`, etc. should be directly inside that root.
3. Enable HTTPS with your hosting provider and point the domain to that hosting account. No domain or DNS settings were changed as part of this build.
4. The canonical domain is `https://www.cleoa.co.uk`, matching the original. Redirect the apex domain to `www`, or change `domain` in `content/site.json` and rebuild if you prefer the apex.
5. Confirm that directory URLs such as `/about-me` and `/post/does-jamaica-have-a-film-industry` serve their `index.html` files. Configure the host's custom 404 to `/404.html`. Avoid a catch-all rewrite to the homepage; these are real static pages.

No database, Wix account, application server, API key or build tool is needed on the host. Contact links open the visitor's email app, matching the original site. There is no pretend contact form or newsletter submission.

### Nginx / Docker option

An Nginx configuration is supplied in `hosting/nginx.conf`. The Dockerfile serves the already-built files:

```sh
npm run build
docker build -t cleoa-website .
docker run --rm -p 8080:80 cleoa-website
```

Open `http://localhost:8080`. Configure HTTPS at your hosting reverse proxy. This optional container configuration has been supplied for deployment; Docker has not been run on this computer.

## Editing

A Vercel Preview is also available for review. Deployment details and future Preview commands are recorded in `audit/VERCEL-PREVIEW.md`. Use the guest-access link from the chat when sharing the protected Preview.

| File | What to edit |
| --- | --- |
| `content/site.json` | Contact information, domain, home-page work and LinkedIn updates |
| `content/projects.json` | Complete project descriptions and event history |
| `content/articles.json` | Article titles, dates, HTML, categories and tags |
| `content/original-pages.json` | About-page copy and service descriptions |
| `scripts/build.mjs` | Page layouts, portfolio categories and media assignments |
| `public/styles.css` | Colours, typography, spacing and responsive layouts |
| `public/app.js` | Menu, tabs, filters, search, gallery and media interactions |
| `public/assets/` | All local images, audio, video and the linked PDF |
| `audit/media-manifest.json` | Source-to-local asset mappings and media component records |

The website renders as static HTML, with a small JavaScript file for interactions. Articles and project copy are present in the HTML; visitors and search engines do not need a client-side framework to retrieve them.

The Jost font is self-hosted under its SIL Open Font License (`public/fonts/OFL.txt`). It keeps a similar geometric feel to the original typography.

## Verification and provenance

`npm run check` verifies every original sitemap route, all archive routes, all 28 article bodies, every project paragraph, local assets, local links and fragment targets, heading counts and structured data. Results are saved in `audit/validation.json`.

`audit/SOURCE-AUDIT.md` records the content scope and LinkedIn additions. `audit/media-notes.md` documents media migration. `audit/tag-pages.json` records successful live inspection of all 72 archives. `audit/youtube-checks.json` records availability of all 12 original YouTube videos. `audit/BROWSER-QA.md` records interaction and responsive checks.

The original site's Journalism category currently contains no articles. The replacement preserves that category and gives visitors useful links to all writing and the journalism portfolio.

YouTube videos, LinkedIn posts, and external portfolio/article links remain with their original publishers. They are not copied into a new account. YouTube loads only when a visitor chooses to play a film. LinkedIn updates are an editable snapshot, not an automatically refreshed feed.

The `scripts/audit_original.py`, `scripts/extract_content.py` and `scripts/migrate_assets.py` scripts are optional migration utilities. They require Python and their documented packages; they are **not** required to build or host the finished site. Do not rerun extraction after editorial changes unless you intend to refresh the original copy.
