# Project notes

## What this repo is

`nadia-elementor-pixel-template.json` is a WordPress **Elementor page template export**
(`type: "page"`, `template: "elementor_canvas"`). All the page content lives in one
Elementor `html` widget at `content[0].elements[0].settings.html`.

The export contains **markup only — no styling**. The `.ngp-*` classes it uses are styled by
`assets/ngp.css`, written for this repo (the original Elementor/Lovable stylesheet was not
exported with the template). Replace or extend `ngp.css` with the real design when it is available.

The portrait and project images are loaded from `https://nadiaghoeyshi.lovable.app/assets/...`,
so the preview needs outbound access to that host for images.

## How it runs

`docker-compose.base44.yml` serves the repo with `server.mjs` (plain Node, no dependencies) on
**host port 3000**:

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

- Static root is the repo root; `GET /` serves `index.html`.
- `index.html` fetches the template JSON and mounts the widget HTML into `#ngp-root`, so the
  JSON stays the single source of truth (edit the JSON → the page shows the change, no build step).
- `server.mjs` exposes `GET /__version` (newest file mtime in the repo). The page polls it once a
  second and reloads itself when anything changes — there is no separate hot-reload dev server.

## Verifying it works

```bash
curl -sI http://localhost:3000/                       # 200 + text/html
curl -s  http://localhost:3000/ | grep ngp-root       # index.html served
curl -s  http://localhost:3000/nadia-elementor-pixel-template.json | head -c 40
docker compose -f docker-compose.base44.yml ps        # web: healthy
```

The page should render the RTL Persian layout: sticky glass navigation, hero with portrait,
six service cards, three portfolio cards, résumé timeline, contact box and footer.
