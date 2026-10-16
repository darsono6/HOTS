@echo off
setlocal enabledelayedexpansion

if defined ProgramData (
    set "MACHINE_DIR=%ProgramData%\HOTS Hosts"
) else (
    set "MACHINE_DIR=C:\ProgramData\HOTS Hosts"
)

if defined APPDATA (
    set "USER_DIR=%APPDATA%\HOTS Hosts"
) else (
    set "USER_DIR=C:\HOTS Hosts"
)

set "LOG=%TEMP%\hots_uninstall.log"
set "RESULT_FILE=%TEMP%\hots_uninstall_result_%RANDOM%.json"

rem Arguments from the uninstaller: the wizard choices file and the password file.
set "CHOICES_FILE=%~1"
set "AUTH_FILE=%~2"
set "PS_CHOICES=%CHOICES_FILE:'=''%"
set "PS_AUTH=%AUTH_FILE:'=''%"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [hots_uninstall] Not running as administrator - elevating via UAC... >> "%LOG%"
    powershell -NoProfile -Command "$p = Start-Process -FilePath '%~f0' -ArgumentList '\"%PS_CHOICES%\" \"%PS_AUTH%\"' -Verb RunAs -Wait -PassThru; exit $p.ExitCode"
    exit /b %errorlevel%
)

echo [hots_uninstall] ---- %DATE% %TIME% ---- >> "%LOG%"
echo [hots_uninstall] Choices file: %CHOICES_FILE% >> "%LOG%"
if exist "%CHOICES_FILE%" (
    type "%CHOICES_FILE%" >> "%LOG%"
    echo. >> "%LOG%"
) else (
    echo [hots_uninstall] WARNING: choices file not found - nothing selected in the wizard will be applied. >> "%LOG%"
)

echo [hots_uninstall] Applying the choices made in the uninstall wizard... >> "%LOG%"
"%~dp0HOTS Hosts.exe" --uninstall-apply "%CHOICES_FILE%" "%RESULT_FILE%" "%AUTH_FILE%"
echo [hots_uninstall] Cleanup step finished (exit code !errorlevel!). >> "%LOG%"

set "DELETE_DATA=0"
if exist "%RESULT_FILE%" (
    type "%RESULT_FILE%" >> "%LOG%"
    echo. >> "%LOG%"
    findstr /c:"\"delete_data\": true" "%RESULT_FILE%" >nul 2>&1
    if not errorlevel 1 set "DELETE_DATA=1"
    del /f /q "%RESULT_FILE%" >nul 2>&1
) else (
    echo [hots_uninstall] WARNING: no result from the cleanup step - keeping saved configuration to be safe. >> "%LOG%"
)

if "%DELETE_DATA%"=="1" (
    if exist "%MACHINE_DIR%" (
        echo [hots_uninstall] Removing data folder: %MACHINE_DIR% ... >> "%LOG%"
        attrib -R -H -S "%MACHINE_DIR%\*.*" /S /D >nul 2>&1
        rmdir /s /q "%MACHINE_DIR%" >nul 2>&1
        if exist "%MACHINE_DIR%" (
            echo [hots_uninstall] WARNING: could not fully remove %MACHINE_DIR% >> "%LOG%"
        ) else (
            echo [hots_uninstall] Removed %MACHINE_DIR% >> "%LOG%"
        )
    ) else (
        echo [hots_uninstall] Folder %MACHINE_DIR% does not exist - skipping. >> "%LOG%"
    )

    if exist "%USER_DIR%" (
        echo [hots_uninstall] Removing data folder: %USER_DIR% ... >> "%LOG%"
        attrib -R -H -S "%USER_DIR%\*.*" /S /D >nul 2>&1
        rmdir /s /q "%USER_DIR%" >nul 2>&1
        if exist "%USER_DIR%" (
            echo [hots_uninstall] WARNING: could not fully remove %USER_DIR% >> "%LOG%"
        ) else (
            echo [hots_uninstall] Removed %USER_DIR% >> "%LOG%"
        )
    ) else (
        echo [hots_uninstall] Folder %USER_DIR% does not exist - skipping. >> "%LOG%"
    )
) else (
    echo [hots_uninstall] Keeping saved configuration in %MACHINE_DIR% and %USER_DIR%. >> "%LOG%"
)

echo [hots_uninstall] Done. >> "%LOG%"

endlocal
exit /b 0
