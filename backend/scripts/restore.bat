@echo off

echo 数据库恢复工具
echo.

:: 列出可用的备份
echo 可用的备份文件:
echo.
set /a count=0
for %%f in (backups\*.db) do (
    set /a count+=1
    echo !count!. %%f
    set backup!count!=%%f
)

if %count% equ 0 (
    echo 没有找到备份文件！
    pause
    exit /b 1
)

:: 选择备份文件
echo.
set /p choice=请选择要恢复的备份文件编号: 

:: 确认恢复
echo.
echo 警告：恢复操作将覆盖当前数据库！
set /p confirm=确定要继续吗？(y/n): 

if /i "%confirm%" neq "y" (
    echo 操作已取消
    pause
    exit /b 0
)

:: 备份当前数据库
echo.
echo 备份当前数据库...
copy ..\ledger.db ..\ledger.db.before_restore

:: 执行恢复
echo 正在恢复数据库...
copy !backup%choice%! ..\ledger.db

if %errorlevel% equ 0 (
    echo 恢复成功！
    echo 原数据库已备份为: ledger.db.before_restore
) else (
    echo 恢复失败！
    copy ..\ledger.db.before_restore ..\ledger.db
)

pause