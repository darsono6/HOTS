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

set "RESULT_FILE=%TEMP%\hots_uninstall_result_%RANDOM%.json"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [hots_uninstall] Not running as administrator - elevating via UAC...
    powershell -NoProfile -Command "$p = Start-Process -FilePath '%~f0' -Verb RunAs -Wait -PassThru; exit $p.ExitCode"
    exit /b %errorlevel%
)

echo [hots_uninstall] Launching cleanup wizard...
"%~dp0HOTS Hosts.exe" --uninstall-cleanup "%RESULT_FILE%"
echo [hots_uninstall] Cleanup step finished.

set "DELETE_DATA=0"
if exist "%RESULT_FILE%" (
    findstr /c:"\"delete_data\": true" "%RESULT_FILE%" >nul 2>&1
    if not errorlevel 1 set "DELETE_DATA=1"
    del /f /q "%RESULT_FILE%" >nul 2>&1
) else (
    echo [hots_uninstall] WARNING: no result from the cleanup wizard - keeping saved configuration to be safe.
)

if "%DELETE_DATA%"=="1" (
    if exist "%MACHINE_DIR%" (
        echo [hots_uninstall] Removing data folder: %MACHINE_DIR% ...
        attrib -R -H -S "%MACHINE_DIR%\*.*" /S /D >nul 2>&1
        rmdir /s /q "%MACHINE_DIR%" >nul 2>&1
        if exist "%MACHINE_DIR%" (
            echo [hots_uninstall] WARNING: could not fully remove %MACHINE_DIR%
        ) else (
            echo [hots_uninstall] Removed %MACHINE_DIR%
        )
    ) else (
        echo [hots_uninstall] Folder %MACHINE_DIR% does not exist - skipping.
    )

    if exist "%USER_DIR%" (
        echo [hots_uninstall] Removing data folder: %USER_DIR% ...
        attrib -R -H -S "%USER_DIR%\*.*" /S /D >nul 2>&1
        rmdir /s /q "%USER_DIR%" >nul 2>&1
        if exist "%USER_DIR%" (
            echo [hots_uninstall] WARNING: could not fully remove %USER_DIR%
        ) else (
            echo [hots_uninstall] Removed %USER_DIR%
        )
    ) else (
        echo [hots_uninstall] Folder %USER_DIR% does not exist - skipping.
    )
) else (
    echo [hots_uninstall] Keeping saved configuration in %MACHINE_DIR% and %USER_DIR%, as requested in the wizard.
)

echo [hots_uninstall] Done.

endlocal
exit /b 0
