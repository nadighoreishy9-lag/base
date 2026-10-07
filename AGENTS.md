# Project notes

## What this repo is

A **WordPress site** for نادیا قریشی (SEO specialist / web designer), converted from the Lovable
design source. The site's three pages are built with **native Elementor widgets** so everything is
editable in the Elementor editor.

```
wordpress/
  elementor/01-home.json      قالب صفحه خانه      (Elementor page template)
  elementor/02-services.json  قالب صفحه خدمات
  elementor/03-portfolio.json قالب صفحه نمونه‌کارها
  plugin/nadia-design/        design system: nadia.css + Vazirmatn + the images
  downloads/index.html        صفحه دانلود فایل‌ها (/nadia-downloads/ در پیش‌نمایش)
  bin/build-elementor.py      generates the three JSON templates (source of truth for content)
  bin/bootstrap.sh            provisions WordPress + Elementor and builds the three pages
  bin/entrypoint-web.sh       web container entrypoint: image setup → bootstrap.sh → apache
  bin/import-pages.php        creates/updates the three pages from the JSON templates
  Dockerfile.web              wordpress:php8.3-apache + the wp-cli binary (see quirks #2)
  README.md                   handover guide (نصب روی دامنه خودی)
  nadia-elementor-site.zip    ready-to-install package (plugin + templates + README)
```

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
| `/nadia-package/nadia-elementor-site.zip` | بسته آماده نصب (افزونه + سه قالب + راهنما) |
| `/nadia-package/templates/01-home.json` | قالب خانه |
| `/nadia-package/templates/02-services.json` | قالب خدمات |
| `/nadia-package/templates/03-portfolio.json` | قالب نمونه‌کارها |

These are bind mounts of `wordpress/downloads/`, `wordpress/nadia-elementor-site.zip` and
`wordpress/elementor/` — the files in the repo are the ones served, nothing is copied. The links in
`downloads/index.html` rely on the HTML `download` attribute, so `.json` links download instead of
opening inline; no `.htaccess` is needed.

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
