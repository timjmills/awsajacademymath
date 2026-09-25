# Awsaj Math Curriculum

The White Rose Maths curriculum site for Awsaj Academy: pacing grids, lesson popups, EE standards, tools, PD, IXL, Twinkl, This Week, and catch-me-up.

The whole site is one self-contained file, `index.html`. All data, fonts and code are inline, so you can host it anywhere static.

## Hosting on GitHub Pages

Settings → Pages → Source: **Deploy from a branch**, branch `main`, folder `/ (root)`.
The site is then served at `https://timjmills.github.io/awsajacademymath/`.

## MY TEACHING (sign-in and tracking)

The tracker is a separate Cloudflare Worker (`awsaj-math-tracker-api`) with a D1 database. It stays on Cloudflare, because GitHub Pages can't run a server.
After moving the site, set the Worker's `ALLOW_ORIGIN` setting to `https://timjmills.github.io`. Otherwise sign-in fails with "Failed to fetch".
