@echo off
set BACKUP_DIR=skillzone_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%

:: Create backup directory
mkdir %BACKUP_DIR%

:: Copy project files
xcopy /E /I /Y .\ %BACKUP_DIR%\
copy .env %BACKUP_DIR%\
copy requirements.txt %BACKUP_DIR%\
copy skillzone_backup.sql %BACKUP_DIR%\

:: Create ZIP (requires 7-Zip, adjust path if needed)
"C:\Program Files\7-Zip\7z.exe" a -tzip %BACKUP_DIR%.zip %BACKUP_DIR%\

echo Backup completed! Files are in %BACKUP_DIR% and %BACKUP_DIR%.zip