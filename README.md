# kali-launcher

由于个人觉得kali开始菜单使用起来编辑麻烦就想着自己写一个启动器，起初自己手动用Python+PyQt6进行开发，结果效果不是太理想，就让AI基于Electron写了一个。有能力的小伙伴可以二开。

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
```


