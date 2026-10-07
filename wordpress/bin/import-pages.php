<?php
/**
 * ساخت/به‌روزرسانی سه صفحه سایت از فایل‌های قالب المنتور در مخزن.
 * اجرا: wp eval-file /source/bin/import-pages.php
 */

if (!defined('WP_CLI')) {
    exit;
}

$templates = [
    ['slug' => 'home', 'title' => 'خانه', 'file' => '/source/elementor/01-home.json', 'front' => true],
    ['slug' => 'services', 'title' => 'خدمات', 'file' => '/source/elementor/02-services.json'],
    ['slug' => 'portfolio', 'title' => 'نمونه‌کارها', 'file' => '/source/elementor/03-portfolio.json'],
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

if ($home_id) {
    update_option('show_on_front', 'page');
    update_option('page_on_front', $home_id);
}

if (class_exists('\Elementor\Plugin')) {
    \Elementor\Plugin::$instance->files_manager->clear_cache();
}

WP_CLI::success('صفحات المنتور ساخته شد.');
