#!/bin/sh
# راه‌اندازی وردپرس + المنتور و ساخت سه صفحه از قالب‌های مخزن.
# این اسکریپت idempotent است: هر بار اجرا شود، صفحات را به‌روزرسانی می‌کند.
set -eu

WP="wp --path=/var/www/html --allow-root"

# شیم محیط پیش‌نمایش: پروکسی Base44 هدر X-Forwarded-Proto نمی‌فرستد و درخواست را با هاست
# داخلی sandbox می‌رساند؛ بدون این شیم وردپرس فکر می‌کند درخواست روی http و هاستی دیگر است و
# بی‌وقفه به آدرس سایت ریدایرکت می‌کند. فقط وقتی BASE44_PREVIEW_MODE دقیقاً "1" باشد ساخته می‌شود.
MU_DIR=/var/www/html/wp-content/mu-plugins
if [ "${BASE44_PREVIEW_MODE:-}" = "1" ] && [ -n "${BASE44_PUBLIC_HOST_SUFFIX:-}" ]; then
  mkdir -p "$MU_DIR"
  cat > "$MU_DIR/nadia-preview-proxy.php" <<'PHP'
<?php
/**
 * فقط در محیط پیش‌نمایش Base44 بارگذاری می‌شود: هاست و پروتکل واقعی مرورگر را
 * به وردپرس اعلام می‌کند تا ریدایرکت بی‌پایان به آدرس سایت رخ ندهد.
 */
if (getenv('BASE44_PREVIEW_MODE') === '1' && getenv('BASE44_PUBLIC_HOST_SUFFIX')) {
    $_SERVER['HTTPS'] = 'on';
    $_SERVER['SERVER_PORT'] = '443';
    $_SERVER['HTTP_HOST'] = '3000-' . getenv('BASE44_PUBLIC_HOST_SUFFIX');
}
PHP
  echo "→ شیم پروکسی پیش‌نمایش فعال شد"
else
  rm -f "$MU_DIR/nadia-preview-proxy.php"
fi

fix_ownership() {
  # همه‌چیز جز افزونه nadia-design (که از مخزن mount شده) باید مال کاربر وب‌سرور باشد.
  find /var/www/html/wp-content -mindepth 1 -maxdepth 1 -not -name nadia-design \
    -exec chown -R 33:33 {} + 2>/dev/null || true
}

fix_ownership

echo "→ انتظار برای فایل‌های هسته وردپرس"
until $WP core version >/dev/null 2>&1; do sleep 2; done

echo "→ انتظار برای دیتابیس"
until $WP db query "SELECT 1" >/dev/null 2>&1; do sleep 2; done

# آدرس سایت: در حالت پیش‌نمایش Base44 از دامنه عمومی و در غیر آن از localhost استفاده می‌شود.
if [ "${BASE44_PREVIEW_MODE:-}" = "1" ] && [ -n "${BASE44_PUBLIC_HOST_SUFFIX:-}" ]; then
  SITE_URL="https://3000-${BASE44_PUBLIC_HOST_SUFFIX}"
else
  SITE_URL="${SITE_URL:-http://localhost:3000}"
fi

if ! $WP core is-installed; then
  echo "→ نصب وردپرس روی $SITE_URL"
  $WP core install \
    --url="$SITE_URL" \
    --title="نادیا قریشی | کارشناس سئو و طراح وب" \
    --admin_user=admin \
    --admin_password="${WP_ADMIN_PASSWORD:-nadia-dev-admin}" \
    --admin_email=admin@example.com \
    --skip-email
fi

$WP option update home "$SITE_URL" >/dev/null
$WP option update siteurl "$SITE_URL" >/dev/null
$WP option update blogdescription "سئو با نگاه طراحی؛ طراحی با فکر دیده‌شدن" >/dev/null
$WP option update timezone_string "Asia/Tehran" >/dev/null

echo "→ نصب افزونه المنتور و قالب Hello Elementor"
$WP plugin install elementor --activate
$WP theme install hello-elementor --activate
$WP plugin activate nadia-design

echo "→ زبان فارسی وردپرس"
$WP language core install fa_IR --activate || echo "  (نصب بسته زبان انجام نشد؛ مشکلی برای نمایش سایت نیست)"

echo "→ ساختار پیوندها"
$WP rewrite structure '/%postname%/' --hard >/dev/null

echo "→ ساخت/به‌روزرسانی صفحات المنتور"
$WP eval-file /source/bin/import-pages.php

# بازگرداندن مالکیت به کاربر وب‌سرور (uid=33 در تصویر وردپرس) تا آپلودها و CSS المنتور نوشته شوند.
fix_ownership

echo "✓ آماده است: $SITE_URL"
