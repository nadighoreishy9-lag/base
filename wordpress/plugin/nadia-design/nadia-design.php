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
    // نسخه از زمان تغییر فایل خوانده می‌شود تا هر ویرایش CSS بلافاصله در مرورگر دیده شود
    // (نسخه ثابت باعث می‌شد مرورگر نسخه قدیمی کش‌شده را سرو کند).
    $style_path = plugin_dir_path(__FILE__) . 'assets/nadia.css';
    $version = file_exists($style_path) ? (string) filemtime($style_path) : NADIA_DESIGN_VERSION;
    wp_enqueue_style(
        'nadia-design',
        plugin_dir_url(__FILE__) . 'assets/nadia.css',
        [],
        $version
    );
}
add_action('wp_enqueue_scripts', 'nadia_design_enqueue');
