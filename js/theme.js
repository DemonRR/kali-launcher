// js/theme.js

// 主题切换逻辑
const settingsBtn = document.getElementById('settings-btn');

settingsBtn.addEventListener('click', async () => {
  const body = document.body;
  const header = document.querySelector('header');
  const aside = document.querySelector('aside');
  const itemCards = document.querySelectorAll('.bg-white');
  const textDarkElements = document.querySelectorAll('.text-dark');
  const contextMenu = document.getElementById('item-context-menu');
  const refreshBtn = document.getElementById('refresh-btn');

  if (body.classList.contains('light')) {
    body.classList.remove('light');
    body.classList.add('dark');
    header.classList.remove('light');
    header.classList.add('dark');
    aside.classList.remove('light');
    aside.classList.add('dark');
    itemCards.forEach(card => {
      card.classList.remove('light');
      card.classList.add('dark');
    });
    textDarkElements.forEach(element => {
      element.classList.remove('light');
      element.classList.add('dark');
    });
    contextMenu.classList.remove('light');
    contextMenu.classList.add('dark');
    refreshBtn.classList.remove('light');
    refreshBtn.classList.add('dark');
    // 更新右键菜单背景色为暗主题样式
    contextMenu.style.backgroundColor = '#1e293b';
    contextMenu.style.borderColor = '#334155';
    AppConfig.theme = 'dark';
  } else {
    body.classList.remove('dark');
    body.classList.add('light');
    header.classList.remove('dark');
    header.classList.add('light');
    aside.classList.remove('dark');
    aside.classList.add('light');
    itemCards.forEach(card => {
      card.classList.remove('dark');
      card.classList.add('light');
    });
    textDarkElements.forEach(element => {
      element.classList.remove('dark');
      element.classList.add('light');
    });
    contextMenu.classList.remove('dark');
    contextMenu.classList.add('light');
    refreshBtn.classList.remove('dark');
    refreshBtn.classList.add('light');
    // 更新右键菜单背景色为亮主题样式
    contextMenu.style.backgroundColor = '#ffffff';
    contextMenu.style.borderColor = '#e2e8f0';
    AppConfig.theme = 'light';
  }

  // 保存新的主题设置
  await saveConfig();
});