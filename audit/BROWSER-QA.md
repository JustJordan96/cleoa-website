# Browser verification

Verified against the built local website on 3 November 2026, using the browser UI.

## Layout and navigation

- Desktop at 1440 × 960: home and portfolio layout, project expansion and media presentation.
- Tablet at 768 × 1024: homepage layout, work tabs and the writing archive.
- Phone at 390 × 844: home, About, Services, writing archive, long article and tag archive; no horizontal overflow or failed loaded images.
- Narrow phone at 320 × 740: home, portfolio, writing, a long policy-article title, a LifeStart article and a long tag title. Long-title wrapping was corrected and rechecked; no horizontal overflow remains in these checks.
- Mobile menu opens, exposes all navigation links, and closes on navigation.
- Service links navigate correctly and all four complete service descriptions are present.

## Interactions

- Writing search for `vegetarian Christmas` returns the matching article.
- A nonexistent query produces a clear empty state. Clear search restores the archive.
- More stories reveals the next 12 articles and moves keyboard focus to the first newly revealed title.
- Film & television filter displays the five matching portfolio entries.
- Direct project links open the appropriate project and scroll it into view.
- Home tabs respond to arrow keys and End, update their selected state, and expose the correct panel.
- Image gallery opens, moves to the next image, reports its position, closes with Escape and restores focus to its opening button.
- All six independent-film gallery images and all 14 LifeStart gallery images are present.

## Media

- A love for the land plays inside the YouTube embed, with the correct title, controls, captions and 5:31 duration.
- KFC local MP4 plays without a media error and reports 30.89 seconds.
- KCL Cassettes local MP3 plays without a media error and reports approximately 144.84 seconds.
- Closing a project pauses its local media. Filtering a playing project out pauses it.
- Closing a project with a YouTube player removes the iframe and restores the play button.
- All 12 original YouTube videos return successful public oEmbed responses; see `youtube-checks.json`. Individual playback was sampled as above, not claimed for every third-party film.
- All three local videos and the MP3 also passed the file/decoder checks in `media-notes.md`.

## Build and HTTP checks

- 110 generated pages return HTTP 200.
- A nonexistent URL returns the custom page with HTTP 404.
- Media byte-range requests return HTTP 206 with the expected Content-Range and byte count.
- 3,302 local references checked: no missing files or fragment targets.
- All 28 migrated article bodies match the built article text.
- Every original portfolio paragraph appears in the generated portfolio.
- All 109 discovered original routes are represented, plus `/services`.
- All 121 migrated assets exist locally; no original Wix runtime is required.
- No application console errors were observed during the checked interactions.

Final screenshots: `screenshots/home-desktop.jpg` and `screenshots/home-mobile.jpg`.

This is local build and browser verification. The user's domain and production hosting have not been configured or deployed. External publishers control the continued availability of their pages and YouTube videos.

## LinkedIn update acceptance — 4 November 2026

The three numbered update labels have become semantic `time` elements with verified dates. A More on LinkedIn block follows the update cards, with a full-width Visit my LinkedIn button on mobile. Checked at 320px and 390px without horizontal overflow. The published Preview was also checked at 390px: all three dates, the visible block, stacked layout, and profile link were present. Screenshot: `screenshots/linkedin-mobile.jpg`.
