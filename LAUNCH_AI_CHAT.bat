@echo off
echo 🤖 LAUNCHING AI-PC PARTNERSHIP INTERFACE
echo =====================================

echo Starting AI Workbench with Chat Interface...
start "AI Workbench" python ai\AI_WORKBENCH.py

echo Starting Web Dashboard...
start "Web Dashboard" python gui\web_interface.py

echo Starting WebSocket AI Server...
start "AI Server" node ai-workbench\server\websocket-server.js

echo Starting Ultimate AI Optimizer...
start "Ultimate AI" python ai\ULTIMATE_AI_OPTIMIZER.py

echo.
echo ✅ AI-PC Partnership Interfaces Launched!
echo.
echo 🌐 Web Dashboard: http://localhost:5000
echo 🤖 AI Chat: Available in all interfaces
echo ⚡ Auto-healing: ACTIVE
echo 🔧 Coding assistance: READY
echo.
pause