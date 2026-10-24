#!/usr/bin/env python3
"""Builds the Elementor page template (native widgets) for the Nadia site.

Output: wordpress/elementor/01-home.json
Elementor imports this through Templates -> Saved Templates -> Import.

The site is a single page, like the Lovable design source: hero + services +
portfolio + résumé band + contact, all on one page. The header menu therefore
links to in-page anchors (#top / #services / #portfolio / #contact).
"""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "wordpress/elementor")
IMG = "/wp-content/plugins/nadia-design/assets/images/"

# استایل‌ها داخل خود صفحه تزریق نمی‌شوند: وردپرس محتوای صفحه‌های المنتور را هنگام ذخیره
# با wp_kses_post پاکسازی می‌کند و اگر کاربر مجوز unfiltered_html نداشته باشد (مولتی‌سایت،
# هاست‌های سخت‌گیر یا حساب غیرمدیر) تگ <style> حذف می‌شود و متن CSS به‌صورت متن خام روی
# صفحه می‌ماند. بنابراین CSS از فایل nadia.css بارگذاری می‌شود (افزونه nadia-design یا
# «ظاهر → سفارشی‌سازی → CSS افزودنی»).
LOVABLE_ASSETS = "https://nadiaghoeyshi.lovable.app/assets/"
IMG_MAP = {
    "nadia-portrait.jpg": LOVABLE_ASSETS + "nadia-portrait-faTNC5M7.jpg",
    "project-content.jpg": LOVABLE_ASSETS + "project-content-CdsveXjx.jpg",
    "project-corporate.jpg": LOVABLE_ASSETS + "project-corporate-DApRPBWH.jpg",
    "project-ecommerce.jpg": LOVABLE_ASSETS + "project-ecommerce-Ozm8DC6S.jpg",
}

_counter = 0


def eid() -> str:
    global _counter
    _counter += 1
    return f"{_counter:07x}"


def container(cls=None, children=None, depth=0, **settings):
    s = {"content_width": "full"}
    if cls:
        # کانتینرها در المنتور ۳.۱۶+ از css_classes و نسخه‌های قدیمی‌تر از _css_classes
        # استفاده می‌کنند؛ هر دو را ست می‌کنیم تا مستقل از نسخه کار کند.
        s["css_classes"] = cls
        s["_css_classes"] = cls
    s.update(settings)
    return {
        "id": eid(),
        "elType": "container",
        "settings": s,
        "elements": [c for c in (children or []) if c],
        "isInner": depth > 0,
    }


def widget(wtype, settings, cls=None):
    s = dict(settings)
    if cls:
        # ویجت‌ها کلاس را از کنترل _css_classes می‌خوانند.
        s["_css_classes"] = cls
        s["css_classes"] = cls
    return {"id": eid(), "elType": "widget", "widgetType": wtype, "settings": s, "elements": []}


def rewrite_image_urls(node):
    """آدرس تصاویر افزونه را با آدرس عمومی طراحی جایگزین می‌کند."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "url" and isinstance(value, str) and value.startswith(IMG):
                node[key] = IMG_MAP.get(value[len(IMG):], value)
            else:
                rewrite_image_urls(value)
    elif isinstance(node, list):
        for item in node:
            rewrite_image_urls(item)


def heading(title, tag="h2", cls=None, link=None):
    s = {"title": title, "header_size": tag}
    if link:
        s["link"] = {"url": link, "is_external": "", "nofollow": ""}
    return widget("heading", s, cls)


def text(html, cls=None):
    return widget("text-editor", {"editor": html}, cls)


def image(url, alt, cls=None):
    return widget(
        "image",
        {"image": {"url": url, "id": "", "alt": alt, "source": "library"}, "image_size": "full"},
        cls,
    )


def button(label, url, cls=None):
    return widget("button", {"text": label, "link": {"url": url, "is_external": "", "nofollow": ""}}, cls)


def icon(name, cls=None):
    return widget("icon", {"selected_icon": {"value": name, "library": "fa-solid"}, "view": "default"}, cls)


# ---------------------------------------------------------------- سربرگ و فوتر

def nav():
    """منوی سربرگ: سایت تک‌صفحه‌ای است، پس همه لینک‌ها لنگرهای همین صفحه‌اند."""

    def link(label, url):
        return button(label, url, "nd-menu-link")

    return container(
        "nd-header",
        [
            container(
                "nd-nav nd-glass",
                [
                    container(
                        "nd-brand",
                        [
                            heading("ن", "div", "nd-brand-mark", link="#top"),
                            heading("نادیا قریشی", "div", "nd-brand-name", link="#top"),
                        ],
                    ),
                    container(
                        "nd-menu",
                        [
                            link("خانه", "#top"),
                            link("خدمات", "#services"),
                            link("نمونه‌کار", "#portfolio"),
                            link("تماس", "#contact"),
                        ],
                    ),
                    button("شروع گفتگو", "#contact", "nd-btn nd-btn-dark nd-cta"),
                ],
            )
        ],
    )


def footer():
    return container(
        "nd-footer",
        [
            heading("© ۱۴۰۵ نادیا قریشی", "div"),
            heading("سئو با نگاه طراحی؛ طراحی با فکر دیده‌شدن", "div"),
        ],
    )


# ---------------------------------------------------------------- کارت‌ها

def card(icon_name, title, body, tag=None, extra_cls=""):
    top = container(
        "nd-card-top",
        [icon(icon_name, "nd-card-icon"), heading(tag, "div", "nd-tag") if tag else None],
    )
    return container(f"nd-card nd-glass {extra_cls}".strip(), [top, heading(title, "h3", "nd-h3"), text(f"<p>{body}</p>", "nd-muted")])


def project_card(img, alt, kind, title, body):
    return container(
        "nd-project",
        [
            image(img, alt, "nd-project-img"),
            container(
                "nd-project-body",
                [
                    container(
                        "nd-project-meta",
                        [heading(kind, "div", "nd-project-type"), icon("fas fa-arrow-up", "nd-project-arrow")],
                    ),
                    heading(title, "h3", "nd-h3"),
                    text(f"<p>{body}</p>", "nd-muted"),
                ],
            ),
        ],
    )


def timeline_item(number, label, title, body):
    return container(
        "nd-timeline-item",
        [
            heading(str(number), "div", "nd-step-num"),
            container(
                "nd-timeline-body",
                [heading(label, "div", "nd-step-label"), heading(title, "h3"), text(f"<p>{body}</p>", "nd-muted")],
            ),
        ],
    )


def page(title, sections):
    content = container("nd-page", [nav(), *sections, footer()])
    data = {
        "title": title,
        "type": "page",
        "version": "0.4",
        "page_settings": {"template": "elementor_canvas"},
        "content": [content],
    }
    rewrite_image_urls(data)
    return data


# ---------------------------------------------------------------- محتوای صفحه

home_services = [
    ("fas fa-search", "بررسی و سئو فنی", "بررسی ساختار، سرعت، ایندکس، لینک‌های داخلی و خطاهایی که مانع دیده‌شدن سایت می‌شوند.", True),
    ("fas fa-crosshairs", "تحقیق کلمات کلیدی", "شناخت جست‌وجوهای واقعی مخاطب و تبدیل آن‌ها به نقشه‌ای روشن برای صفحات و محتوا.", True),
    ("fas fa-chart-bar", "تحلیل و گزارش سئو", "بررسی داده‌ها و ارائه گزارش قابل فهم برای تشخیص فرصت‌ها و اولویت‌بندی قدم‌های بعدی.", True),
    ("fas fa-magic", "بهینه‌سازی محتوا", "بازبینی ساختار و متن صفحات برای پاسخ بهتر به نیاز کاربر و استانداردهای موتورهای جست‌وجو.", False),
    ("fas fa-code", "طراحی رابط وب", "طراحی صفحات تمیز، کاربردی و هماهنگ با هویت کسب‌وکار با تمرکز بر مسیر ساده کاربر.", False),
    ("fas fa-arrow-up", "طراحی واکنش‌گرا", "ساخت تجربه‌ای یکپارچه و خوانا در موبایل، تبلت و دسکتاپ با جزئیات دقیق.", False),
]

home_projects = [
    ("project-ecommerce.jpg", "نمونه نمایشی طراحی فروشگاه اینترنتی", "سئو فروشگاهی · طراحی", "فروشگاه اینترنتی", "نمونه‌ای برای نمایش بررسی ساختار دسته‌بندی، صفحات محصول و تجربه خرید."),
    ("project-content.jpg", "نمونه نمایشی وب‌سایت محتوایی", "استراتژی محتوا · سئو", "وب‌سایت محتوایی", "نمونه‌ای برای نمایش معماری محتوا، تحقیق کلمات کلیدی و بهینه‌سازی مقاله‌ها."),
    ("project-corporate.jpg", "نمونه نمایشی طراحی سایت شرکتی", "طراحی وب · سئو فنی", "وب‌سایت شرکتی", "نمونه‌ای برای نمایش طراحی رابط، ساختار خدمات و پایه‌های فنی سئو."),
]

home_resume = [
    ("تخصص اصلی", "یادگیری و اجرای پروژه‌های سئو", "تمرکز روی اصول سئو فنی، تحقیق کلمات کلیدی، تحلیل رقبا و بهینه‌سازی محتوا با رویکرد مسئله‌محور."),
    ("مهارت مکمل", "طراحی وب و رابط کاربری", "طراحی صفحات واکنش‌گرا و قابل استفاده با توجه هم‌زمان به نیاز کاربر و قابلیت دیده‌شدن در جست‌وجو."),
    ("رویکرد کاری", "یادگیری مستمر و اجرای مسئولانه", "به‌جای وعده‌های بزرگ، روی ارتباط شفاف، مستندسازی و بهبود پیوسته کیفیت کار تمرکز دارم."),
]


def home_page():
    hero = container(
        "nd-hero",
        [
            container(
                "nd-hero-copy nd-reveal",
                [
                    container("nd-kicker", [heading("سئو، طراحی و تجربه بهتر وب", "div", "nd-kicker-text")]),
                    heading("سلام، من نادیا هستم.", "p", "nd-hello"),
                    heading(
                        'کمک می‌کنم سایت‌ها <span class="nd-accent">بهتر دیده شوند</span> و بهتر کار کنند.',
                        "h1",
                        "nd-hero-title",
                    ),
                    text(
                        "<p>کارشناس سئو و طراح وب هستم. تمرکز اصلی من روی بهینه‌سازی اصولی سایت برای موتورهای جست‌وجو است و نگاه طراحی کمک می‌کند راهکارهایم فقط فنی نباشند؛ بلکه برای کاربر هم ساده و دلنشین باشند.</p>",
                        "nd-lead",
                    ),
                    container(
                        "nd-actions",
                        [
                            button("دیدن نمونه‌کارها", "#portfolio", "nd-btn nd-btn-primary"),
                            button("ارتباط با من", "#contact", "nd-btn nd-btn-ghost"),
                        ],
                    ),
                ],
            ),
            container(
                "nd-portrait-wrap nd-reveal nd-reveal-delay",
                [
                    container(
                        "nd-portrait-card nd-glass",
                        [
                            image(IMG + "nadia-portrait.jpg", "پرتره نادیا قریشی، کارشناس سئو و طراح وب", "nd-portrait-img"),
                            container(
                                "nd-portrait-caption",
                                [
                                    heading("آماده همکاری پروژه‌ای", "div", "nd-caption-strong"),
                                    heading("ایران", "div", "nd-caption-muted"),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
        _element_id="top",
    )

    services = container(
        "nd-section nd-surface",
        [
            container(
                "nd-section-head",
                [
                    heading("خدمات و تخصص‌ها", "p", "nd-eyebrow"),
                    heading("از پیدا شدن در جست‌وجو تا تجربه‌ای که در ذهن می‌ماند", "h2", "nd-h2"),
                    text("<p>هر پروژه را بر اساس نیاز واقعی آن بررسی می‌کنم؛ بدون نسخه آماده و وعده‌های غیرواقعی.</p>", "nd-muted"),
                ],
            ),
            container(
                "nd-grid nd-grid-3",
                [card(name, title, body, "تمرکز اصلی" if tag else None) for name, title, body, tag in home_services],
            ),
        ],
        _element_id="services",
    )

    portfolio = container(
        "nd-section",
        [
            container(
                "nd-head-row",
                [
                    container(
                        "nd-head-main",
                        [
                            heading("نمونه‌کارها", "p", "nd-eyebrow"),
                            heading("چند مسیر برای نمایش توانمندی‌ها", "h2", "nd-h2"),
                        ],
                    ),
                    text("<p>این بخش فعلاً با نمونه‌های نمایشی آماده شده تا بعداً پروژه‌های واقعی، نقش شما و نتیجه هر پروژه جایگزین شوند.</p>", "nd-head-aside"),
                ],
            ),
            container(
                "nd-grid nd-grid-3",
                [project_card(IMG + img, alt, kind, title, body) for img, alt, kind, title, body in home_projects],
            ),
        ],
        _element_id="portfolio",
    )

    resume = container(
        "nd-band",
        [
            container(
                "nd-band-left",
                [
                    heading("مسیر حرفه‌ای", "p", "nd-band-eyebrow"),
                    heading("در حال ساختن یک مسیر دقیق و ماندگار", "h2", "nd-h2"),
                    text(
                        "<p>تجربه‌ام را قدم‌به‌قدم با یادگیری مستمر و پروژه‌های واقعی گسترش می‌دهم. برای من کیفیت اجرا و مسئولیت‌پذیری مهم‌تر از ادعاهای بزرگ است.</p>",
                        "nd-band-text",
                    ),
                    container("nd-band-btn", [button("درخواست رزومه کامل", "#contact", "nd-btn nd-btn-light")]),
                ],
            ),
            container("nd-timeline", [timeline_item(i + 1, *item) for i, item in enumerate(home_resume)]),
        ],
        _element_id="resume",
    )

    contact = container(
        "nd-section",
        [
            container(
                "nd-contact-box nd-glass",
                [
                    container(
                        "nd-contact-inner",
                        [
                            icon("fas fa-envelope", "nd-contact-icon"),
                            heading("برای یک گفت‌وگوی حرفه‌ای آماده‌ام", "h2", "nd-contact-title"),
                            text(
                                "<p>اگر برای همکاری، فرصت شغلی یا پروژه سئو و طراحی وب به دنبال همراهی دقیق و مسئولیت‌پذیر هستید، خوشحال می‌شوم بیشتر صحبت کنیم.</p>",
                                "nd-contact-text",
                            ),
                            container(
                                "nd-contact-links",
                                [
                                    heading("ایمیل: در انتظار تکمیل", "div", "nd-chip nd-chip-primary"),
                                    heading("لینکدین: در انتظار تکمیل", "div", "nd-chip"),
                                    heading("تلگرام: در انتظار تکمیل", "div", "nd-chip"),
                                ],
                            ),
                        ],
                    )
                ],
            )
        ],
        _element_id="contact",
    )

    return page("خانه", [hero, services, portfolio, resume, contact])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "01-home.json"
    path.write_text(json.dumps(home_page(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{path}  {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
