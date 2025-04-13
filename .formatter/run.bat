@echo off
setlocal enabledelayedexpansion

:: Configuration
set VAULT_PATH=C:\Users\Po-Chun Wu\Desktop\home\notes
set PYTHON_PATH=python3
set FORMATTER_PATH=C:\Users\Po-Chun Wu\Desktop\home\notes\.formatter\formatter.py
set COMMIT_MESSAGE=Auto format Obsidian vault %date% %time%

:: Display header
echo ===================================
echo Obsidian Vault Formatter with Git
echo ===================================

:: Check if paths exist
if not exist "%VAULT_PATH%" (
    echo Error: Vault path not found: %VAULT_PATH%
    goto :error
)

if not exist "%FORMATTER_PATH%" (
    echo Error: Formatter script not found: %FORMATTER_PATH%
    goto :error
)

:: Navigate to vault directory
cd /d "%VAULT_PATH%"
echo Working directory: %cd%

:: Check if git repository exists
if not exist ".git" (
    echo Error: Git repository not initialized in %VAULT_PATH%
    echo Please run 'git init' in your vault directory first.
    goto :error
)

:: Check for uncommitted changes before formatting
echo Checking for existing changes...
git status --porcelain > temp_status.txt
set /p GIT_STATUS=<temp_status.txt
del temp_status.txt

if not "!GIT_STATUS!"=="" (
    echo Warning: You have uncommitted changes in your vault.
    choice /C YN /M "Do you want to commit these changes before formatting?"
    if errorlevel 2 goto :run_formatter
    if errorlevel 1 (
        echo Committing existing changes...
        git add .
        git commit -m "Changes before formatting %date% %time%"
        if !errorlevel! neq 0 (
            echo Error: Failed to commit existing changes.
            goto :error
        )
        echo Existing changes committed successfully.
    )
)

:run_formatter
:: Run the formatter
echo.
echo Running Obsidian vault formatter...
%PYTHON_PATH% "%FORMATTER_PATH%" "%VAULT_PATH%"
if %errorlevel% neq 0 (
    echo Error: Formatter failed with exit code %errorlevel%
    goto :error
)

:: Commit changes to git
echo.
echo Committing formatted changes to git...
git add .

:: Check if there are changes to commit
git status --porcelain > temp_status.txt
set /p GIT_STATUS=<temp_status.txt
del temp_status.txt

if "!GIT_STATUS!"=="" (
    echo No changes to commit after formatting.
    goto :success
)

:: Commit the changes
git commit -m "%COMMIT_MESSAGE%"
if %errorlevel% neq 0 (
    echo Error: Failed to commit changes.
    goto :error
)

echo Changes committed successfully.

:: Optional: Push to remote repository
choice /C YN /M "Do you want to push changes to remote repository?"
if errorlevel 1 (
    git push
    if !errorlevel! neq 0 (
        echo Error: Failed to push changes.
        goto :error
    )
    echo Changes pushed successfully.
)

:success
echo.
echo ===================================
echo Process completed successfully!
echo ===================================
goto :end

:error
echo.
echo ===================================
echo Process failed!
echo ===================================
exit /b 1

:end
echo.
echo Press any key to exit...
pause > nul
exit /b 0