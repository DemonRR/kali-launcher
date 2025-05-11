// js/categories.js
// 当前操作的分类ID（用于编辑和删除）
let currentCategoryIdForEdit = null;

// 渲染分类列表
function renderCategories() {
  const categoriesList = document.getElementById('categories-list');
  categoriesList.innerHTML = '';

  // 添加"全部项目"分类项
  const allCategoryItem = document.createElement('div');
  allCategoryItem.className = `flex items-center justify-between p-2 rounded-lg cursor-pointer hover:bg-light-1 transition-custom category-list-item ${!currentCategoryId ? 'bg-primary/10 text-primary' : ''}`;
  allCategoryItem.dataset.id = 'all';
  
  allCategoryItem.addEventListener('click', () => {
    currentCategoryId = null;
    renderCategories();
    renderItems();
  });

  // 创建分类内容
  const allCategoryContent = document.createElement('div');
  allCategoryContent.className = 'flex items-center space-x-2';
  
  const allCategoryIcon = document.createElement('i');
  allCategoryIcon.className = 'fa fa-list';
  
  const allCategoryName = document.createElement('span');
  allCategoryName.textContent = '全部项目';

  // 添加全部项目的数量统计，添加 item-count 类名
  const allItemCount = document.createElement('span');
  allItemCount.className = 'item-count bg-light-1 text-xs text-dark-2 rounded-full w-6 h-6 flex items-center justify-center shadow-sm';
  allItemCount.textContent = AppConfig.items.length;
  
  allCategoryContent.appendChild(allCategoryIcon);
  allCategoryContent.appendChild(allCategoryName);
  allCategoryContent.appendChild(allItemCount);
  
  allCategoryItem.appendChild(allCategoryContent);
  categoriesList.appendChild(allCategoryItem);

  // 添加用户自定义分类
  AppConfig.categories.forEach(category => {
    const categoryItem = document.createElement('div');
    categoryItem.className = `flex items-center justify-between p-2 rounded-lg cursor-pointer hover:bg-light-1 transition-custom category-list-item ${currentCategoryId === category.id ? 'bg-primary/10 text-primary' : ''}`;
    categoryItem.dataset.id = category.id;
    
    categoryItem.addEventListener('click', () => {
      currentCategoryId = category.id;
      renderCategories();
      renderItems();
    });

    // 分类内容
    const categoryContent = document.createElement('div');
    categoryContent.className = 'flex items-center space-x-2';
    
    const categoryIcon = document.createElement('i');
    categoryIcon.className = `fa ${category.icon}`;
    
    const categoryName = document.createElement('span');
    categoryName.textContent = category.name;

    // 添加项目数量统计，添加 item-count 类名
    const itemCount = document.createElement('span');
    itemCount.className = 'item-count bg-light-1 text-xs text-dark-2 rounded-full w-6 h-6 flex items-center justify-center shadow-sm';
    itemCount.textContent = AppConfig.items.filter(item => item.categoryId === category.id).length;
    
    categoryContent.appendChild(categoryIcon);
    categoryContent.appendChild(categoryName);
    categoryContent.appendChild(itemCount);
    
    // 操作按钮容器
    const actionButtons = document.createElement('div');
    actionButtons.className = 'flex items-center space-x-1 opacity-0 hover:opacity-100 transition-custom';
    
    const editButton = document.createElement('button');
    editButton.className = 'p-1 text-dark-2 hover:text-primary transition-custom';
    editButton.innerHTML = '<i class="fa fa-pencil"></i>';
    editButton.addEventListener('click', (e) => {
      e.stopPropagation();
      currentCategoryIdForEdit = category.id;
      openCategoryModal(category.id);
    });
    
    const deleteButton = document.createElement('button');
    deleteButton.className = 'p-1 text-dark-2 hover:text-danger transition-custom';
    deleteButton.innerHTML = '<i class="fa fa-trash"></i>';
    deleteButton.addEventListener('click', (e) => {
      e.stopPropagation();
      currentCategoryIdForEdit = category.id;
      document.getElementById('confirm-title').textContent = '确认删除';
      document.getElementById('confirm-message').textContent = `你确定要删除分类 "${category.name}" 吗？`;
      document.getElementById('confirm-modal').classList.remove('hidden');
    });
    
    actionButtons.appendChild(editButton);
    actionButtons.appendChild(deleteButton);
    
    categoryItem.appendChild(categoryContent);
    categoryItem.appendChild(actionButtons);
    
    categoriesList.appendChild(categoryItem);
  });
}

// 打开分类模态框
function openCategoryModal(categoryId = null) {
  const modal = document.getElementById('category-modal');
  const form = document.getElementById('category-form');
  const title = document.getElementById('category-modal-title');
  
  // 重置表单
  form.reset();
  document.getElementById('category-id').value = '';
  document.getElementById('category-name-error').classList.add('hidden');
  
  if (categoryId) {
    title.textContent = '编辑分类';
    
    // 查找要编辑的分类
    const category = AppConfig.categories.find(c => c.id === categoryId);
    if (category) {
      document.getElementById('category-id').value = category.id;
      document.getElementById('category-name').value = category.name;
      document.getElementById('category-icon').value = category.icon;
      document.getElementById('category-icon-preview').className = `fa ${category.icon}`;
    }
  } else {
    title.textContent = '添加分类';
    document.getElementById('category-icon-preview').className = 'fa fa-folder';
  }
  
  // 显示模态框
  modal.classList.remove('hidden');
  
  // 确保输入框可聚焦
  setTimeout(() => {
    document.getElementById('category-name').focus();
  }, 100);
}

// 设置分类相关事件
function setupCategoryEvents() {
  // 添加分类按钮
  document.getElementById('add-category-btn').addEventListener('click', () => {
    openCategoryModal();
  });
  
  // 分类表单提交
  document.getElementById('category-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const categoryId = document.getElementById('category-id').value;
    const categoryName = document.getElementById('category-name').value.trim();
    const categoryIcon = document.getElementById('category-icon').value.trim();
    
    // 验证
    let isValid = true;
    
    if (!categoryName) {
      document.getElementById('category-name-error').classList.remove('hidden');
      isValid = false;
    } else {
      document.getElementById('category-name-error').classList.add('hidden');
    }
    
    if (!isValid) return;
    
    try {
      if (categoryId) {
        // 更新现有分类
        const index = AppConfig.categories.findIndex(c => c.id === categoryId);
        if (index !== -1) {
          AppConfig.categories[index].name = categoryName;
          AppConfig.categories[index].icon = categoryIcon;
          // 更新关联的项目
          AppConfig.items.forEach(item => {
            if (item.categoryId === categoryId) {
              item.categoryName = categoryName;
            }
          });
          showNotification('成功', '分类已更新', 'success');
        }
      } else {
        // 创建新分类
        const newCategory = {
          id: Date.now().toString(),
          name: categoryName,
          icon: categoryIcon || 'fa-folder'
        };
        AppConfig.categories.push(newCategory);
        showNotification('成功', '分类已添加', 'success');
      }
      
      // 保存配置
      await saveConfig();
      
      // 重新渲染分类和项目
      renderCategories();
      renderItems();
      
      // 关闭模态框
      document.getElementById('category-modal').classList.add('hidden');
    } catch (error) {
      console.error('保存分类失败:', error);
      showNotification('错误', '保存分类失败: ' + error.message, 'error');
    }
  });
  
  // 图标实时预览
  document.getElementById('category-icon').addEventListener('input', (e) => {
    const iconPreview = document.getElementById('category-icon-preview');
    iconPreview.className = `fa ${e.target.value || 'fa-folder'}`;
  });
}

// 删除分类
async function deleteCategory(categoryId) {
  // 从本地配置中删除分类及其项目
  AppConfig.categories = AppConfig.categories.filter(c => c.id !== categoryId);
  AppConfig.items = AppConfig.items.filter(i => i.categoryId !== categoryId);
  
  // 保存配置
  await saveConfig();
  
  // 更新UI
  renderCategories();
  renderItems();
}