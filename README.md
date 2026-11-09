# NKT Live Sidebar

A compact NKT-themed sidebar powered by Chess.com's **public, read-only Published-Data API**.

## Included live data

- Club member count
- Club average daily rating
- Club creation year
- Three most recently joined members, with joining dates and public profile links
- Countdown to the next **registered club team match**, when one exists

## Intentionally not included

- **Hosted tournament top-three leaderboard:** the public club endpoints do not provide an automatically discoverable list of NKT-hosted tournaments and their standings. This build does not fabricate results or substitute unrelated team-match results.
- Tournament count, game count, rating gain, quotes, awards, and other figures that cannot be verified from the selected public endpoints.
- A countdown when Chess.com has no future registered NKT team match in the public matches response.

## GitHub setup

1. Extract this ZIP into a new GitHub repository, or upload all its contents into the root of an existing repository.
2. Keep the folder structure exactly as supplied:
   - `index.html`
   - `data.json`
   - `scripts/update_data.py`
   - `.github/workflows/update.yml`
3. In GitHub, open **Settings → Actions → General → Workflow permissions** and allow workflows to read and write repository contents.
4. Open **Actions → Update NKT sidebar data → Run workflow** once.
5. After it succeeds, check that `data.json` has been updated.
6. Enable GitHub Pages under **Settings → Pages**, using the branch and root folder containing `index.html`.
7. Open the Pages URL. The sidebar reads `data.json` from the same directory.

The workflow runs every 12 hours and can also be run manually. Chess.com's API cache itself refreshes at most once every 12 hours, so running it more often would not guarantee fresher data.

## If the workflow fails

- Check that the club slug `nashediyon-ki-toli-nkt` is publicly accessible.
- Check the Actions log for a Chess.com `404`, `429`, or network error.
- Do not run many parallel API requests. This workflow makes requests sequentially.
- GitHub Pages serves the last committed `data.json` even if a later scheduled run fails.

## Embedding in Chess.com

Publish this repository with GitHub Pages and use its public Pages URL wherever you are embedding or linking the sidebar. If Chess.com strips external iframe/embed support in the specific sidebar area, the HTML must be placed in a supported hosting/embed surface; the API data pipeline remains separate.

## Data and affiliation

This project uses public Chess.com data. It is an independent community project and is not affiliated with, endorsed by, or sponsored by Chess.com.
