<?php
/**
 * Plugin Name: Nadia Design
 * Description: استایل و فونت سایت شخصی نادیا قریشی برای صفحات ساخته‌شده با المنتور (توکن‌های رنگ، افکت شیشه‌ای، چیدمان واکنش‌گرا).
 * Version: 1.0.0
 * Author: Nadia Ghoeyshi
 * Text Domain: nadia-design
 */

if (!defined('ABSPATH')) {
    exit;
}

define('NADIA_DESIGN_VERSION', '1.0.1');

function nadia_design_enqueue(): void
{
    // فونت وزیرمتن داخل خود nadia.css با @import بارگذاری می‌شود، پس هر دو روش
    // (این افزونه و «CSS افزودنی» بدون افزونه) یک استایل و یک فونت یکسان می‌دهند.
    wp_enqueue_style(
        'nadia-design',
        plugin_dir_url(__FILE__) . 'assets/nadia.css',
        [],
        NADIA_DESIGN_VERSION
    );
}
add_action('wp_enqueue_scripts', 'nadia_design_enqueue');
