# Project notes

## What this repo is

A **WordPress site** for نادیا قریشی (SEO specialist / web designer), converted from the Lovable
design source. The site's three pages are built with **native Elementor widgets** so everything is
editable in the Elementor editor.

```
wordpress/
  elementor/01-home.json      قالب صفحه خانه      (self-contained Elementor page template)
  elementor/02-services.json  قالب صفحه خدمات
  elementor/03-portfolio.json قالب صفحه نمونه‌کارها
  plugin/nadia-design/        design system: nadia.css + Vazirmatn + the images
  downloads/index.html        صفحه دانلود فایل‌ها (/nadia-downloads/ در پیش‌نمایش)
  bin/build-elementor.py      generates the three JSON templates (source of truth for content)
  bin/bootstrap.sh            provisions WordPress + Elementor and builds the three pages
  bin/entrypoint-web.sh       web container entrypoint → docker-entrypoint.sh apache2-bootstrap
  bin/apache2-bootstrap       bootstrap.sh → apache2-foreground (name must start with "apache2", see quirks #5)
  bin/import-pages.php        creates/updates the three pages from the JSON templates
  bin/build-kit.py            patches the exported Elementor kit (page titles → slugs, see "The kit")
  Dockerfile.web              wordpress:php8.3-apache + the wp-cli binary (see quirks #2)
  README.md                   handover guide (نصب روی دامنه خودی)
  nadia-elementor-site.zip    legacy package (plugin + templates + README)
  nadia-elementor-kit.zip     Elementor kit: global colors/fonts + three pages, no plugin needed
```

The three templates are **self-contained**: the whole `nadia.css` is embedded in an HTML widget at
the top of each page and images load from the public Lovable domain, so importing them needs no
plugin (see "The kit").

`nadia-elementor-pixel-template.json` in the repo root is the older hand-made export and is unused.

## Running it

```bash
docker compose -f docker-compose.base44.yml up -d           # db + wordpress on :3000
docker compose -f docker-compose.base44.yml logs -f wordpress  # includes provisioning output
```

- `db` — MariaDB 11, data in the `db-data` volume.
- `wordpress` — built from `wordpress/Dockerfile.web`, core in the `wp-data` volume, **port 3000**.
  The style plugin is bind-mounted from `wordpress/plugin/nadia-design`, so CSS edits show up
  immediately (no rebuild, no live-reload server — use `reload_preview` after edits).
  Provisioning runs **inside this service** on every start (`bin/entrypoint-web.sh` →
  `bin/bootstrap.sh`): installs WP, installs/activates Elementor + Hello Elementor, activates the
  style plugin, installs the Persian language pack, sets `/%postname%/` permalinks and
  (re)builds the three pages. It is idempotent. Re-run after changing a template:

```bash
docker compose -f docker-compose.base44.yml up -d --force-recreate wordpress
```

There is deliberately **no separate `wpcli` service**: a one-shot container would sit in the
`exited` state, which the Base44 supervisor reports as a failed application service. The `wp-cli`
binary is copied into the web image instead (`Dockerfile.web`).

After editing content in `bin/build-elementor.py`: `python3 wordpress/bin/build-elementor.py wordpress/elementor`
then re-run the `wordpress` service.

WP admin: `/wp-admin`, user `admin`, password `${WP_ADMIN_PASSWORD:-nadia-dev-admin}` (dev only).

## Downloading the deliverables

The preview serves the handover files so they can be downloaded from the browser:

| URL | File |
| --- | --- |
| `/nadia-downloads/` | صفحه دانلود با دکمه‌ها (RTL) |
| `/nadia-package/nadia-elementor-kit.zip` | کیت المنتور (رنگ/فونت سراسری + سه صفحه، بدون افزونه) |
| `/nadia-package/nadia-elementor-site.zip` | بسته قدیمی (افزونه + سه قالب + راهنما) |
| `/nadia-package/templates/01-home.json` | قالب خانه |
| `/nadia-package/templates/02-services.json` | قالب خدمات |
| `/nadia-package/templates/03-portfolio.json` | قالب نمونه‌کارها |

These are bind mounts of `wordpress/downloads/`, `wordpress/nadia-elementor-site.zip` and
`wordpress/elementor/` — the files in the repo are the ones served, nothing is copied. The links in
`downloads/index.html` rely on the HTML `download` attribute, so `.json` links download instead of
opening inline; no `.htaccess` is needed.

## The kit (`nadia-elementor-kit.zip`)

An Elementor **kit export** (Elementor → Tools → Import/Export Kit) carrying the site's global colors
+ typography and the three pages. It is produced by Elementor itself, so the format is exactly what
the importer expects.

Rebuild it:

```bash
python3 wordpress/bin/build-elementor.py wordpress/elementor      # regenerate the templates
docker compose -f docker-compose.base44.yml exec -T wordpress \
  wp --path=/var/www/html --allow-root eval-file /source/bin/import-pages.php
# (re)set the kit's global colors/typography, then:
docker compose -f docker-compose.base44.yml exec -T wordpress \
  wp --path=/var/www/html --allow-root elementor kit export /tmp/kit.zip --include=settings,content
docker compose -f docker-compose.base44.yml cp wordpress:/tmp/kit.zip /tmp/kit.zip
python3 wordpress/bin/build-kit.py /tmp/kit.zip wordpress/nadia-elementor-kit.zip
```

- `build-kit.py` is **required**: Elementor derives each imported page's *slug from its title*, so the
  Persian titles produced percent-encoded Persian slugs while the menu links to `/services/` and
  `/portfolio/`. The script rewrites the manifest titles to `Home`/`Services`/`Portfolio` so the
  imported pages get the slugs the menu expects.
- Elementor's free version has no usable "Custom CSS" (the Site Settings tab is a Pro teaser), so the
  CSS cannot travel in the kit's settings — it lives inside each page instead. That is why the
  templates embed `nadia.css` and reference images from the public Lovable domain.
- `wp elementor kit import` needs `--user=admin`; plain `--allow-root` fails with "You must run this
  command as an admin user". The kit's `experiments` list is ignored on import, so it is safe to ship.

## Sandbox quirks (discovered the hard way)

1. **Preview proxy is not a forwarding proxy.** It sends no `X-Forwarded-Proto` and forwards the
   request with the *internal* sandbox host (`3000-<id>.$BASE44_SANDBOX_HOST_DOMAIN`), so WordPress
   believes it is on http at a foreign host and redirects `/` to the site URL forever.
   Fix: `bootstrap.sh` writes `wp-content/mu-plugins/nadia-preview-proxy.php` **only when
   `BASE44_PREVIEW_MODE` is exactly `"1"`** (and deletes it otherwise) to set `$_SERVER['HTTPS']`,
   `SERVER_PORT` and `HTTP_HOST` to the real browser values. Unset/other values → original behavior.
2. **No `mysql` client in the web image.** `wp db query` shells out to the `mysql` binary, which
   the official `wordpress:php8.3-apache` image does not ship (it only exists in `wordpress:cli`).
   Provisioning now runs in the web container, so `bootstrap.sh` probes the database with
   `php -r mysqli_connect(...)` instead. Keep that probe if you add DB waits.
3. **Healthcheck must probe `/index.php`.** The health check uses `php -r file_get_contents()`
   against `http://127.0.0.1/index.php` (php is the only http client in the image) and its
   `start_period` (240s) must cover provisioning, since Apache only starts after `bootstrap.sh`.
4. **Nested bind mounts cannot be created inside a read-only mount.** The download files are
   mounted at sibling paths under `/var/www/html/` (`nadia-downloads/` and `nadia-package/`) rather
   than nesting a file inside the read-only `downloads/` mount.
5. **The official entrypoint only provisions when `$1` matches `apache2*`.** Newer
   `wordpress:php8.3-apache` images gate the core-copy + `wp-config.php` block with
   `[[ "${1-}" == apache2* ]]`, so the previous `docker-entrypoint.sh true` idiom skipped
   provisioning entirely: the core was never copied into the volume, `bootstrap.sh` waited forever
   on `wp core version`, and the container never became healthy (the app failed to start).
   `entrypoint-web.sh` now calls `docker-entrypoint.sh apache2-bootstrap`; `apache2-bootstrap`
   runs `bootstrap.sh` and then `exec apache2-foreground`. Keep the final command `apache2*`-prefixed
   and executable (`chmod +x`) — it is exec'd via `PATH`, not run with `sh`.
6. **Provisioning must stay idempotent, because `set -eu` turns any error into a crash loop.**
   `wp plugin install elementor --activate` (and the theme equivalent) exits 1 once the plugin folder
   already exists — which happens as soon as a newer Elementor is released. `bootstrap.sh` now guards
   both with `wp plugin is-installed` / `wp theme is-installed` and only installs when missing.

## Elementor specifics that this project depends on

- **Widget vs container CSS classes.** Containers read `css_classes`, widgets read `_css_classes`
  (`includes/widgets/common-base.php`). `bin/build-elementor.py` sets **both** on every element so
  the templates work across Elementor versions.
- **Optimized markup.** Elementor 4.x omits `div.e-con-inner` (containers) and
  `div.elementor-widget-container` (widgets). `nadia.css` normalizes both layers with
  `display: contents`, so layout rules sit on the element itself and work in either mode.
- **Icons** are rendered as inline `<svg class="e-font-icon-svg e-fas-…">` (no Font Awesome `<i>`
  tag), so icon boxes are sized via `.elementor-icon svg`.
- **Page canvas.** Templates use `page_settings.template = elementor_canvas`; the header/footer are
  inside each page (no Elementor Pro theme builder needed).
- **Images** are referenced as `/wp-content/plugins/nadia-design/assets/images/…` so an imported
  template renders correctly on any domain without extra setup.
- The generated CSS lives in `wp-content/uploads/elementor/css/post-<id>.css`;
  `import-pages.php` calls Elementor's file manager `clear_cache()` after each import.

## Verifying the site works

```bash
U="https://3000-$BASE44_PUBLIC_HOST_SUFFIX"
curl -s -o /dev/null -w '%{http_code}\n' "$U/" "$U/services/" "$U/portfolio/"     # 200 200 200
curl -s -o /dev/null -w '%{http_code}\n' "$U/nadia-downloads/" \
     "$U/nadia-package/nadia-elementor-site.zip" "$U/nadia-package/templates/01-home.json"
curl -s "$U/" | grep -o 'elementor/css/post-[0-9]*\.css'                          # generated CSS linked
curl -s "$U/" | grep -o 'id="\(services\|portfolio\|resume\|contact\)"'            # anchors
```

Expected structure: home = hero + 6 service cards + 3 projects + dark résumé band (3 steps) +
contact box; services = divider + 4 SEO cards + 2 design cards + 4 process steps + CTA;
portfolio = 5 filter chips + featured project + 6 work cards + CTA.

Elementor's real import path (Templates → Import) can be exercised without a browser:

```bash
docker compose -f docker-compose.base44.yml exec -T -v /tmp:/extra wordpress \
  sh -c "wp --path=/var/www/html --allow-root eval-file /extra/verify-import.php"
```

with a script calling `wp_set_current_user(1)` then
`\Elementor\Plugin::$instance->templates_manager->get_source('local')->import_template($name, $path)`.
