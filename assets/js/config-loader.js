function updateSocialLinks() {
  if (typeof socialConfig === 'undefined') {
    console.warn('socialConfig not loaded');
    return;
  }

  // Generate social links in the container
  const container = document.getElementById('social-links-container');
  if (container) {
    container.innerHTML = '';
    socialConfig.forEach(item => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = item.action;
      a.textContent = item.value;
      li.innerHTML = `<strong>${item.label}：</strong> `;
      li.appendChild(a);
      container.appendChild(li);
    });
  }

  // Update other elements with data-social attribute (legacy support)
  const configMap = {};
  socialConfig.forEach(item => {
    configMap[item.label.toLowerCase()] = item;
  });

  document.querySelectorAll('[data-social]').forEach(element => {
    const social = element.getAttribute('data-social').toLowerCase();
    const config = configMap[social];

    if (config) {
      if (element.tagName === 'A') {
        element.href = config.action;
        if (!element.textContent || element.textContent.trim() === '') {
          element.textContent = config.value;
        }
      } else {
        element.textContent = config.value;
      }
    }
  });
}

// Run when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', updateSocialLinks);
} else {
  updateSocialLinks();
}


