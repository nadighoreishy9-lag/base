#!/bin/sh
# نقطه ورود سرویس وب: ابتدا آماده‌سازی رسمی تصویر وردپرس (کپی هسته در /var/www/html و
# ساخت wp-config.php)، سپس راه‌اندازی المنتور/صفحات با bootstrap.sh و در نهایت اجرای وب‌سرور.
set -eu

# docker-entrypoint.sh تصویر رسمی، setup را انجام می‌دهد و در پایان «exec "$@"» می‌کند؛
# با `true` فقط setup انجام و بلافاصله خارج می‌شود و ما کنترل را پس می‌گیریم.
/usr/local/bin/docker-entrypoint.sh true

/bin/sh /source/bin/bootstrap.sh

exec apache2-foreground
