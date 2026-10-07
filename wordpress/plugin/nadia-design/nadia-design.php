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

define('NADIA_DESIGN_VERSION', '1.0.0');

function nadia_design_enqueue(): void
{
    wp_enqueue_style(
        'nadia-design-fonts',
        'https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&display=swap',
        [],
        null
    );

    wp_enqueue_style(
        'nadia-design',
        plugin_dir_url(__FILE__) . 'assets/nadia.css',
        ['nadia-design-fonts'],
        NADIA_DESIGN_VERSION
    );
}
add_action('wp_enqueue_scripts', 'nadia_design_enqueue');
