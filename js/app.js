// js/app.js
document.addEventListener('DOMContentLoaded', async () => {
  console.log('应用初始化...');
  
  // 初始化配置
  await loadConfig();
  
  // 渲染UI
  renderCategories();
  renderItems();
  
  // 设置事件监听
  setupCategoryEvents();
  setupItemEvents();
  
  // 设置确认模态框事件
  document.getElementById('confirm-ok-btn').addEventListener('click', async () => {
    try {
      if (currentItemId) {
        // 删除项目
        await deleteItem(currentItemId);
        showNotification('成功', '项目已删除', 'success');
      } else if (currentCategoryIdForEdit) {
        // 删除分类
        await deleteCategory(currentCategoryIdForEdit);
        showNotification('成功', '分类已删除', 'success');
      }
    } catch (error) {
      console.error('删除失败:', error);
      showNotification('错误', '删除失败: ' + error.message, 'error');
    }
    
    document.getElementById('confirm-modal').classList.add('hidden');
    currentItemId = null;
    currentCategoryIdForEdit = null;
  });
  
  document.getElementById('confirm-cancel-btn').addEventListener('click', () => {
    document.getElementById('confirm-modal').classList.add('hidden');
    currentItemId = null;
    currentCategoryIdForEdit = null;
  });
  
  // 导出功能
  document.getElementById('export-btn').addEventListener('click', async () => {
    try {
      const configJson = JSON.stringify(AppConfig, null, 2);
      const blob = new Blob([configJson], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'launcher_config.json';
      a.click();
      URL.revokeObjectURL(url);
      
      showNotification('成功', '配置已导出', 'success');
    } catch (error) {
      console.error('导出失败:', error);
      showNotification('错误', '导出失败: ' + error.message, 'error');
    }
  });
  
  // 导入功能
  document.getElementById('import-btn').addEventListener('click', async () => {
    // 创建并触发文件输入
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.style.display = 'none';
    
    document.body.appendChild(input);
    
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      
      try {
        const reader = new FileReader();
        reader.onload = async (event) => {
          try {
            const newConfig = JSON.parse(event.target.result);
            
            // 验证导入的配置
            if (!newConfig || !newConfig.items || !newConfig.categories) {
              throw new Error('无效的配置文件');
            }
            
            // 确认覆盖现有配置
            document.getElementById('confirm-title').textContent = '确认导入';
            document.getElementById('confirm-message').textContent = '导入将覆盖现有配置，是否继续？';
            document.getElementById('confirm-ok-btn').onclick = async () => {
              try {
                AppConfig = newConfig;
                await saveConfig();
                renderCategories();
                renderItems(currentSearchTerm);
                document.getElementById('confirm-modal').classList.add('hidden');
                showNotification('成功', '配置已导入', 'success');
              } catch (error) {
                console.error('保存导入的配置失败:', error);
                showNotification('错误', '保存配置失败: ' + error.message, 'error');
              }
            };
            document.getElementById('confirm-modal').classList.remove('hidden');
          } catch (parseError) {
            console.error('解析配置文件失败:', parseError);
            showNotification('错误', '解析配置文件失败: ' + parseError.message, 'error');
          }
        };
        reader.readAsText(file);
      } catch (error) {
        console.error('导入失败:', error);
        showNotification('错误', '导入失败: ' + error.message, 'error');
      }
    };
    
    input.click();
    document.body.removeChild(input);
  });
  
  // 主题切换功能
  document.getElementById('settings-btn').addEventListener('click', () => {
    const body = document.body;
    const settingsBtn = document.getElementById('settings-btn');
    
    if (body.classList.contains('dark-theme')) {
      // 切换到明亮主题
      body.classList.remove('dark-theme');
      body.classList.add('light-theme');
      settingsBtn.innerHTML = '<i class="fa fa-sun mr-1"></i> 明亮主题';
      localStorage.setItem('appTheme', 'light');
      showNotification('成功', '已切换到明亮主题', 'success');
    } else {
      // 切换到暗黑主题
      body.classList.remove('light-theme');
      body.classList.add('dark-theme');
      settingsBtn.innerHTML = '<i class="fa fa-moon mr-1"></i> 暗黑主题';
      localStorage.setItem('appTheme', 'dark');
      showNotification('成功', '已切换到暗黑主题', 'success');
    }
  });
  
  // 加载保存的主题偏好
  const savedTheme = localStorage.getItem('appTheme');
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
    document.getElementById('settings-btn').innerHTML = '<i class="fa fa-moon mr-1"></i> 暗黑主题';
  } else {
    document.body.classList.add('light-theme');
    document.getElementById('settings-btn').innerHTML = '<i class="fa fa-sun mr-1"></i> 明亮主题';
  }
});