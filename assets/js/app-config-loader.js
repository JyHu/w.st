// 应用配置加载器
function updateAppConfig() {
  if (typeof appConfig === 'undefined') {
    console.warn('appConfig not loaded');
    return;
  }

  // 更新页面标题和品牌名称
  const brandElements = document.querySelectorAll('[data-app-brand]');
  brandElements.forEach(element => {
    element.textContent = `${appConfig.icon} ${appConfig.name}`;
  });

  // 更新页面 meta description
  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute('content', appConfig.description);
  }

  // 更新页面 title
  if (document.title.includes('Stellect')) {
    document.title = appConfig.title;
  }
}

// Run when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', updateAppConfig);
} else {
  updateAppConfig();
}
