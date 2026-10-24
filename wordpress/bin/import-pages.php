<?php
/**
 * ساخت/به‌روزرسانی صفحه تک‌صفحه‌ای سایت از فایل قالب المنتور در مخزن.
 * اجرا: wp eval-file /source/bin/import-pages.php
 *
 * سایت مثل منبع طراحی (Lovable) تک‌صفحه‌ای است؛ صفحه‌های جدا و قدیمی «خدمات» و
 * «نمونه‌کارها» اگر از قبل وجود داشته باشند به سطل زباله می‌روند تا سایت واقعاً تک‌صفحه‌ای بماند.
 */

if (!defined('WP_CLI')) {
    exit;
}

$templates = [
    ['slug' => 'home', 'title' => 'خانه', 'file' => '/source/elementor/01-home.json', 'front' => true],
];

$home_id = 0;

foreach ($templates as $template) {
    $raw = file_get_contents($template['file']);
    $data = json_decode($raw, true);

    if (!is_array($data) || empty($data['content'])) {
        WP_CLI::error('قالب نامعتبر: ' . $template['file']);
    }

    $existing = get_page_by_path($template['slug'], OBJECT, 'page');
    $postarr = [
        'post_title' => $template['title'],
        'post_name' => $template['slug'],
        'post_status' => 'publish',
        'post_type' => 'page',
        'post_content' => '',
    ];

    if ($existing) {
        $postarr['ID'] = $existing->ID;
    }

    $page_id = wp_insert_post($postarr, true);

    if (is_wp_error($page_id)) {
        WP_CLI::error($page_id->get_error_message());
    }

    $template_type = $data['page_settings']['template'] ?? 'elementor_canvas';

    update_post_meta($page_id, '_elementor_edit_mode', 'builder');
    update_post_meta($page_id, '_elementor_template_type', 'wp-page');
    update_post_meta($page_id, '_elementor_version', defined('ELEMENTOR_VERSION') ? ELEMENTOR_VERSION : '3.0.0');
    update_post_meta($page_id, '_elementor_data', wp_slash(wp_json_encode($data['content'])));
    update_post_meta($page_id, '_elementor_page_settings', ['template' => $template_type]);
    update_post_meta($page_id, '_wp_page_template', $template_type);

    if (!empty($template['front'])) {
        $home_id = $page_id;
    }

    WP_CLI::log(sprintf('  %s → %s (#%d)', $template['title'], $template['slug'], $page_id));
}

// صفحه‌های جدا که دیگر بخشی از طراحی تک‌صفحه‌ای نیستند.
foreach (['services', 'portfolio'] as $stale_slug) {
    $stale = get_page_by_path($stale_slug, OBJECT, 'page');
    if ($stale && 'trash' !== $stale->post_status) {
        wp_trash_post($stale->ID);
        WP_CLI::log(sprintf('  صفحه قدیمی به سطل زباله رفت: %s (#%d)', $stale_slug, $stale->ID));
    }
}

if ($home_id) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', $home_id);
}

if (class_exists('\Elementor\Plugin')) {
    \Elementor\Plugin::$instance->files_manager->clear_cache();
}

WP_CLI::success('صفحه تک‌صفحه‌ای سایت ساخته شد.');
