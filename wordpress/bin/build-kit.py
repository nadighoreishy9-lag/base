#!/usr/bin/env python3
"""عنوان صفحه‌های کیت المنتور را به معادل لاتین تغییر می‌دهد.

المنتور هنگام ایمپورت، «نامک» (slug) هر صفحه را از عنوان آن می‌سازد. عنوان فارسی
نامک فارسی (درصدی) می‌سازد که با لینک‌های منوی سایت (‎/services/‎ و ‎/portfolio/‎)
هم‌خوان نیست و منو به صفحه ۴۰۴ می‌رود. این اسکریپت عنوان صفحه‌ها را در manifest به
معادل لاتین برمی‌گرداند تا نامک درست ساخته شود.

اجرا:
    python3 wordpress/bin/build-kit.py <kit-exported.zip> <nadia-elementor-kit.zip>
"""
import json
import sys
import zipfile
from pathlib import Path
from urllib.parse import urlparse

# آخرین بخش آدرس صفحه → نامک مورد انتظار
SLUG_BY_PATH = {"": "home", "services": "services", "portfolio": "portfolio"}


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])

    with zipfile.ZipFile(src) as zin:
        names = zin.namelist()
        files = {name: zin.read(name) for name in names}

    manifest = json.loads(files["manifest.json"])
    for page in manifest.get("content", {}).get("page", {}).values():
        last = urlparse(page.get("url", "")).path.strip("/")
        slug = SLUG_BY_PATH.get(last)
        if slug:
            page["title"] = slug.capitalize()
    files["manifest.json"] = json.dumps(manifest, ensure_ascii=False).encode("utf-8")

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            zout.writestr(name, files[name])

    print(f"{dst}  {dst.stat().st_size} bytes")


if __name__ == "__main__":
    main()
