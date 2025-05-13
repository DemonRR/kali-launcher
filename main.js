const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs').promises; // 使用异步版本的 fs
const { exec, execSync, spawn } = require('child_process');


// 设置 Linux 输入法环境变量
if (process.platform === 'linux') {
  // 检测当前系统使用的输入法框架
  try {
    const fcitx5Running = execSync('pgrep fcitx5', { stdio: 'ignore' }).toString().trim().length > 0;
    const fcitxRunning = execSync('pgrep fcitx', { stdio: 'ignore' }).toString().trim().length > 0;
    const ibusRunning = execSync('pgrep ibus', { stdio: 'ignore' }).toString().trim().length > 0;

    if (fcitx5Running) {
      process.env.GTK_IM_MODULE = 'fcitx';
      process.env.QT_IM_MODULE = 'fcitx';
      process.env.XMODIFIERS = '@im=fcitx';
      process.env.IM_CONFIG_PHASE = '1';
      console.log('已检测到 fcitx5，设置输入法环境变量');
    } else if (fcitxRunning) {
      process.env.GTK_IM_MODULE = 'fcitx';
      process.env.QT_IM_MODULE = 'fcitx';
      process.env.XMODIFIERS = '@im=fcitx';
      console.log('已检测到 fcitx，设置输入法环境变量');
    } else if (ibusRunning) {
      process.env.GTK_IM_MODULE = 'ibus';
      process.env.QT_IM_MODULE = 'ibus';
      process.env.XMODIFIERS = '@im=ibus';
      console.log('已检测到 ibus，设置输入法环境变量');
    }
  } catch (error) {
    // 如果检测失败，使用默认设置
    console.log('输入法检测失败，使用默认设置');
    process.env.GTK_IM_MODULE = 'fcitx';
    process.env.QT_IM_MODULE = 'fcitx';
    process.env.XMODIFIERS = '@im=fcitx';
  }

  // 设置应用数据目录
  app.setPath('userData', path.join(app.getPath('home'), '.config/kali-launcher'));
}

// 配置文件路径
const CONFIG_PATH = path.join(app.getPath('userData'), 'config.json');

// 初始化配置
let config = {
  categories: [],
  items: [],
  theme: 'light' // 添加 theme 字段
};

// 异步读取配置文件
async function loadConfig() {
  try {
    const data = await fs.readFile(CONFIG_PATH, 'utf8');
    config = JSON.parse(data);
    console.log('配置文件加载成功');
  } catch (error) {
    console.error('加载配置文件失败:', error);
    config = { categories: [], items: [], theme: 'light' };
    await saveConfig(); // 创建新的配置文件
  }
}

// 异步保存配置文件
async function saveConfig() {
  try {
    await fs.writeFile(CONFIG_PATH, JSON.stringify(config, null, 2));
    console.log('配置文件保存成功');
  } catch (error) {
    console.error('保存配置文件失败:', error);
  }
}

// 创建主窗口
function createWindow() {
  const win = new BrowserWindow({
    width: 1100,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, // 启用上下文隔离
      nodeIntegration: false, // 禁用Node.js集成
      inputMethod: 'system', // 确保输入法配置
      enableRemoteModule: false, // 禁用remote模块
      sandbox: true // 启用沙盒
    }
  });

  win.loadFile('index.html');

  // 开发环境下打开开发者工具
  if (process.env.NODE_ENV === 'development') {
    win.webContents.openDevTools();
  }

  console.log('主窗口已创建');
}

// 应用准备就绪时创建窗口
app.whenReady().then(async () => {
  await loadConfig();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// 所有窗口关闭时退出应用
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

// 移除顶部菜单栏
Menu.setApplicationMenu(null);

// IPC通信处理

// 获取所有配置
ipcMain.handle('get-config', () => {
  console.log('收到获取配置请求');
  return config;
});

// 保存配置
ipcMain.handle('save-config', async (event, newConfig) => {
  console.log('收到保存配置请求');
  config = newConfig;
  await saveConfig();
  return true;
});

// 添加分类
ipcMain.handle('add-category', async (event, name) => {
  console.log('收到添加分类请求:', name);
  const newCategory = {
    id: Date.now().toString(),
    name
  };
  config.categories.push(newCategory);
  await saveConfig();
  return newCategory;
});

// 编辑分类
ipcMain.handle('edit-category', async (event, id, name) => {
  console.log('收到编辑分类请求:', id, name);
  const category = config.categories.find(c => c.id === id);
  if (category) {
    category.name = name;
    // 更新关联的项目
    config.items.forEach(item => {
      if (item.categoryId === id) {
        item.categoryName = name;
      }
    });
    await saveConfig();
    return true;
  }
  return false;
});

// 删除分类
ipcMain.handle('delete-category', async (event, id) => {
  console.log('收到删除分类请求:', id);
  // 先删除关联的项目
  config.items = config.items.filter(item => item.categoryId !== id);
  // 再删除分类
  config.categories = config.categories.filter(c => c.id !== id);
  await saveConfig();
  return true;
});

// 添加项目
ipcMain.handle('add-item', async (event, item) => {
  console.log('收到添加项目请求:', item);
  const newItem = {
    id: Date.now().toString(),
    ...item
  };
  config.items.push(newItem);
  await saveConfig();
  return newItem;
});

// 编辑项目
ipcMain.handle('edit-item', async (event, id, updatedItem) => {
  console.log('收到编辑项目请求:', id, updatedItem);
  const index = config.items.findIndex(item => item.id === id);
  if (index !== -1) {
    config.items[index] = { ...config.items[index], ...updatedItem };
    await saveConfig();
    return true;
  }
  return false;
});

// 删除项目
ipcMain.handle('delete-item', async (event, id) => {
  console.log('收到删除项目请求:', id);
  config.items = config.items.filter(item => item.id !== id);
  await saveConfig();
  return true;
});

// 执行命令
ipcMain.handle('execute-command', (event, command) => {
  console.log('收到执行命令请求:', command);
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`执行命令出错: ${error.message}`);
        reject(error.message);
        return;
      }
      if (stderr) {
        console.error(`命令错误输出: ${stderr}`);
        reject(stderr);
        return;
      }
      console.log(`命令输出: ${stdout}`);
      resolve(stdout);
    });
  });
});

// 在终端中执行命令
ipcMain.handle('execute-command-in-terminal', (event, command) => {
  console.log('收到在终端中执行命令请求:', command);
  return new Promise((resolve, reject) => {
    let cmd, args;

    if (process.platform === 'win32') {
      // Windows系统
      cmd = 'cmd.exe';
      args = ['/k', command];
    } else if (process.platform === 'darwin') {
      // macOS系统
      const script = `tell app "Terminal" to do script "${escapeShell(command)}; bash"`;
      cmd = 'osascript';
      args = ['-e', script];
    } else {
      // Linux系统
      const terminals = [
        { bin: 'gnome-terminal', args: ['--', 'bash', '-c'] },
        { bin: 'konsole', args: ['-e', 'bash', '-c'] },
        { bin: 'xfce4-terminal', args: ['-x', 'bash', '-c'] },
        { bin: 'terminator', args: ['-x', 'bash', '-c'] },
        { bin: 'tilix', args: ['--', 'bash', '-c'] },
        { bin: 'mate-terminal', args: ['--', 'bash', '-c'] },
      ];

      let terminalFound = false;

      for (const terminal of terminals) {
        try {
          // 检查终端是否存在
          execSync(`which ${terminal.bin}`, { stdio: 'ignore' });
          cmd = terminal.bin;
          args = [...terminal.args, `${escapeShell(command)}; bash`];
          terminalFound = true;
          break;
        } catch (e) {
          continue;
        }
      }

      if (!terminalFound) {
        // 使用默认的终端
        cmd = 'x-terminal-emulator';
        args = ['-e', `bash -c '${escapeShell(command)}; bash'`];
      }
    }

    console.log('执行终端命令:', cmd, args);

    // 使用 spawn 代替 exec，分离进程，不等待输出
    const child = spawn(cmd, args, { detached: true, stdio: 'ignore' });

    // 立即分离子进程，让它在后台运行
    child.unref();

    // 命令已成功启动，无需等待终端关闭
    resolve('命令已在新终端中启动');
  });
});

// 转义shell命令
function escapeShell(cmd) {
  return cmd.replace(/(["'$`\\])/g, '\\$1');
}

// 打开URL
ipcMain.handle('open-url', async (event, url) => {
  console.log('收到打开URL请求:', url);
  try {
    await shell.openExternal(url);
    return true;
  } catch (error) {
    console.error('打开URL失败:', error);
    throw new Error(`无法打开URL: ${error.message}`);
  }
});

// 打开文件或文件夹
ipcMain.handle('open-path', (event, path) => {
  console.log('收到打开路径请求:', path);
  shell.openPath(path);
});

// 导出配置
ipcMain.handle('export-config', async () => {
  const { canceled, filePath } = await dialog.showSaveDialog({
    filters: [
      { name: 'JSON Files', extensions: ['json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (!canceled) {
    try {
      await fs.writeFile(filePath, JSON.stringify(config, null, 2));
      return true;
    } catch (error) {
      console.error('导出配置失败:', error);
      return false;
    }
  }
  return false;
});

// 导入配置
ipcMain.handle('import-config', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    filters: [
      { name: 'JSON Files', extensions: ['json'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });

  if (!canceled) {
    try {
      const data = await fs.readFile(filePaths[0], 'utf8');
      const newConfig = JSON.parse(data);
      config = newConfig;
      await saveConfig();
      return true;
    } catch (error) {
      console.error('导入配置失败:', error);
      return false;
    }
  }
  return false;
});