@echo off
REM 统一启动脚本 - 同时启动飞书机器人和 Web 管理界面 (Windows)
REM
REM 使用方法:
REM   scripts\start_all.bat [development|production]
REM
REM 默认: development

setlocal enabledelayedexpansion

REM 确定运行模式
set MODE=%1
if "%MODE%"=="" set MODE=development

REM 获取项目根目录
cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%

echo ========================================
echo   飞书 AI 机器人 - 统一启动脚本
echo ========================================
echo.

REM 检查 .env 文件
if not exist .env (
    echo 错误: .env 文件不存在
    echo 请从 .env.example 创建 .env 文件
    exit /b 1
)

REM 创建必要的目录
if not exist data mkdir data
if not exist logs mkdir logs

REM PID 文件路径
set BOT_PID_FILE=%PROJECT_ROOT%\data\bot.pid
set WEB_PID_FILE=%PROJECT_ROOT%\data\web.pid

echo 运行模式: %MODE%
echo.

REM 启动飞书机器人
echo [1/2] 启动飞书机器人...
start /b python lark_bot.py > logs\bot.log 2>&1
echo 飞书机器人已启动
echo   日志文件: logs\bot.log
echo.

REM 等待机器人启动
timeout /t 2 /nobreak > nul

REM 启动 Web 管理界面
echo [2/2] 启动 Web 管理界面...

if /i "%MODE%"=="development" goto dev_mode
if /i "%MODE%"=="dev" goto dev_mode
if /i "%MODE%"=="production" goto prod_mode
if /i "%MODE%"=="prod" goto prod_mode

echo 错误: 无效的运行模式 '%MODE%'
echo 使用方法: %0 [development^|production]
exit /b 1

:dev_mode
echo 使用开发模式 (Flask dev server)
start /b python -m feishu_bot.web_admin.server --host 0.0.0.0 --port 8080 --debug --log-level DEBUG > logs\web.log 2>&1
goto web_started

:prod_mode
echo 使用生产模式 (Gunicorn)
where gunicorn >nul 2>&1
if errorlevel 1 (
    echo 错误: Gunicorn 未安装
    echo 安装命令: pip install gunicorn
    exit /b 1
)
start /b gunicorn -c gunicorn.conf.py wsgi:app > logs\web.log 2>&1
goto web_started

:web_started
echo Web 管理界面已启动
echo   访问地址: http://localhost:8080
echo   日志文件: logs\web.log
echo.

REM 等待 Web 服务启动
timeout /t 2 /nobreak > nul

echo ========================================
echo   所有服务启动成功！
echo ========================================
echo.
echo 服务状态:
echo   • 飞书机器人: 运行中
echo   • Web 管理界面: 运行中
echo.
echo 日志查看:
echo   • 机器人日志: type logs\bot.log
echo   • Web 日志: type logs\web.log
echo.
echo 按任意键停止所有服务...
pause > nul

REM 停止服务
echo.
echo 正在停止服务...
taskkill /f /im python.exe /fi "WINDOWTITLE eq lark_bot*" > nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq feishu_bot*" > nul 2>&1
taskkill /f /im gunicorn.exe > nul 2>&1
echo 所有服务已停止

endlocal
