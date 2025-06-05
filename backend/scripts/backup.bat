@echo off
setlocal enabledelayedexpansion

:: 设置备份目录
set BACKUP_DIR=backups
set DB_FILE=ledger.db

:: 创建备份目录
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

:: 生成时间戳
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%-%dt:~12,2%"

:: 备份文件名
set BACKUP_FILE=%BACKUP_DIR%\ledger_backup_%timestamp%.db

:: 执行备份
echo 正在备份数据库...
copy ..\%DB_FILE% %BACKUP_FILE%

if %errorlevel% equ 0 (
    echo 备份成功: %BACKUP_FILE%
    
    :: 删除7天前的备份
    forfiles /p %BACKUP_DIR% /s /m *.db /d -7 /c "cmd /c del @path" 2>nul
    echo 已清理7天前的旧备份
) else (
    echo 备份失败！
    exit /b 1
)

:: 创建备份日志
echo %date% %time% - 备份成功: %BACKUP_FILE% >> %BACKUP_DIR%\backup.log

echo.
echo 备份完成！