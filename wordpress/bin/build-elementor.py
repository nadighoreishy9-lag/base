#!/usr/bin/env python3
"""Builds the Elementor page templates (native widgets) for the Nadia site.

Output: wordpress/elementor/01-home.json, 02-services.json, 03-portfolio.json
Elementor imports these through Templates -> Saved Templates -> Import.
"""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "wordpress/elementor")
IMG = "/wp-content/plugins/nadia-design/assets/images/"

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

def nav(active=""):
    def link(label, url):
        cls = "nd-menu-link" + (" nd-menu-link-active" if label == active else "")
        return button(label, url, cls)

    return container(
        "nd-header",
        [
            container(
                "nd-nav nd-glass",
                [
                    container(
                        "nd-brand",
                        [
                            heading("ن", "div", "nd-brand-mark", link="/"),
                            heading("نادیا قریشی", "div", "nd-brand-name", link="/"),
                        ],
                    ),
                    container(
                        "nd-menu",
                        [
                            link("خانه", "/"),
                            link("خدمات", "/services/"),
                            link("نمونه‌کار", "/portfolio/"),
                            link("رزومه", "/#resume"),
                            link("تماس", "/#contact"),
                        ],
                    ),
                    button("شروع گفتگو", "/#contact", "nd-btn nd-btn-dark nd-cta"),
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


def cta_box(title, body, primary, primary_url, ghost, ghost_url):
    return container(
        "nd-section",
        [
            container(
                "nd-contact-box nd-glass",
                [
                    container(
                        "nd-contact-inner",
                        [
                            heading(title, "h2", "nd-contact-title"),
                            text(f"<p>{body}</p>", "nd-contact-text"),
                            container(
                                "nd-contact-links",
                                [
                                    button(primary, primary_url, "nd-btn nd-btn-primary"),
                                    button(ghost, ghost_url, "nd-btn nd-btn-ghost"),
                                ],
                            ),
                        ],
                    )
                ],
            )
        ],
    )


# ---------------------------------------------------------------- کارت‌ها

def card(icon_name, title, body, tag=None, extra_cls=""):
    top = container(
        "nd-card-top",
        [icon(icon_name, "nd-card-icon"), heading(tag, "div", "nd-tag") if tag else None],
    )
    return container(f"nd-card nd-glass {extra_cls}".strip(), [top, heading(title, "h3", "nd-h3"), text(f"<p>{body}</p>", "nd-muted")])


def detail_card(icon_name, title, intro, items, deliverable, tag=None, lined=False):
    """کارت خدمات در صفحه «خدمات»."""
    bullets = "".join(f"<li>{i}</li>" for i in items)
    return container(
        f"nd-detail nd-glass{' nd-detail-lined' if lined else ''}",
        [
            container(
                "nd-card-top",
                [icon(icon_name, "nd-detail-icon"), heading(tag, "div", "nd-tag") if tag else None],
            ),
            heading(title, "h2", "nd-h3"),
            text(f"<p>{intro}</p>", "nd-muted"),
            text(f"<ul>{bullets}</ul>", "nd-list"),
            text(f'<p><span class="nd-strong">خروجی کار: </span>{deliverable}</p>', "nd-deliverable"),
        ],
    )


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


def work_card(img, alt, icon_name, tag, title, body, points):
    chips = "".join(f"<li>{p}</li>" for p in points)
    return container(
        "nd-work",
        [
            image(img, alt, "nd-work-img"),
            container(
                "nd-work-body",
                [
                    container(
                        "nd-work-meta",
                        [icon(icon_name, "nd-work-icon"), heading(tag, "div", "nd-work-tag")],
                    ),
                    heading(title, "h3", "nd-h3"),
                    text(f"<p>{body}</p>", "nd-muted"),
                    text(f"<ul>{chips}</ul>", "nd-chips"),
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
    return {
        "title": title,
        "type": "page",
        "version": "0.4",
        "page_settings": {"template": "elementor_canvas"},
        "content": [container("nd-page", [nav_for(title), *sections, footer()])],
    }


ACTIVE_BY_TITLE = {"خانه": "", "خدمات": "خدمات", "نمونه‌کارها": "نمونه‌کار"}


def nav_for(title):
    return nav(ACTIVE_BY_TITLE.get(title, ""))


# ---------------------------------------------------------------- خانه

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
                            button("دیدن نمونه‌کارها", "/portfolio/", "nd-btn nd-btn-primary"),
                            button("ارتباط با من", "/#contact", "nd-btn nd-btn-ghost"),
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
                    button("توضیح کامل هر خدمت", "/services/", "nd-link-btn"),
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
            container(
                "nd-cta-row",
                [button("مشاهده صفحه کامل نمونه‌کارها", "/portfolio/", "nd-btn nd-btn-primary")],
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
                    container("nd-band-btn", [button("درخواست رزومه کامل", "/#contact", "nd-btn nd-btn-light")]),
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
                                "<p>اگر برای همکاری، فرصت شغلی یا پروژه سئو و طراحی وب به دنبال همکاری دقیق و مسئولیت‌پذیر هستید، خوشحال می‌شوم بیشتر صحبت کنیم.</p>",
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


# ---------------------------------------------------------------- خدمات

seo_services = [
    (
        "fas fa-search",
        "بررسی و سئو فنی",
        "پیش از هر محتوایی، باید زیرساخت سایت اجازه دیده‌شدن بدهد. ساختار فنی، سرعت و ایندکس را بررسی می‌کنم تا مشخص شود دقیقاً چه چیزی مانع رتبه‌گیری است.",
        ["بررسی وضعیت ایندکس و خطاهای خزش", "ارزیابی سرعت بارگذاری و تجربه موبایل", "بررسی لینک‌سازی داخلی و ساختار URL", "بازبینی متادیتا و داده‌های ساختاریافته"],
        "فهرست اولویت‌بندی‌شده مشکلات فنی با توضیح ساده و راه‌حل هر کدام.",
    ),
    (
        "fas fa-crosshairs",
        "تحقیق کلمات کلیدی",
        "به‌جای حدس زدن، بررسی می‌کنم کاربران واقعاً چه عبارتی جست‌وجو می‌کنند و هر عبارت چه نیت پشت خود دارد؛ سپس آن را به نقشه‌ای برای صفحات سایت تبدیل می‌کنم.",
        ["تحلیل عبارت‌های جست‌وجوی مخاطب واقعی", "خوشه‌بندی موضوعی کلمات کلیدی", "بررسی نیت جست‌وجو (اطلاعاتی، خریداری، مقایسه‌ای)", "تحلیل رقبا برای پیدا کردن فرصت‌های خالی"],
        "نقشه کلمات کلیدی، خوشه‌بندی‌شده و متناسب با ساختار صفحات سایت.",
    ),
    (
        "fas fa-pen-nib",
        "بهینه‌سازی محتوا",
        "محتوای خوب باید هم برای کاربر خوانا باشد و هم پاسخگوی نیاز جست‌وجو. ساختار و متن صفحات را بازبینی می‌کنم تا هر دو هدف در کنار هم برآورده شوند.",
        ["بازنویسی و مرتب‌سازی عنوان‌ها و سرفصل‌ها", "بهبود ساختار H1 تا H3 و خوانایی متن", "بهینه‌سازی تصاویر و متن‌های جایگزین", "تکمیل نیت جست‌وجو در متن صفحه"],
        "نسخه اصلاح‌شده صفحات با ساختار بهینه و فهرست تغییرات انجام‌شده.",
    ),
    (
        "fas fa-chart-bar",
        "تحلیل و گزارش سئو",
        "بدون داده، سئو به حدس زدن تبدیل می‌شود. عملکرد جست‌وجو را زیر نظر می‌گیرم و آن را به گزارشی قابل فهم تبدیل می‌کنم که نشان دهد چه چیزی جواب داده و قدم بعدی چیست.",
        ["پایش ترافیک ارگانیک و رتبه کلمات کلیدی", "تحلیل رفتار کاربر در صفحات کلیدی", "تشخیص افت‌ها و فرصت‌های رشد", "ارائه گزارش دوره‌ای با زبان ساده"],
        "گزارش دوره‌ای عملکرد، همراه با اولویت‌بندی اقدام‌های بعدی.",
    ),
]

design_services = [
    (
        "fas fa-magic",
        "طراحی رابط وب",
        "صفحه‌ای که دیده شود اما کاربر در آن گم شود، نتیجه واقعی ندارد. رابط‌هایی تمیز و کاربردی طراحی می‌کنم که مسیر کاربر به مقصدش ساده باشد و با هویت کسب‌وکار هماهنگ بماند.",
        ["طراحی صفحات با سلسله‌مراتب بصری روشن", "کال‌تو‌اکشن‌های مشخص و کم‌تعداد", "هماهنگی رنگ، تایپوگرافی و هویت برند", "توجه به دسترس‌پذیری و خوانایی"],
        "طراحی صفحات آماده پیاده‌سازی، همراه با منطق چیدمان هر بخش.",
    ),
    (
        "fas fa-mobile-alt",
        "طراحی واکنش‌گرا",
        "بیشتر کاربران با موبایل وارد می‌شوند و گوگل هم سایت را با نگاه موبایل می‌سنجد. تجربه‌ای یکپارچه می‌سازم که در موبایل، تبلت و دسکتاپ همان کیفیت و سرعت را داشته باشد.",
        ["طراحی موبایل‌اول با جزئیات دقیق", "بهینه‌سازی سرعت در همه اندازه‌ها", "تنظیم فاصله‌ها و اندازه‌ها برای لمس راحت", "هماهنگی کامل سئو با تجربه موبایل"],
        "طراحی واکنش‌گرا با نمایش وضعیت در موبایل، تبلت و دسکتاپ.",
    ),
]

steps = [
    ("گفت‌وگوی اولیه", "وضعیت سایت، هدف و انتظار شما را می‌شنوم و مشخص می‌کنم کدام خدمت واقعاً لازم است."),
    ("بررسی و برنامه", "سایت و داده‌های موجود را بررسی می‌کنم و برنامه‌ای شفاف با اولویت‌های مشخص ارائه می‌دهم."),
    ("اجرا", "کار را مرحله‌به‌مرحله و مستند انجام می‌دهم و در جریان بودن تغییرات، جایی برای ابهام نمی‌گذارم."),
    ("تحویل و پیگیری", "خروجی را با توضیح ساده تحویل می‌دهم و برای پایش نتیجه و بهبود ادامه‌دار کنار می‌مانم."),
]


def divider(label):
    return container(
        "nd-divider",
        [container("nd-divider-line"), heading(label, "div", "nd-divider-label"), container("nd-divider-line")],
    )


def services_page():
    hero = container(
        "nd-page-hero",
        [
            heading("خدمات و تخصص‌ها", "p", "nd-eyebrow"),
            heading('هر خدمت، پاسخ به یک <span class="nd-accent">نیاز مشخص</span>', "h1", "nd-page-title"),
            text(
                "<p>تمرکز اصلی من روی سئو است؛ اما چون طراحی وب هم کار می‌کنم، راهکارهایم فقط فنی نیستند و با تجربه کاربر هماهنگ‌اند. در ادامه هر تخصص را با جزئیات توضیح داده‌ام.</p>",
                "nd-muted",
            ),
        ],
    )

    seo = container(
        "nd-section",
        [
            divider("خدمات سئو — تمرکز اصلی"),
            container(
                "nd-grid nd-grid-2",
                [detail_card(*item, tag="تمرکز اصلی", lined=True) for item in seo_services],
            ),
        ],
    )

    design = container(
        "nd-section",
        [
            divider("خدمات طراحی وب"),
            container("nd-grid nd-grid-2", [detail_card(*item) for item in design_services]),
        ],
    )

    process = container(
        "nd-section",
        [
            container(
                "nd-process",
                [
                    container(
                        "nd-section-head",
                        [
                            heading("روند همکاری", "p", "nd-eyebrow"),
                            heading("مسیر کار از اولین گفت‌وگو تا تحویل", "h2", "nd-h2"),
                            text(
                                "<p>برای هر خدمت، همین روند ساده را طی می‌کنم تا از ابتدا بدانید چه انتظاری داشته باشید؛ بدون وعده‌های غیرواقعی و بدون گام‌های اضافه.</p>",
                                "nd-muted",
                            ),
                        ],
                    ),
                    container(
                        "nd-steps",
                        [
                            container(
                                "nd-step-card nd-glass",
                                [
                                    heading(str(i + 1), "div", "nd-step-badge"),
                                    heading(title, "h3", "nd-h3"),
                                    text(f"<p>{body}</p>", "nd-muted"),
                                ],
                            )
                            for i, (title, body) in enumerate(steps)
                        ],
                    ),
                ],
            )
        ],
    )

    cta = cta_box(
        "کدام خدمت به کار شما می‌آید؟",
        "اگر مطمئن نیستید از کجا شروع کنید، وضعیت سایت و هدف‌تان را برایم بنویسید؛ بررسی می‌کنم و صادقانه می‌گویم چه چیزی لازم دارید و چه چیزی لازم نیست.",
        "درخواست این خدمات",
        "/#contact",
        "دیدن نمونه‌کارها",
        "/portfolio/",
    )

    return page("خدمات", [hero, seo, design, process, cta])


# ---------------------------------------------------------------- نمونه‌کارها

filters = ["سئو فنی", "تحقیق کلمات کلیدی", "بهینه‌سازی محتوا", "طراحی رابط", "طراحی واکنش‌گرا"]

featured_points = [
    "ساختاردهی دسته‌بندی‌ها و لینک‌سازی داخلی",
    "بهینه‌سازی عنوان، توضیحات و داده ساختاریافته محصول",
    "بهبود سرعت بارگذاری و تجربه موبایل",
]

works = [
    ("work-analytics.jpg", "داشبورد تحلیل و گزارش سئو روی نمایشگر", "fas fa-chart-bar", "تحلیل و گزارش سئو", "داشبورد تحلیل عملکرد جست‌وجو", "پایش رتبه‌ها، ترافیک ارگانیک و صفحات کلیدی و تبدیل داده‌ها به گزارشی قابل فهم برای تصمیم‌گیری.", ["گزارش ماهانه", "پایش کلمات کلیدی", "اولویت‌بندی اقدام‌ها"]),
    ("work-blog.jpg", "نمونه طراحی وب‌سایت محتوایی و مجله‌ای", "fas fa-search", "استراتژی محتوا · سئو", "وب‌سایت محتوایی و مجله‌ای", "معماری محتوا بر پایه نیت جست‌وجوی کاربر، همراه با طراحی خوانا برای مقاله‌های بلند.", ["خوشه‌بندی موضوعی", "ساختار تیترها", "لینک داخلی مقاله‌ها"]),
    ("work-responsive.jpg", "نمایش سایت شرکتی روی موبایل و تبلت", "fas fa-mobile-alt", "طراحی واکنش‌گرا", "سایت شرکتی در موبایل و تبلت", "طراحی یکپارچه در همه اندازه‌ها با توجه به سرعت، خوانایی و مسیر تماس کاربر.", ["اولویت موبایل", "سرعت بارگذاری", "دسترس‌پذیری"]),
    ("project-corporate.jpg", "نمونه طراحی صفحه خدمات سایت شرکتی", "fas fa-layer-group", "طراحی وب · سئو فنی", "صفحه خدمات شرکتی", "ساختاردهی معرفی خدمات با چینش روشن و پایه‌های فنی سئو برای ایندکس بهتر صفحات.", ["ساختار صفحه", "متادیتای صفحه", "ناوبری روشن"]),
    ("project-ecommerce.jpg", "نمونه طراحی صفحه محصول فروشگاه اینترنتی", "fas fa-search", "سئو فروشگاهی", "بهینه‌سازی صفحه محصول", "بازبینی عنوان، توضیحات و بخش نقد و بررسی برای پاسخ کامل‌تر به پرسش خریدار.", ["توضیح محصول", "داده ساختاریافته", "تجربه خرید"]),
    ("work-shop.jpg", "نمونه طراحی صفحه اصلی فروشگاه اینترنتی", "fas fa-layer-group", "طراحی رابط", "صفحه اصلی فروشگاهی", "چیدمان بنرها، دسته‌بندی‌ها و پیشنهادهای ویژه برای هدایت سریع کاربر به محصول درست.", ["سلسله‌مراتب بصری", "کال‌تو‌اکشن روشن", "هویت رنگی"]),
]


def portfolio_page():
    hero = container(
        "nd-page-hero",
        [
            heading("نمونه‌کارها", "p", "nd-eyebrow"),
            heading('کارهایی که ترکیب <span class="nd-accent">سئو</span> و طراحی را نشان می‌دهند', "h1", "nd-page-title"),
            text(
                "<p>در هر نمونه، رویکرد کار، کارهایی که انجام شده و نکته‌های سئویی آن را آورده‌ام. تصاویر برای نمایش فضای پروژه‌ها هستند و با ارسال فایل‌های واقعی شما جایگزین می‌شوند.</p>",
                "nd-muted",
            ),
            container("nd-filters", [heading(f, "div", "nd-filter") for f in filters]),
        ],
    )

    featured = container(
        "nd-section",
        [
            container(
                "nd-featured",
                [
                    image(IMG + "work-shop.jpg", "نمونه طراحی و سئوی فروشگاه اینترنتی روی نمایشگر لپ‌تاپ", "nd-featured-img"),
                    container(
                        "nd-featured-body",
                        [
                            heading("پروژه شاخص", "div", "nd-badge-accent"),
                            heading("فروشگاه اینترنتی چنددسته‌ای", "h2", "nd-h2"),
                            text(
                                "<p>بازطراحی صفحه اصلی و صفحات دسته‌بندی با تمرکز بر مسیر ساده خرید، همراه با ساختار لینک داخلی و عنوان‌های بهینه برای صفحات محصول.</p>",
                                "nd-muted",
                            ),
                            text("<ul>" + "".join(f"<li>{p}</li>" for p in featured_points) + "</ul>", "nd-points"),
                        ],
                    ),
                ],
            )
        ],
    )

    grid = container(
        "nd-section",
        [container("nd-grid nd-grid-2", [work_card(IMG + img, alt, ic, tag, title, body, points) for img, alt, ic, tag, title, body, points in works])],
    )

    cta = cta_box(
        "پروژه بعدی می‌تواند مال شما باشد",
        "اگر سایتی دارید که باید بهتر دیده شود یا نیاز به طراحی تازه دارد، جزئیات را برایم بفرستید تا مسیر کار را شفاف توضیح دهم.",
        "ارتباط با من",
        "/#contact",
        "بازگشت به صفحه اصلی",
        "/",
    )

    return page("نمونه‌کارها", [hero, featured, grid, cta])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pages = [("01-home.json", home_page()), ("02-services.json", services_page()), ("03-portfolio.json", portfolio_page())]
    for name, data in pages:
        path = OUT / name
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{path}  {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
