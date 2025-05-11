// electron-app/preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  addCategory: (name) => ipcRenderer.invoke('add-category', name),
  editCategory: (id, name) => ipcRenderer.invoke('edit-category', id, name),
  deleteCategory: (id) => ipcRenderer.invoke('delete-category', id),
  addItem: (item) => ipcRenderer.invoke('add-item', item),
  editItem: (id, updatedItem) => ipcRenderer.invoke('edit-item', id, updatedItem),
  deleteItem: (id) => ipcRenderer.invoke('delete-item', id),
  executeCommand: (command) => ipcRenderer.invoke('execute-command', command),
  executeCommandInTerminal: (command) => ipcRenderer.invoke('execute-command-in-terminal', command), // 新增方法
  openUrl: (url) => ipcRenderer.invoke('open-url', url),
  openPath: (path) => ipcRenderer.invoke('open-path', path)
});
