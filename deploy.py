import osfrom pathlib import Pathfrom shutil import copy, copytreefrom distutils.sysconfig import get_python_lib# 1. activate virtual environment#    $ conda activate YOUR_ENV_NAME## 2. run deploy script#    $ python deploy.pyargs = [    'nuitka',
    '--standalone',
    '--assume-yes-for-downloads',
    '--msvc=latest',
    '--enable-plugins=pyqt6',
    '--show-progress',
    '--onefile',
    '--show-memory',
    '--output-dir=E:/主文件夹/桌面/test/build',
    'E:/主文件夹/桌面/test/main.py']dist_folder = Path("E:/主文件夹/桌面/test/build")copied_site_packages = [    ]copied_standard_packages = [    ]# run nuitka# https://blog.csdn.net/qq_25262697/article/details/129302819# https://www.cnblogs.com/happylee666/articles/16158458.htmlos.system(" ".join(args))# copy site-packages to dist foldersite_packages = Path(get_python_lib())for src in copied_site_packages:    src = site_packages / src    dist = dist_folder / src.name    print(f"Coping site-packages `{src}` to `{dist}`")    try:        if src.is_file():            copy(src, dist)        else:            copytree(src, dist)    except:        pass# copy standard libraryfor file in copied_standard_packages:    src = site_packages.parent / file    dist = dist_folder / src.name    print(f"Coping stand library `{src}` to `{dist}`")    try:        if src.is_file():            copy(src, dist)        else:            copytree(src, dist)    except:        pass