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
  bin/build-elementor.py      generates the three JSON templates (source of truth for content)
  bin/bootstrap.sh            provisions the local WordPress + Elementor and builds the pages
  bin/import-pages.php        creates/updates the three pages from the JSON templates
  README.md                   handover guide (نصب روی دامنه خودی)
  nadia-elementor-site.zip    ready-to-install package (plugin + templates + README)
```

`nadia-elementor-pixel-template.json` in the repo root is the older hand-made export and is unused.

## Running it

```bash
docker compose -f docker-compose.base44.yml up -d      # db + wordpress on :3000 + one-shot wpcli
docker compose -f docker-compose.base44.yml logs wpcli  # provisioning output
```

- `db` — MariaDB 11, data in the `db-data` volume.
- `wordpress` — `wordpress:php8.3-apache`, core in the `wp-data` volume, **port 3000**.
  The style plugin is bind-mounted from `wordpress/plugin/nadia-design`, so CSS edits show up
  immediately (no rebuild, no live-reload server — use `reload_preview` after edits).
- `wpcli` — one-shot, idempotent provisioning: installs WP, installs/activates Elementor +
  Hello Elementor, activates the style plugin, installs the Persian language pack, sets
  `/%postname%/` permalinks and (re)builds the three pages. Re-run after changing a template:

```bash
docker compose -f docker-compose.base44.yml up -d --force-recreate wpcli
```

After editing content in `bin/build-elementor.py`: `python3 wordpress/bin/build-elementor.py wordpress/elementor`
then re-run the `wpcli` service.

WP admin: `/wp-admin`, user `admin`, password `${WP_ADMIN_PASSWORD:-nadia-dev-admin}` (dev only).

## Sandbox quirks (discovered the hard way)

1. **Preview proxy is not a forwarding proxy.** It sends no `X-Forwarded-Proto` and forwards the
   request with the *internal* sandbox host (`3000-<id>.$BASE44_SANDBOX_HOST_DOMAIN`), so WordPress
   believes it is on http at a foreign host and redirects `/` to the site URL forever.
   Fix: `bootstrap.sh` writes `wp-content/mu-plugins/nadia-preview-proxy.php` **only when
   `BASE44_PREVIEW_MODE` is exactly `"1"`** (and deletes it otherwise) to set `$_SERVER['HTTPS']`,
   `SERVER_PORT` and `HTTP_HOST` to the real browser values. Unset/other values → original behavior.
2. **wp-cli image uid mismatch.** `wordpress:cli` is Alpine (`www-data` = uid 82) while the
   `wordpress` image is Debian (`www-data` = uid 33), so the shared volume is not writable by the
   cli user. The `wpcli` service therefore runs as root with `--allow-root` and `bootstrap.sh`
   chowns `wp-content` back to 33:33 at the end (skipping the bind-mounted plugin).
3. **Healthcheck must probe `/index.php`.** `/wp-login.php` 30x-redirects through the public URL,
   which a naive probe follows out of the container. The check uses `php -r file_get_contents()`
   against `http://127.0.0.1/index.php` (php is the only http client in the image).

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
curl -s "$U/" | grep -o 'elementor/css/post-[0-9]*\.css'                          # generated CSS linked
curl -s "$U/" | grep -o 'id="\(services\|portfolio\|resume\|contact\)"'            # anchors
```

Expected structure: home = hero + 6 service cards + 3 projects + dark résumé band (3 steps) +
contact box; services = divider + 4 SEO cards + 2 design cards + 4 process steps + CTA;
portfolio = 5 filter chips + featured project + 6 work cards + CTA.

Elementor's real import path (Templates → Import) can be exercised without a browser:

```bash
docker compose -f docker-compose.base44.yml run --rm -v /tmp:/extra --entrypoint sh wpcli \
  -c "wp --path=/var/www/html --allow-root eval-file /extra/verify-import.php"
```

with a script calling `wp_set_current_user(1)` then
`\Elementor\Plugin::$instance->templates_manager->get_source('local')->import_template($name, $path)`.
