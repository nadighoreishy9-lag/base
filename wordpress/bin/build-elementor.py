#!/usr/bin/env python3
"""Builds the Elementor page template (native widgets + native layout) for the Nadia site.

Output: wordpress/elementor/01-home.json
Elementor imports this through Templates -> Saved Templates -> Import.

**چیدمان همه‌جا با خود المنتور ساخته می‌شود**: کانتینرها (flex/grid، جهت، wrap، ترازبندی،
gap، عرض، پدینگ/مارجین، رنگ، حاشیه، سایه، گردی گوشه) و ویجت‌ها (تایپوگرافی، رنگ، پس‌زمینه،
حاشیه، انیمیشن ورود) همه با کنترل‌های خود المنتور تنظیم شده‌اند تا از داخل ویرایشگر
قابل تغییر باشند. فایل `nadia.css` فقط چیزهایی را دارد که المنتور کنترلش را ندارد
(فونت، راست‌به‌چپ، backdrop-filter، هاله‌های تزئینی، نسبت تصویر، هاور تصویر).

The site is a single page, like the Lovable design source: hero + services +
portfolio + résumé band + contact, all on one page. The header menu therefore
links to in-page anchors (#top / #services / #portfolio / #contact).
"""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "wordpress/elementor")
IMG = "/wp-content/plugins/nadia-design/assets/images/"

LOVABLE_ASSETS = "https://nadiaghoeyshi.lovable.app/assets/"
IMG_MAP = {
    "nadia-portrait.jpg": LOVABLE_ASSETS + "nadia-portrait-faTNC5M7.jpg",
    "project-content.jpg": LOVABLE_ASSETS + "project-content-CdsveXjx.jpg",
    "project-corporate.jpg": LOVABLE_ASSETS + "project-corporate-DApRPBWH.jpg",
    "project-ecommerce.jpg": LOVABLE_ASSETS + "project-ecommerce-Ozm8DC6S.jpg",
}

# ---------------------------------------------------------------- توکن‌های طراحی
# معادل hex رنگ‌های oklch دیزاین‌سیستم لاویبل (کنترل رنگ المنتور hex/rgba می‌گیرد).
BG = "#F6F6FD"
FG = "#141425"
PRIMARY = "#6440B8"
PRIMARY_FG = "#FAFAFD"
SECONDARY = "#E1DEF7"
SECONDARY_FG = "#2F2452"
ACCENT = "#A7DDDF"
ACCENT_FG = "#00272F"
BORDER = "#D6D5E8"
BORDER_SOFT = "rgba(214, 213, 232, 0.72)"
SURFACE = "rgba(255, 255, 255, 0.66)"
CARD = "rgba(255, 255, 255, 0.78)"
MUTED = "#606174"
CYAN = "#36B8C5"
ON_DARK_70 = "rgba(246, 246, 253, 0.7)"
ON_DARK_65 = "rgba(246, 246, 253, 0.65)"
ON_DARK_55 = "rgba(246, 246, 253, 0.55)"
ON_DARK_15 = "rgba(246, 246, 253, 0.15)"
ON_DARK_05 = "rgba(246, 246, 253, 0.05)"
TRANSPARENT = "rgba(0, 0, 0, 0)"
SHADOW_SOFT = "0 24px 70px -32px rgba(20, 20, 37, 0.2)"
SHADOW_VIOLET = "0 24px 70px -34px rgba(128, 95, 218, 0.38)"
FONT = "Vazirmatn"
SHELL = 1200  # عرض جعبه؛ با پدینگ ۲۴px کناری → محتوای ۱۱۵۲px (همان 72rem)

_counter = 0


def eid() -> str:
    global _counter
    _counter += 1
    return f"{_counter:07x}"


# ---------------------------------------------------------------- سازنده‌های تنظیمات

def w(size, unit="px"):
    """مقدار اسلایدر (عرض، ارتفاع، اندازه آیکون، فاصله…)."""
    return {"unit": unit, "size": size}


def dim(top=None, right=None, bottom=None, left=None, unit="px"):
    """مقدار Dimensions (پدینگ، مارجین، گردی گوشه، ضخامت حاشیه)."""
    value = {"unit": unit, "isLinked": False}
    for key, val in (("top", top), ("right", right), ("bottom", bottom), ("left", left)):
        if val is not None:
            value[key] = str(val)
    return value


def gap(row, column=None, unit="px"):
    """مقدار Gaps کانتینر (flex/grid)."""
    column = row if column is None else column
    return {"column": str(column), "row": str(row), "isLinked": column == row, "unit": unit}


def typo(size=None, size_tablet=None, size_mobile=None, weight=None, height=None,
         line_unit="em", unit="px", transform=None):
    s = {"typography_typography": "custom", "typography_font_family": FONT}
    if size is not None:
        s["typography_font_size"] = {"unit": unit, "size": size}
    if size_tablet is not None:
        s["typography_font_size_tablet"] = {"unit": unit, "size": size_tablet}
    if size_mobile is not None:
        s["typography_font_size_mobile"] = {"unit": unit, "size": size_mobile}
    if weight is not None:
        s["typography_font_weight"] = str(weight)
    if height is not None:
        s["typography_line_height"] = {"unit": line_unit, "size": height}
    if transform:
        s["typography_text_transform"] = transform
    return s


def radius(value):
    return {"border_radius": dim(value, value, value, value)}


def bg(color):
    return {"background_background": "classic", "background_color": color}


def border(color=BORDER, width=1, sides=(1, 1, 1, 1), style="solid"):
    return {
        "border_border": style,
        "border_width": dim(sides[0], sides[1], sides[2], sides[3], unit="px") if width == 1 else
        dim(*[width if s else 0 for s in sides]),
        "border_color": color,
    }


def shadow(value=SHADOW_SOFT):
    h, v, blur, spread, color = _parse_shadow(value)
    return {
        "box_shadow_box_shadow_type": "yes",
        "box_shadow_box_shadow": {"horizontal": h, "vertical": v, "blur": blur, "spread": spread, "color": color},
    }


def _parse_shadow(value):
    """'0 24px 70px -32px rgba(...)' → (0, 24, 70, -32, 'rgba(...)')"""
    numbers, color = value.split("rgba(", 1)
    color = "rgba(" + color
    parts = numbers.split()
    return (int(float(parts[0].replace("px", ""))), int(float(parts[1].replace("px", ""))),
            int(float(parts[2].replace("px", ""))), int(float(parts[3].replace("px", ""))), color)


# ---------------------------------------------------------------- سازنده‌های المان

def container(children=None, cls=None, inner=True, **settings):
    s = {
        "content_width": "full",
        "container_type": "flex",
        "flex_direction": "column",
        "flex_gap": gap(0),
        "padding": dim(0, 0, 0, 0),
    }
    if cls:
        # کانتینرها در نسخه‌های مختلف از css_classes و _css_classes استفاده می‌کنند؛
        # هر دو را ست می‌کنیم تا مستقل از نسخه کار کند.
        s["css_classes"] = cls
        s["_css_classes"] = cls
    s.update(settings)
    return {
        "id": eid(),
        "elType": "container",
        "settings": s,
        "elements": [c for c in (children or []) if c],
        "isInner": inner,
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


def heading(title, tag="h2", cls=None, link=None, color=None, align=None, mt=None, extra=None, **typo_kw):
    s = {"title": title, "header_size": tag}
    if link:
        s["link"] = {"url": link, "is_external": "", "nofollow": ""}
    if color:
        s["title_color"] = color
    if align:
        s["align"] = align
    if mt is not None:
        s["_margin"] = dim(mt, 0, 0, 0)
    s.update(typo(**typo_kw))
    if extra:
        s.update(extra)
    return widget("heading", s, cls)


def text(html, cls=None, color=MUTED, align=None, mt=None, **typo_kw):
    s = {"editor": html}
    if color:
        s["text_color"] = color
    if align:
        s["align"] = align
    if mt is not None:
        s["_margin"] = dim(mt, 0, 0, 0)
    s.update(typo(**typo_kw))
    return widget("text-editor", s, cls)


def image(url, alt, cls=None, width=None, radius_=None):
    s = {"image": {"url": url, "id": "", "alt": alt, "source": "library"}, "image_size": "full"}
    if width is not None:
        s["width"] = {"unit": "%", "size": width}
    if radius_ is not None:
        s["image_border_radius"] = dim(radius_, radius_, radius_, radius_)
    return widget("image", s, cls)


def button(label, url, cls=None, bgc=PRIMARY, fg=PRIMARY_FG, radius_=12, pad=(14, 24, 14, 24),
           size=16, weight=700, height=1.6, border_color=None, hover_color=None,
           hover_bg=None, extra=None):
    s = {
        "text": label,
        "link": {"url": url, "is_external": "", "nofollow": ""},
        "background_background": "classic",
        "background_color": bgc,
        "button_text_color": fg,
        "border_radius": dim(radius_, radius_, radius_, radius_),
        "text_padding": dim(*pad),
    }
    if border_color:
        s.update({"border_border": "solid", "border_width": dim(1, 1, 1, 1), "border_color": border_color})
    if hover_color:
        s["hover_color"] = hover_color
    if hover_bg:
        s["button_background_hover_background"] = "classic"
        s["button_background_hover_color"] = hover_bg
    s.update(typo(size=size, weight=weight, height=height))
    if extra:
        s.update(extra)
    return widget("button", s, cls)


def icon(name, cls=None, color=PRIMARY, size=20):
    return widget("icon", {
        "selected_icon": {"value": name, "library": "fa-solid"},
        "view": "default",
        "primary_color": color,
        "size": w(size),
    }, cls)


def icon_chip(name, cls=None, bgc=SECONDARY, color=PRIMARY, size=20, box=44, radius_=12):
    """آیکون داخل مربع گرد رنگی — کانتینر نیتیو، نه CSS."""
    return container(
        [icon(name, color=color, size=size)],
        cls,
        flex_direction="row", flex_justify_content="center", flex_align_items="center",
        width=w(box), min_height=w(box),
        **bg(bgc), **radius(radius_),
    )


def badge(title, cls=None, bgc=ACCENT, fgc=ACCENT_FG, size=12, weight=700, radius_=999,
          pad=(4, 12, 4, 12), border_color=None):
    """برچسب/چیپ — ویجت heading با پس‌زمینه و گردی گوشهٔ نیتیو المنتور."""
    extra = {
        "_background_background": "classic",
        "_background_color": bgc,
        "_border_radius": dim(radius_, radius_, radius_, radius_),
        "_padding": dim(*pad),
    }
    if border_color:
        extra.update({"_border_border": "solid", "_border_width": dim(1, 1, 1, 1), "_border_color": border_color})
    return heading(title, "div", cls, color=fgc, size=size, weight=weight, extra=extra)


def boxed(children, cls=None, pad=24, **settings):
    """محتوای وسط‌چین: عرض محدود + پدینگ کناری؛ والدش با align-items:center وسطش می‌چیند.

    عمداً از content_width «full» استفاده می‌کنیم نه «boxed»: المنتور تنظیمات flex
    (جهت/ترازبندی/gap) را فقط روی کانتینرهای full اعمال می‌کند و کانتینر boxed را
    همیشه ستون با justify-content:normal می‌کند.
    """
    return container(
        children, cls,
        width={"unit": "custom", "size": f"min(100%, {SHELL}px)"}, _flex_size="none",
        padding=dim(0, pad, 0, pad),
        **settings,
    )


def section(children, cls=None, element_id=None, surface=False, **settings):
    """بخش تمام‌عرض با پدینگ عمودی؛ محتوای وسط‌چین داخل آن."""
    s = {"flex_direction": "column", "flex_align_items": "center", "padding": dim(96, 0, 96, 0)}
    if surface:
        s.update(bg(SURFACE))
        s.update(border(BORDER, sides=(1, 0, 1, 0)))
    s.update(settings)
    outer = container(
        [boxed(children, flex_direction="column", flex_gap=gap(48))],
        cls, _element_id=element_id, **s,
    )
    return outer


def grid(children, columns=3, tablet=None, mobile=1, spacing=20, cls=None, **settings):
    """گرید نیتیو المنتور (Grid Container)."""
    return container(
        children, cls,
        container_type="grid",
        grid_columns_grid=w(columns, "fr"),
        grid_columns_grid_tablet=w(tablet if tablet else columns, "fr"),
        grid_columns_grid_mobile=w(mobile, "fr"),
        grid_rows_grid={"unit": "custom", "size": "auto"},
        grid_gaps=gap(spacing),
        **settings,
    )


# ---------------------------------------------------------------- سربرگ و فوتر

def header():
    brand_mark = container(
        [heading("ن", "div", color=PRIMARY_FG, size=16, weight=800, align="center")],
        "nd-brand-mark",
        flex_direction="row", flex_justify_content="center", flex_align_items="center",
        width=w(36), min_height=w(36),
        **bg(PRIMARY), **radius(12),
    )
    brand = container(
        [
            brand_mark,
            heading("نادیا قریشی", "div", "nd-brand-name", link="#top", color=FG, size=16, weight=800),
        ],
        "nd-brand",
        flex_direction="row", flex_align_items="center", flex_gap=gap(12),
        width={"unit": "custom", "size": "auto"}, _flex_size="none",
    )

    def menu_link(label, url):
        return button(label, url, "nd-menu-link", bgc=TRANSPARENT, fg=MUTED, radius_=0,
                      pad=(0, 0, 0, 0), size=14, weight=600, hover_color=FG, hover_bg=TRANSPARENT)

    menu = container(
        [menu_link("خانه", "#top"), menu_link("خدمات", "#services"),
         menu_link("نمونه‌کار", "#portfolio"), menu_link("تماس", "#contact")],
        "nd-menu",
        flex_direction="row", flex_align_items="center", flex_gap=gap(28),
        flex_justify_content_mobile="space-between", flex_gap_mobile=gap(12),
        width={"unit": "custom", "size": "auto"}, width_mobile={"unit": "%", "size": 100},
        _flex_size="none",
    )

    nav = container(
        [
            brand,
            menu,
            button("شروع گفتگو", "#contact", "nd-cta nd-btn", bgc=FG, fg=BG, radius_=12,
                   pad=(8, 16, 8, 16), size=14, weight=600,
                   extra={"_flex_size": "none", "hide_mobile": "hidden-mobile"}),
        ],
        "nd-nav nd-glass",
        width={"unit": "custom", "size": "min(100%, 1152px)"}, _flex_size="none",
        flex_direction="row", flex_align_items="center", flex_justify_content="space-between",
        flex_gap=gap(16), padding=dim(12, 24, 12, 24),
        **bg(SURFACE), **border(BORDER_SOFT), **radius(24), **shadow(),
    )

    return container(
        [nav],
        "nd-header",
        flex_direction="column", flex_align_items="center",
        position="fixed", _offset_orientation_h="start", _offset_x=w(0), _offset_y=w(0), z_index=50,
        padding=dim(16, 16, 0, 16),
    )


def footer():
    row = boxed(
        [
            heading("© ۱۴۰۵ نادیا قریشی", "div", color=MUTED, size=14, weight=500),
            heading("سئو با نگاه طراحی؛ طراحی با فکر دیده‌شدن", "div", color=MUTED, size=14, weight=500),
        ],
        "nd-footer-row",
        flex_direction="row", flex_wrap="wrap", flex_align_items="center",
        flex_justify_content="space-between", flex_gap=gap(12),
    )
    return container(
        [row],
        "nd-footer",
        flex_direction="column", flex_align_items="center",
        padding=dim(32, 0, 32, 0),
        border_border="solid", border_width=dim(1, 0, 0, 0), border_color=BORDER,
    )


# ---------------------------------------------------------------- کارت‌ها

def card(icon_name, title, body, tag=None):
    top = container(
        [
            icon_chip(icon_name, "nd-card-icon"),
            badge(tag, "nd-tag") if tag else None,
        ],
        "nd-card-top",
        flex_direction="row", flex_align_items="center", flex_justify_content="space-between",
        flex_gap=gap(16),
    )
    return container(
        [
            top,
            heading(title, "h3", "nd-h3", color=FG, size=20, weight=800, mt=24),
            text(f"<p>{body}</p>", "nd-muted", color=MUTED, size=16, height=1.75, mt=12),
        ],
        "nd-card nd-glass",
        padding=dim(24, 24, 24, 24),
        **bg(SURFACE), **border(BORDER_SOFT), **radius(24), **shadow(),
    )


def project_card(img, alt, kind, title, body):
    return container(
        [
            image(img, alt, "nd-project-img"),
            container(
                [
                    container(
                        [
                            heading(kind, "div", "nd-project-type", color=PRIMARY, size=12, weight=700),
                            icon("fas fa-arrow-up", "nd-project-arrow", color=MUTED, size=16),
                        ],
                        "nd-project-meta",
                        flex_direction="row", flex_align_items="center",
                        flex_justify_content="space-between", flex_gap=gap(16),
                    ),
                    heading(title, "h3", "nd-h3", color=FG, size=20, weight=800, mt=12),
                    text(f"<p>{body}</p>", "nd-muted", color=MUTED, size=16, height=1.75, mt=12),
                ],
                "nd-project-body",
                padding=dim(24, 24, 24, 24),
            ),
        ],
        "nd-project",
        overflow="hidden",
        **bg(CARD), **border(BORDER), **radius(24), **shadow(),
    )


def timeline_item(number, label, title, body):
    return container(
        [
            container(
                [heading(str(number), "div", color=PRIMARY_FG, size=16, weight=900, align="center")],
                "nd-step-num",
                flex_direction="row", flex_justify_content="center", flex_align_items="center",
                width=w(40), min_height=w(40),
                **bg(PRIMARY), **radius(999),
            ),
            container(
                [
                    heading(label, "div", "nd-step-label", color=ON_DARK_55, size=14, weight=500),
                    heading(title, "h3", "nd-h3", color=BG, size=20, weight=800, mt=4),
                    text(f"<p>{body}</p>", "nd-muted", color=ON_DARK_65, size=16, height=1.75, mt=12),
                ],
                "nd-timeline-body",
            ),
        ],
        "nd-timeline-item",
        flex_direction="row", flex_gap=gap(20),
        padding=dim(24, 24, 24, 24),
        **bg(ON_DARK_05), **border(ON_DARK_15), **radius(16),
    )


def page(title, sections):
    content = container(
        [header(), *sections, footer()],
        "nd-page", inner=False,
        **bg(BG),
    )
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


def hero():
    kicker = container(
        [heading("سئو، طراحی و تجربه بهتر وب", "div", "nd-kicker-text", color=SECONDARY_FG, size=14, weight=700)],
        "nd-kicker",
        flex_direction="row", flex_align_items="center", flex_gap=gap(8),
        width={"unit": "custom", "size": "fit-content"},
        padding=dim(8, 16, 8, 16),
        **bg(SECONDARY), **radius(999),
    )

    actions = container(
        [
            button("دیدن نمونه‌کارها", "#portfolio", "nd-btn nd-btn-primary", bgc=PRIMARY, fg=PRIMARY_FG,
                   radius_=12, pad=(14, 24, 14, 24), size=16, weight=700, extra=shadow(SHADOW_VIOLET)),
            button("ارتباط با من", "#contact", "nd-btn nd-btn-ghost nd-glass", bgc=SURFACE, fg=FG,
                   radius_=12, pad=(14, 24, 14, 24), size=16, weight=700, border_color=BORDER_SOFT),
        ],
        "nd-actions",
        flex_direction="row", flex_wrap="wrap", flex_gap=gap(12),
        margin=dim(36, 0, 0, 0),
    )

    copy = container(
        [
            kicker,
            heading("سلام، من نادیا هستم.", "p", "nd-hello", color=PRIMARY, size=18, weight=700, mt=28),
            heading(
                'کمک می‌کنم سایت‌ها <span class="nd-accent">بهتر دیده شوند</span> و بهتر کار کنند.',
                "h1", "nd-hero-title", color=FG, size=72, size_mobile=48, weight=900, height=1.15, mt=12,
            ),
            text(
                "<p>کارشناس سئو و طراح وب هستم. تمرکز اصلی من روی بهینه‌سازی اصولی سایت برای موتورهای جست‌وجو است و نگاه طراحی کمک می‌کند راهکارهایم فقط فنی نباشند؛ بلکه برای کاربر هم ساده و دلنشین باشند.</p>",
                "nd-lead", color=MUTED, size=18, height=2, mt=28,
            ),
            actions,
        ],
        "nd-hero-copy",
        animation="fadeInUp",
    )

    portrait = container(
        [
            container(
                [
                    image(IMG + "nadia-portrait.jpg", "پرتره نادیا قریشی، کارشناس سئو و طراح وب",
                          "nd-portrait-img", radius_=22),
                    container(
                        [
                            heading("آماده همکاری پروژه‌ای", "div", "nd-caption-strong", color=FG, size=14, weight=700),
                            heading("ایران", "div", "nd-caption-muted", color=MUTED, size=14, weight=500),
                        ],
                        "nd-portrait-caption",
                        flex_direction="row", flex_align_items="center", flex_justify_content="space-between",
                        padding=dim(16, 12, 4, 12),
                    ),
                ],
                "nd-portrait-card nd-glass",
                padding=dim(12, 12, 12, 12),
                **bg(SURFACE), **radius(32), **shadow(),
            ),
        ],
        "nd-portrait-wrap",
        width=w(448),
        animation="fadeInUp", animation_delay=150,
    )

    return container(
        [
            container(
                [copy, portrait],
                "nd-hero-grid",
                width={"unit": "custom", "size": f"min(100%, {SHELL}px)"}, _flex_size="none",
                container_type="grid",
                grid_columns_grid={"unit": "custom", "size": "1.15fr 0.85fr"},
                grid_columns_grid_tablet=w(1, "fr"),
                grid_columns_grid_mobile=w(1, "fr"),
                grid_rows_grid={"unit": "custom", "size": "auto"},
                grid_gaps=gap(48), grid_gaps_tablet=gap(40), grid_gaps_mobile=gap(40),
                grid_align_items="center",
                padding=dim(0, 24, 0, 24),
            ),
        ],
        "nd-hero",
        _element_id="top",
        flex_direction="column", flex_align_items="center", flex_justify_content="center",
        min_height=w(78, "vh"), min_height_tablet=w(0),
        padding=dim(144, 0, 64, 0),
    )


def services():
    head = container(
        [
            heading("خدمات و تخصص‌ها", "p", "nd-eyebrow", color=PRIMARY, size=16, weight=700),
            heading("از پیدا شدن در جست‌وجو تا تجربه‌ای که در ذهن می‌ماند", "h2", "nd-h2",
                    color=FG, size=44, size_mobile=28, weight=900, height=1.25, mt=12),
            text("<p>هر پروژه را بر اساس نیاز واقعی آن بررسی می‌کنم؛ بدون نسخه آماده و وعده‌های غیرواقعی.</p>",
                 "nd-muted", color=MUTED, size=16, height=2, mt=20),
        ],
        "nd-section-head",
        width={"unit": "custom", "size": "42rem"},
    )
    cards = grid([card(name, title, body, "تمرکز اصلی" if tag else None)
                  for name, title, body, tag in home_services],
                 columns=3, tablet=2, mobile=1, cls="nd-grid nd-grid-3")
    return section([head, cards], "nd-section nd-surface", element_id="services", surface=True)


def portfolio():
    head_row = container(
        [
            container(
                [
                    heading("نمونه‌کارها", "p", "nd-eyebrow", color=PRIMARY, size=16, weight=700),
                    heading("چند مسیر برای نمایش توانمندی‌ها", "h2", "nd-h2",
                            color=FG, size=44, size_mobile=28, weight=900, height=1.25, mt=12),
                ],
                "nd-head-main",
            ),
            text("<p>این بخش فعلاً با نمونه‌های نمایشی آماده شده تا بعداً پروژه‌های واقعی، نقش شما و نتیجه هر پروژه جایگزین شوند.</p>",
                 "nd-head-aside", color=MUTED, size=16, height=1.75),
        ],
        "nd-head-row",
        flex_direction="row", flex_wrap="wrap", flex_align_items="flex-end",
        flex_justify_content="space-between", flex_gap=gap(20),
    )
    cards = grid([project_card(IMG + img, alt, kind, title, body)
                  for img, alt, kind, title, body in home_projects],
                 columns=3, tablet=2, mobile=1, cls="nd-grid nd-grid-3")
    return section([head_row, cards], "nd-section", element_id="portfolio")


def resume():
    left = container(
        [
            heading("مسیر حرفه‌ای", "p", "nd-band-eyebrow", color=CYAN, size=16, weight=700),
            heading("در حال ساختن یک مسیر دقیق و ماندگار", "h2", "nd-h2",
                    color=BG, size=44, size_mobile=28, weight=900, height=1.25, mt=12),
            text("<p>تجربه‌ام را قدم‌به‌قدم با یادگیری مستمر و پروژه‌های واقعی گسترش می‌دهم. برای من کیفیت اجرا و مسئولیت‌پذیری مهم‌تر از ادعاهای بزرگ است.</p>",
                 "nd-band-text", color=ON_DARK_70, size=16, height=2, mt=24),
            container(
                [button("درخواست رزومه کامل", "#contact", "nd-btn nd-btn-light",
                        bgc=BG, fg=FG, radius_=12, pad=(14, 24, 14, 24), size=16, weight=700)],
                "nd-band-btn",
                flex_direction="row", width={"unit": "custom", "size": "fit-content"},
                margin=dim(32, 0, 0, 0),
            ),
        ],
        "nd-band-left",
    )
    timeline = grid([timeline_item(i + 1, *item) for i, item in enumerate(home_resume)],
                    columns=1, spacing=20, cls="nd-timeline")

    return container(
        [
            container(
                [left, timeline],
                "nd-band-grid",
                width={"unit": "custom", "size": f"min(100%, {SHELL}px)"}, _flex_size="none",
                container_type="grid",
                grid_columns_grid={"unit": "custom", "size": "0.8fr 1.2fr"},
                grid_columns_grid_tablet=w(1, "fr"),
                grid_columns_grid_mobile=w(1, "fr"),
                grid_rows_grid={"unit": "custom", "size": "auto"},
                grid_gaps=gap(64), grid_gaps_tablet=gap(40), grid_gaps_mobile=gap(40),
                grid_align_items="start",
                padding=dim(0, 24, 0, 24),
            ),
        ],
        "nd-band",
        _element_id="resume",
        flex_direction="column", flex_align_items="center",
        padding=dim(96, 0, 96, 0),
        **bg(FG),
    )


def contact():
    box = container(
        [
            container(
                [
                    icon("fas fa-envelope", "nd-contact-icon", color=PRIMARY, size=32),
                    heading("برای یک گفت‌وگوی حرفه‌ای آماده‌ام", "h2", "nd-contact-title",
                            color=FG, size=44, size_mobile=28, weight=900, height=1.25, align="center", mt=20),
                    text("<p>اگر برای همکاری، فرصت شغلی یا پروژه سئو و طراحی وب به دنبال همراهی دقیق و مسئولیت‌پذیر هستید، خوشحال می‌شوم بیشتر صحبت کنیم.</p>",
                         "nd-contact-text", color=MUTED, size=16, height=2, align="center", mt=20),
                    container(
                        [
                            badge("ایمیل: در انتظار تکمیل", "nd-chip nd-chip-primary",
                                  bgc=PRIMARY, fgc=PRIMARY_FG, size=16, radius_=12, pad=(12, 20, 12, 20)),
                            badge("لینکدین: در انتظار تکمیل", "nd-chip",
                                  bgc=BG, fgc=FG, size=16, radius_=12, pad=(12, 20, 12, 20), border_color=BORDER),
                            badge("تلگرام: در انتظار تکمیل", "nd-chip",
                                  bgc=BG, fgc=FG, size=16, radius_=12, pad=(12, 20, 12, 20), border_color=BORDER),
                        ],
                        "nd-contact-links",
                        flex_direction="row", flex_wrap="wrap", flex_align_items="center",
                        flex_justify_content="center", flex_gap=gap(12),
                        margin=dim(32, 0, 0, 0),
                    ),
                ],
                "nd-contact-inner",
                flex_direction="column", flex_align_items="center",
            ),
        ],
        "nd-contact-box nd-glass",
        overflow="hidden",
        padding=dim(64, 48, 64, 48),
        **bg(SURFACE), **border(BORDER_SOFT), **radius(28), **shadow(),
    )
    return section([box], "nd-section", element_id="contact")


def home_page():
    return page("خانه", [hero(), services(), portfolio(), resume(), contact()])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "01-home.json"
    path.write_text(json.dumps(home_page(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{path}  {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
