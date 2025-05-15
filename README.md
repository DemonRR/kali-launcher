<p align="center">
  <h1 align="center">kali-launcher</h1>
</p>

<p align="center">
<a href="https://github.com/DemonRR/kali-launcher/releases/"><img src="https://img.shields.io/github/release/DemonRR/kali-launcher?label=%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC&style=square"></a>
<a href="https://github.com/DemonRR/kali-launcher/releases"><img src="https://img.shields.io/github/downloads/DemonRR/kali-launcher/total?label=%E4%B8%8B%E8%BD%BD%E6%AC%A1%E6%95%B0&style=square"></a>
<a href="https://github.com/DemonRR/kali-launcher/issues"><img src="https://img.shields.io/github/issues-raw/DemonRR/kali-launcher?label=%E9%97%AE%E9%A2%98%E5%8F%8D%E9%A6%88&style=square"></a>
<a href="https://github.com/DemonRR/kali-launcher/discussions"><img src="https://img.shields.io/github/stars/DemonRR/kali-launcher?label=%E7%82%B9%E8%B5%9E%E6%98%9F%E6%98%9F&style=square"></a>
</p>

# kali-launcher

由于个人觉得kali开始菜单使用起来编辑麻烦就想着自己写一个启动器，起初自己手动用Python+PyQt6进行开发，结果效果不是太理想，就让AI基于Electron写了一个。有能力的小伙伴可以二开。

## 功能
支持一件快捷打开应用、URL、文件、文件夹。应用以命令方式打开，支持终端运行和静默运行

## 界面展示
![PixPin_2025-05-11_22-42-30](https://github.com/user-attachments/assets/74c2cbea-26e5-4ac3-8718-a47a80de3ab2)

## 安装Electron

```
sudo npm install electron electron-builder --save-dev --verbose
```



## 打包

```
#打包开发版
npm run pack

#打包正式版
npm run dist
```

## 安装
```
dpkg -i kali-launcher_1.0.1_amd64.deb

```

## 运行
```
kali-launcher
# root用户下运行需要添加 --no-sandbox
# 快捷方式kali-launcher.desktop root用户下需要手动编辑添加--no-sandbox
```


