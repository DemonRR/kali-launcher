// js/items.js
// 当前选中的分类ID
let currentCategoryId = null;

// 当前操作的项目ID（用于编辑和删除）
let currentItemId = null;

// 当前搜索关键词
let currentSearchTerm = '';

// 根据分类ID获取分类名称
const getCategoryName = (categoryId) => {
  if (!categoryId) return '未分类';
  
  const category = AppConfig?.categories?.find(c => c.id === categoryId);
  return category ? category.name : '未知分类';
};

// 渲染项目列表
function renderItems(searchTerm = '') {
  const itemsGrid = document.getElementById('items-grid');
  const emptyState = document.getElementById('empty-state');
  
  // 保存当前搜索词
  currentSearchTerm = searchTerm;
  
  // 过滤项目
  let itemsToRender = AppConfig.items;
  
  // 应用分类筛选
  if (currentCategoryId) {
    itemsToRender = itemsToRender.filter(item => item.categoryId === currentCategoryId);
  }
  
  // 应用搜索筛选
  if (searchTerm) {
    const lowerSearchTerm = searchTerm.toLowerCase();
    itemsToRender = itemsToRender.filter(item => 
      item.name.toLowerCase().includes(lowerSearchTerm) || 
      item.command.toLowerCase().includes(lowerSearchTerm)
    );
  }
  
  // 显示空状态或项目列表
  if (itemsToRender.length === 0) {
    itemsGrid.innerHTML = '';
    emptyState.classList.remove('hidden');
    
    // 如果有搜索词但没有结果，显示搜索无结果提示
    if (searchTerm) {
      document.querySelector('#empty-state h3').textContent = '未找到匹配项目';
      document.querySelector('#empty-state p').textContent = '尝试使用不同的关键词或清除搜索条件';
    } else {
      document.querySelector('#empty-state h3').textContent = '暂无项目';
      document.querySelector('#empty-state p').textContent = '添加您的第一个启动器项目，快速访问常用应用和命令';
    }
    
    return;
  } else {
    emptyState.classList.add('hidden');
  }
  
  itemsGrid.innerHTML = '';
  
  // 计算网格列数（根据屏幕宽度自适应）
  const gridColumns = window.innerWidth < 640 ? 1 : 
                     window.innerWidth < 768 ? 2 : 
                     window.innerWidth < 1024 ? 3 : 4;
  
  itemsGrid.style.gridTemplateColumns = `repeat(${gridColumns}, minmax(0, 1fr))`;
  
  itemsToRender.forEach(item => {
    const itemCard = document.createElement('div');
    itemCard.className = 'bg-white rounded-xl shadow-sm p-3 hover-scale hover:shadow-md transition-all duration-200 cursor-pointer';
    itemCard.dataset.itemId = item.id; // 存储项目ID
    
    // 使用CSS Grid进行布局
    itemCard.style.display = 'grid';
    itemCard.style.gridTemplateColumns = 'auto 1fr';
    itemCard.style.gap = '0.75rem'; // 对应Tailwind的mr-3
    
    // 项目图标
    const itemIcon = document.createElement('div');
    itemIcon.className = 'w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary shadow-sm';
    // 修改为 v5 类名
    itemIcon.innerHTML = `<i class="fas ${item.icon || 'fa-terminal'}"></i>`;
    
    // 项目名称
    const itemName = document.createElement('h3');
    itemName.className = 'font-medium text-dark truncate self-center';
    itemName.textContent = item.name;
    
    // 点击卡片执行项目
    itemCard.addEventListener('click', () => {
      runItem(item);
    });
    
    // 右键菜单功能
    itemCard.addEventListener('contextmenu', (e) => {
      e.preventDefault(); // 阻止默认右键菜单
      
      // 获取右键菜单元素
      const contextMenu = document.getElementById('item-context-menu');
      
      // 设置菜单项数据
      contextMenu.dataset.itemId = item.id;
      contextMenu.querySelector('.menu-item-name').textContent = item.name;
      
      // 定位菜单
      contextMenu.style.top = `${e.pageY}px`;
      contextMenu.style.left = `${e.pageX}px`;
      
      // 显示菜单
      contextMenu.classList.remove('hidden');
      
      // 点击其他地方关闭菜单
      setTimeout(() => {
        const closeMenu = (event) => {
          if (!contextMenu.contains(event.target)) {
            contextMenu.classList.add('hidden');
            document.removeEventListener('click', closeMenu);
          }
        };
        document.addEventListener('click', closeMenu);
      }, 0);
    });
    
    itemCard.appendChild(itemIcon);
    itemCard.appendChild(itemName);
    itemsGrid.appendChild(itemCard);
  });
}

// 打开项目模态框
function openItemModal(itemId = null) {
  const modal = document.getElementById('item-modal');
  const form = document.getElementById('item-form');
  const title = document.getElementById('item-modal-title');
  const submitBtn = document.getElementById('item-submit-btn');
  
  // 重置表单
  form.reset();
  document.getElementById('item-id').value = '';
  document.getElementById('item-name-error').classList.add('hidden');
  document.getElementById('item-command-error').classList.add('hidden');
  
  // 填充分类选项
  const categorySelect = document.getElementById('item-category');
  categorySelect.innerHTML = ''; // 清空现有选项
  
  // 只有在编辑已有项目时才添加"未分类"选项
  if (itemId) {
    const noneOption = document.createElement('option');
    noneOption.value = '';
    noneOption.textContent = '未分类';
    categorySelect.appendChild(noneOption);
  }
  
  // 添加用户自定义分类
  AppConfig.categories.forEach(category => {
    const option = document.createElement('option');
    option.value = category.id;
    option.textContent = category.name;
    categorySelect.appendChild(option);
  });
  
  // 初始化终端选项（默认隐藏）
  const terminalOption = document.getElementById('run-in-terminal-option');
  terminalOption.classList.add('hidden');
  
  if (itemId) {
    title.textContent = '编辑项目';
    submitBtn.textContent = '保存修改';
    
    // 查找要编辑的项目
    const item = AppConfig.items.find(i => i.id === itemId);
    if (item) {
      document.getElementById('item-id').value = item.id;
      document.getElementById('item-name').value = item.name;
      document.getElementById('item-type').value = item.type;
      document.getElementById('item-command').value = item.command;
      document.getElementById('item-category').value = item.categoryId || '';
      document.getElementById('item-icon').value = item.icon;
      document.getElementById('item-icon-preview').className = `fa ${item.icon || 'fa-terminal'}`;
      
      // 如果是命令类型，显示终端选项
      if (item.type === 'command') {
        terminalOption.classList.remove('hidden');
        document.getElementById('run-in-terminal').checked = item.runInTerminal || false;
      }
    }
  } else {
    title.textContent = '新建项目';
    submitBtn.textContent = '添加项目';
    document.getElementById('item-icon-preview').className = 'fa fa-terminal';
    
    // 如果有当前选中的分类，自动设置分类
    if (currentCategoryId) {
      document.getElementById('item-category').value = currentCategoryId;
    }
  }
  
  // 显示模态框
  modal.classList.remove('hidden');
  
  // 确保输入框可聚焦
  setTimeout(() => {
    document.getElementById('item-name').focus();
  }, 100);
  
  // 监听项目类型变化
  const itemTypeSelect = document.getElementById('item-type');
  itemTypeSelect.addEventListener('change', (e) => {
    const iconPreview = document.getElementById('item-icon-preview');
    const itemIconInput = document.getElementById('item-icon');
    switch (e.target.value) {
      case 'url':
        iconPreview.className = 'fa fa-globe';
        itemIconInput.value = 'fa-globe';
        break;
      case 'file':
        iconPreview.className = 'fa fa-file';
        itemIconInput.value = 'fa-file';
        break;
      case 'folder':
        iconPreview.className = 'fa fa-folder';
        itemIconInput.value = 'fa-folder';
        break;
      case 'command':
        iconPreview.className = 'fa fa-terminal';
        itemIconInput.value = 'fa-terminal';
        break;
    }
    
    if (e.target.value === 'command') {
      terminalOption.classList.remove('hidden');
    } else {
      terminalOption.classList.add('hidden');
    }
  });
  
  // 触发一次 change 事件，设置初始图标
  itemTypeSelect.dispatchEvent(new Event('change'));
}

// 设置项目相关事件
function setupItemEvents() {
  // 添加项目按钮
  document.getElementById('add-item-btn').addEventListener('click', () => {
    // 检查是否有自定义分类
    const hasCustomCategories = AppConfig.categories.length > 0;
    if (!hasCustomCategories) {
      showNotification('提示', '请先添加至少一个分类后再创建项目', 'warning');
      return;
    }
    openItemModal();
  });
  
  // 空状态添加项目按钮
  document.getElementById('empty-add-item-btn').addEventListener('click', () => {
    // 检查是否有自定义分类
    const hasCustomCategories = AppConfig.categories.length > 0;
    if (!hasCustomCategories) {
      showNotification('提示', '请先添加至少一个分类后再创建项目', 'warning');
      return;
    }
    openItemModal();
  });

  // 添加刷新按钮
  const refreshButton = document.createElement('button');
  refreshButton.id = 'refresh-btn';
  refreshButton.className = 'p-2 rounded-lg hover:bg-light-1 transition-custom';
  refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i>'; // 替换为 v5 图标
  refreshButton.title = '刷新';
  
  // 将刷新按钮插入到新建项目按钮右边
  const addItemBtn = document.getElementById('add-item-btn');
  addItemBtn.after(refreshButton);
  
  // 刷新按钮事件
  refreshButton.addEventListener('click', async () => {
    try {
      // 添加旋转动画
      refreshButton.querySelector('i').classList.add('fa-spin');
      
      // 重新加载配置
      await loadConfig();
      
      // 重新渲染分类和项目列表
      renderCategories();
      renderItems(currentSearchTerm);
      
      showNotification('成功', '界面已刷新', 'success');
    } catch (error) {
      console.error('刷新失败:', error);
      showNotification('错误', '刷新失败: ' + error.message, 'error');
    } finally {
      // 移除旋转动画
      refreshButton.querySelector('i').classList.remove('fa-spin');
    }
  });
  
  // 项目表单提交
  document.getElementById('item-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const itemId = document.getElementById('item-id').value;
    const itemName = document.getElementById('item-name').value.trim();
    const itemType = document.getElementById('item-type').value;
    const itemCommand = document.getElementById('item-command').value.trim();
    const itemCategory = document.getElementById('item-category').value;
    const itemIcon = document.getElementById('item-icon').value.trim();
    
    // 获取"在终端中打开"的状态
    const runInTerminal = itemType === 'command' 
      ? document.getElementById('run-in-terminal').checked 
      : false;
    
    // 验证
    let isValid = true;
    
    if (!itemName) {
      document.getElementById('item-name-error').classList.remove('hidden');
      isValid = false;
    } else {
      document.getElementById('item-name-error').classList.add('hidden');
    }
    
    if (!itemCommand) {
      document.getElementById('item-command-error').classList.remove('hidden');
      isValid = false;
    } else {
      document.getElementById('item-command-error').classList.add('hidden');
    }

    // 检查重名
    if (!itemId) { // 新建项目时检查
      const isDuplicate = AppConfig.items.some(item => item.name === itemName);
      if (isDuplicate) {
        document.getElementById('item-name-error').textContent = '项目名称已存在，请选择其他名称';
        document.getElementById('item-name-error').classList.remove('hidden');
        isValid = false;
      }
    }
    
    if (!isValid) return;
    
    try {
      if (itemId) {
        // 更新现有项目
        const index = AppConfig.items.findIndex(i => i.id === itemId);
        if (index !== -1) {
          AppConfig.items[index].name = itemName;
          AppConfig.items[index].type = itemType;
          AppConfig.items[index].command = itemCommand;
          AppConfig.items[index].categoryId = itemCategory || null;
          AppConfig.items[index].categoryName = getCategoryName(itemCategory);
          AppConfig.items[index].icon = itemIcon;
          
          // 只对命令类型保存runInTerminal属性
          if (itemType === 'command') {
            AppConfig.items[index].runInTerminal = runInTerminal;
          } else {
            // 如果不是命令类型，移除该属性
            delete AppConfig.items[index].runInTerminal;
          }
          
          showNotification('成功', '项目已更新', 'success');
        }
      } else {
        // 创建新项目
        const newItem = {
          id: Date.now().toString(),
          name: itemName,
          type: itemType,
          command: itemCommand,
          categoryId: itemCategory || null,
          categoryName: getCategoryName(itemCategory),
          icon: itemIcon || 'fa-terminal'
        };
        
        // 只对命令类型添加runInTerminal属性
        if (itemType === 'command') {
          newItem.runInTerminal = runInTerminal;
        }
        
        AppConfig.items.push(newItem);
        showNotification('成功', '项目已添加', 'success');
      }
      
      // 保存配置
      await saveConfig();
      
      // 重新渲染分类和项目列表，更新统计数字
      renderCategories();
      renderItems(currentSearchTerm);
      
      // 关闭模态框
      document.getElementById('item-modal').classList.add('hidden');
    } catch (error) {
      console.error('保存项目失败:', error);
      showNotification('错误', '保存项目失败: ' + error.message, 'error');
    }
  });
  
  // 图标实时预览
  document.getElementById('item-icon').addEventListener('input', (e) => {
    const iconPreview = document.getElementById('item-icon-preview');
    // 修改为 v5 类名
    iconPreview.className = `fas ${e.target.value || 'fa-terminal'}`;
  });
  
  // 确保模态框关闭时重置状态
  document.getElementById('item-modal-close').addEventListener('click', () => {
    document.getElementById('item-modal').classList.add('hidden');
  });
  
  // 设置搜索功能
  const searchInput = document.getElementById('search-input');
  searchInput.addEventListener('input', (e) => {
    renderItems(e.target.value.trim());
  });
  
  // 添加键盘事件支持 - 按ESC清除搜索
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      searchInput.value = '';
      renderItems('');
    }
  });
}

// 运行项目
async function runItem(item) {
  try {
    switch (item.type) {
      case 'url':
        // 验证URL格式
        let url = item.command;
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
          url = 'https://' + url;
        }
        
        await window.api.openUrl(url);
        showNotification('成功', `URL已打开: ${item.name}`, 'success');
        break;
      case 'command':
        try {
          if (item.runInTerminal) {
            // 在终端中运行命令
            const result = await window.api.executeCommandInTerminal(item.command);
            showNotification('成功', `命令在终端中执行: ${item.name}`, 'success');
            console.log('命令输出:', result);
          } else {
            // 直接执行命令
            const result = await window.api.executeCommand(item.command);
            showNotification('成功', `命令执行成功: ${item.name}`, 'success');
            console.log('命令输出:', result);
          }
        } catch (error) {
          showNotification('错误', `命令执行失败: ${error}`, 'error');
        }
        break;
      case 'file':
        // 打开文件
        try {
          await window.api.openPath(item.command);
          showNotification('成功', `文件已打开: ${item.name}`, 'success');
        } catch (error) {
          showNotification('错误', `无法打开文件: ${error}`, 'error');
        }
        break;
      case 'folder':
        // 打开文件夹
        try {
          await window.api.openPath(item.command);
          showNotification('成功', `文件夹已打开: ${item.name}`, 'success');
        } catch (error) {
          showNotification('错误', `无法打开文件夹: ${error}`, 'error');
        }
        break;
      default:
        showNotification('提示', `未知项目类型: ${item.type}`, 'warning');
    }
  } catch (error) {
    console.error('执行项目失败:', error);
    showNotification('错误', '执行项目失败: ' + error.message, 'error');
  }
}

// 删除项目
async function deleteItem(itemId) {
  // 删除项目
  AppConfig.items = AppConfig.items.filter(item => item.id !== itemId);
  await saveConfig();
  
  // 重新渲染分类和项目列表
  renderCategories();
  renderItems(currentSearchTerm);
}

// 初始化右键菜单
function initContextMenu() {
  // 创建右键菜单元素
  const contextMenu = document.createElement('div');
  contextMenu.id = 'item-context-menu';
  contextMenu.className = 'hidden context-menu';
  
  // 菜单标题
  const menuTitle = document.createElement('div');
  menuTitle.className = 'px-3 py-1.5 text-xs border-b menu-item-name font-medium truncate menu-title-truncate'; // 添加自定义类名
  menuTitle.textContent = '项目操作';
  contextMenu.appendChild(menuTitle);
  
  // 运行菜单项
  const runMenuItem = document.createElement('div'); // 避免函数名冲突，修改变量名
  runMenuItem.className = 'px-3 py-1.5 cursor-pointer flex items-center context-menu-item';
  runMenuItem.innerHTML = '<i class="fas fa-play mr-2 text-primary"></i> 运行'; // 修改为 v5 类名
  runMenuItem.addEventListener('click', () => {
    const itemId = contextMenu.dataset.itemId;
    const item = AppConfig.items.find(i => i.id === itemId);
    if (item) {
      runItem(item);
    }
    contextMenu.classList.add('hidden');
  });
  contextMenu.appendChild(runMenuItem);
  
  // 编辑菜单项
  const editItem = document.createElement('div');
  editItem.className = 'px-3 py-1.5 cursor-pointer flex items-center context-menu-item';
  editItem.innerHTML = '<i class="fas fa-pencil-alt mr-2 text-primary"></i> 编辑'; // 修改为 v5 图标
  editItem.addEventListener('click', () => {
    const itemId = contextMenu.dataset.itemId;
    openItemModal(itemId);
    contextMenu.classList.add('hidden');
  });
  contextMenu.appendChild(editItem);
  
  // 删除菜单项
  const deleteItem = document.createElement('div');
  deleteItem.className = 'px-3 py-1.5 cursor-pointer flex items-center text-danger context-menu-item';
  deleteItem.innerHTML = '<i class="fas fa-trash-alt mr-2"></i> 删除'; // 修改为 v5 图标
  deleteItem.addEventListener('click', () => {
    const itemId = contextMenu.dataset.itemId;
    const item = AppConfig.items.find(i => i.id === itemId);
    if (item) {
      currentItemId = itemId;
      document.getElementById('confirm-title').textContent = '确认删除';
      document.getElementById('confirm-message').textContent = `你确定要删除 "${item.name}" 吗？`;
      document.getElementById('confirm-modal').classList.remove('hidden');
    }
    contextMenu.classList.add('hidden');
  });
  contextMenu.appendChild(deleteItem);
  
  // 添加到页面
  document.body.appendChild(contextMenu);
}

// 在应用初始化时调用
document.addEventListener('DOMContentLoaded', () => {
  initContextMenu();
  // ... 其他初始化代码 ...
});
