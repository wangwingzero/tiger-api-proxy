@echo off
REM 虎哥API反代 打包脚本
REM 使用 PyInstaller 打包为单文件 exe，自动请求管理员权限

echo ========================================
echo 虎哥API反代 打包脚本
echo ========================================
echo.

REM 检查 PyInstaller 是否安装
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [INFO] 正在安装 PyInstaller...
    pip install pyinstaller
)

echo [INFO] 开始打包...
echo.

REM 打包命令
REM --onefile: 打包为单个 exe 文件
REM --windowed: 不显示控制台窗口
REM --uac-admin: 请求管理员权限 (UAC)
REM --name: 输出文件名

pyinstaller ^
    --onefile ^
    --windowed ^
    --uac-admin ^
    --name "虎哥API反代" ^
    run.py

echo.
if errorlevel 1 (
    echo [ERROR] 打包失败！
    pause
    exit /b 1
)

echo [SUCCESS] 打包完成！
echo 输出文件: dist\虎哥API反代.exe
echo.
pause
