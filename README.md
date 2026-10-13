# Awsaj Math Curriculum

The White Rose Maths curriculum site for Awsaj Academy: pacing grids, lesson popups, EE standards, tools, PD, IXL, Twinkl, This Week, and catch-me-up.

The whole site is one self-contained file, `index.html`. All data, fonts and code are inline, so you can host it anywhere static.

## Hosting on GitHub Pages

Settings → Pages → Source: **Deploy from a branch**, branch `main`, folder `/ (root)`.
The site is then served at `https://timjmills.github.io/awsajacademymath/`.

## MY TEACHING (sign-in and tracking)

The tracker is a separate Cloudflare Worker (`awsaj-math-tracker-api`) with a D1 database. It stays on Cloudflare, because GitHub Pages can't run a server.
After moving the site, set the Worker's `ALLOW_ORIGIN` setting to `https://timjmills.github.io`. Otherwise sign-in fails with "Failed to fetch".

## Site versions

The default `index.html` is the updated K–5 curriculum resequenced by Common Core State Standards (CCSS) domain. Its purple banner links to `old/`, which preserves the previous curriculum and is clearly labeled OLD SITE. The former `preview/` address redirects to the updated default site; its downloadable documents remain in `preview/docs/`.

The default site uses the existing production local storage and tracker API; the preview-only tracking restriction has been removed.

Domain cards on each grade overview expand to show the scheduled lessons and domain data, including a separate enrichment section after MAP. Weekly pacing can be expanded or collapsed by domain. These preferences are saved per grade and signed-in teacher in that browser; signed-out visitors use a separate browser-local preference. Preferences do not sync across devices.
