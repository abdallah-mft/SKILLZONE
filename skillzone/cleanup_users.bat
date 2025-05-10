@echo off
echo Cleaning up users directory...

:: Remove __pycache__ directories and compiled Python files
rmdir /s /q users\__pycache__
rmdir /s /q users\migrations\__pycache__
rmdir /s /q users\management\commands\__pycache__

echo Users directory cleanup complete!
