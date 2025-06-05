@echo off
title Git 一键初始化脚本
cd /d %~dp0

:: 检查是否已初始化 Git 仓库
IF EXIST ".git" (
    echo 当前目录已经是 Git 仓库，无需重复初始化。
    pause
    exit /b
)

echo 正在初始化 Git 仓库...
git init

:: 创建 .gitignore 文件（如果不存在）
IF NOT EXIST ".gitignore" (
    echo 创建默认 .gitignore 文件...
    (
        echo # Python 缓存
        echo __pycache__/
        echo *.pyc
        echo *.pyo

        echo # 虚拟环境
        echo venv/

        echo # Flask 实例配置
        echo instance/
        echo .env

        echo # 编辑器设置
        echo .vscode/
        echo .idea/

        echo # 日志
        echo *.log
        echo logs/

        echo # 系统文件
        echo Thumbs.db
        echo .DS_Store
    ) > .gitignore
    echo .gitignore 创建成功。
)

echo 添加所有项目文件...
git add .

set /p msg=请输入提交说明（默认：初始化提交）：
if "%msg%"=="" set msg=初始化提交

git commit -m "%msg%"

echo Git 仓库初始化成功，已完成首次提交。
echo.

:: 是否绑定远程仓库
set /p bind=是否需要绑定远程 GitHub 仓库？(y/n)：
if /i "%bind%"=="y" (
    set /p repo=https://github.com/kexl-atc/kexianlong.git：
    git branch -M main
    git remote add origin %repo%
    git push -u origin main
    echo 代码已推送到远程仓库。
)

pause
