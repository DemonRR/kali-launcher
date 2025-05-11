// js/config.js
// 应用配置
let AppConfig = {
  categories: [],
  items: [],
  defaultCategoryId: null,
  settings: {
    theme: 'light',
    layout: 'grid',
    animations: true
  }
};

// 加载配置
async function loadConfig() {
  try {
    // 从主进程获取配置
    const config = await window.api.getConfig();
    if (config) {
      AppConfig = config;
      showNotification('成功', '配置加载成功', 'success');
      // 应用主题设置
      applyTheme(config.theme);
    } else {
      showNotification('提示', '使用默认配置', 'info');
    }
  } catch (error) {
    console.error('加载配置失败:', error);
    showNotification('错误', '加载配置失败: ' + error.message, 'error');
  }
}

// 保存配置
async function saveConfig() {
  try {
    // 确保数据完整性
    AppConfig.categories = AppConfig.categories || [];
    AppConfig.items = AppConfig.items || [];
    
    // 保存到主进程
    await window.api.saveConfig(AppConfig);
    
    showNotification('成功', '配置已保存', 'success');
  } catch (error) {
    console.error('保存配置失败:', error);
    showNotification('错误', '保存配置失败: ' + error.message, 'error');
    throw error;
  }
}

// 应用主题设置
function applyTheme(theme) {
  const body = document.body;
  const header = document.querySelector('header');
  const aside = document.querySelector('aside');
  const itemCards = document.querySelectorAll('.bg-white');
  const textDarkElements = document.querySelectorAll('.text-dark');

  if (theme === 'dark') {
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
  }
}