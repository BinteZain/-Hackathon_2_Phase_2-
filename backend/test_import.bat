@echo off
REM Clear all Python cache
echo Clearing cache...
del /s /q **\__pycache__\*.pyc 2>nul
del /s /q **\__pycache__\*.pyo 2>nul
del /s /q **\__pycache__\*.pyd 2>nul
echo Cache cleared

REM Run test
echo Testing model imports...
venv\Scripts\python.exe -c "from src.models import User, Conversation, Message, MCPToolExecution, Task; print('SUCCESS: All models loaded!'); print('Tables:', User.__tablename__, Conversation.__tablename__, Message.__tablename__, MCPToolExecution.__tablename__, Task.__tablename__)"
