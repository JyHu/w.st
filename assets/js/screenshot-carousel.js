// 应用截图轮播功能
function initScreenshotCarousel() {
  if (typeof appConfig === 'undefined' || !appConfig.snaps || appConfig.snaps.length === 0) {
    console.warn('snaps config not available');
    return;
  }

  let currentIndex = 0;
  const snaps = appConfig.snaps;

  const imgElement = document.getElementById('screenshotImg');
  const nameElement = document.getElementById('screenshotName');
  const desElement = document.getElementById('screenshotDes');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');

  if (!imgElement || !nameElement || !desElement || !prevBtn || !nextBtn) {
    console.warn('Screenshot carousel elements not found');
    return;
  }

  function updateScreenshot(index) {
    const snap = snaps[index];
    imgElement.src = 'assets/images/' + snap.img;
    imgElement.alt = snap.name;
    nameElement.textContent = snap.name;
    desElement.textContent = snap.des || '';
  }

  function nextScreenshot() {
    currentIndex = (currentIndex + 1) % snaps.length;
    updateScreenshot(currentIndex);
  }

  function prevScreenshot() {
    currentIndex = (currentIndex - 1 + snaps.length) % snaps.length;
    updateScreenshot(currentIndex);
  }

  prevBtn.addEventListener('click', prevScreenshot);
  nextBtn.addEventListener('click', nextScreenshot);

  // 初始化第一张
  updateScreenshot(currentIndex);
}

// 当 DOM 加载完成时初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initScreenshotCarousel);
} else {
  initScreenshotCarousel();
}
