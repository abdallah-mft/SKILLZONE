@echo off
echo Cleaning up users directory...

:: Remove __pycache__ directories and compiled Python files
rmdir /s /q users\__pycache__
rmdir /s /q users\migrations\__pycache__
rmdir /s /q users\management\commands\__pycache__

:: Clean up duplicate/old migration files (be careful with this)
:: You might want to keep these for database history, but there seem to be some duplicates
:: del users\migrations\0002_level.py
:: del users\migrations\0002_level_and_data.py
:: del users\migrations\0003_level.py
:: del users\migrations\0003_create_levels_data.py

echo Users directory cleanup complete!