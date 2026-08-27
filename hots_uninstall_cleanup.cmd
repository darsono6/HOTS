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

set "PS1_FILE=%TEMP%\hots_uninstall_cleanup_%RANDOM%.ps1"
set "VERIFY_PS1=%TEMP%\hots_uninstall_verify_%RANDOM%.ps1"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [hots_uninstall] Not running as administrator - elevating via UAC...
    powershell -NoProfile -Command "$p = Start-Process -FilePath '%~f0' -Verb RunAs -Wait -PassThru; exit $p.ExitCode"
    exit /b %errorlevel%
)

> "%VERIFY_PS1%" echo $ErrorActionPreference = 'SilentlyContinue'
>> "%VERIFY_PS1%" echo Add-Type -AssemblyName System.Windows.Forms
>> "%VERIFY_PS1%" echo Add-Type -AssemblyName System.Drawing
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo $exePath = '%~dp0HOTS Hosts.exe'
>> "%VERIFY_PS1%" echo if (-not (Test-Path -LiteralPath $exePath)) { exit 2 }
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo $storedHash = $null
>> "%VERIFY_PS1%" echo try {
>> "%VERIFY_PS1%" echo     $storedHash = (Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\HOTS Hosts' -Name AppPasswordHash -ErrorAction Stop).AppPasswordHash
>> "%VERIFY_PS1%" echo } catch {}
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo if ([string]::IsNullOrEmpty($storedHash)) { exit 0 }
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo function Test-HotsUninstallPassword([string]$plain) {
>> "%VERIFY_PS1%" echo     $tmp = [System.IO.Path]::GetTempFileName()
>> "%VERIFY_PS1%" echo     try {
>> "%VERIFY_PS1%" echo         $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
>> "%VERIFY_PS1%" echo         [System.IO.File]::WriteAllText($tmp, $plain, $utf8NoBom)
>> "%VERIFY_PS1%" echo         $p = Start-Process -FilePath $exePath -ArgumentList @('--verify-uninstall-password', $tmp) -Wait -PassThru -WindowStyle Hidden
>> "%VERIFY_PS1%" echo         return ($p.ExitCode -eq 0)
>> "%VERIFY_PS1%" echo     } finally {
>> "%VERIFY_PS1%" echo         Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
>> "%VERIFY_PS1%" echo     }
>> "%VERIFY_PS1%" echo }
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo $attempts = 0
>> "%VERIFY_PS1%" echo $verified = $false
>> "%VERIFY_PS1%" echo while ($attempts -lt 3) {
>> "%VERIFY_PS1%" echo     $form = New-Object System.Windows.Forms.Form
>> "%VERIFY_PS1%" echo     $form.Text = 'HOTS Hosts'
>> "%VERIFY_PS1%" echo     $form.ClientSize = New-Object System.Drawing.Size(360,150)
>> "%VERIFY_PS1%" echo     $form.FormBorderStyle = 'FixedDialog'
>> "%VERIFY_PS1%" echo     $form.StartPosition = 'CenterScreen'
>> "%VERIFY_PS1%" echo     $form.MaximizeBox = $false
>> "%VERIFY_PS1%" echo     $form.MinimizeBox = $false
>> "%VERIFY_PS1%" echo     $form.TopMost = $true
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     $lbl = New-Object System.Windows.Forms.Label
>> "%VERIFY_PS1%" echo     $lbl.Text = 'This program is password protected. Enter the password to continue:'
>> "%VERIFY_PS1%" echo     $lbl.SetBounds(16,16,320,40)
>> "%VERIFY_PS1%" echo     $form.Controls.Add($lbl)
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     $edit = New-Object System.Windows.Forms.TextBox
>> "%VERIFY_PS1%" echo     $edit.SetBounds(16,60,320,24)
>> "%VERIFY_PS1%" echo     $edit.UseSystemPasswordChar = $true
>> "%VERIFY_PS1%" echo     $form.Controls.Add($edit)
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     $btnOk = New-Object System.Windows.Forms.Button
>> "%VERIFY_PS1%" echo     $btnOk.Text = 'OK'
>> "%VERIFY_PS1%" echo     $btnOk.SetBounds(180,96,75,28)
>> "%VERIFY_PS1%" echo     $btnOk.DialogResult = [System.Windows.Forms.DialogResult]::OK
>> "%VERIFY_PS1%" echo     $form.Controls.Add($btnOk)
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     $btnCancel = New-Object System.Windows.Forms.Button
>> "%VERIFY_PS1%" echo     $btnCancel.Text = 'Cancel'
>> "%VERIFY_PS1%" echo     $btnCancel.SetBounds(261,96,75,28)
>> "%VERIFY_PS1%" echo     $btnCancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
>> "%VERIFY_PS1%" echo     $form.Controls.Add($btnCancel)
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     $form.AcceptButton = $btnOk
>> "%VERIFY_PS1%" echo     $form.CancelButton = $btnCancel
>> "%VERIFY_PS1%" echo     $form.Add_Shown({ $edit.Focus() })
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     $dlgResult = $form.ShowDialog()
>> "%VERIFY_PS1%" echo     if ($dlgResult -ne [System.Windows.Forms.DialogResult]::OK) { break }
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     if (Test-HotsUninstallPassword $edit.Text) {
>> "%VERIFY_PS1%" echo         $verified = $true
>> "%VERIFY_PS1%" echo         break
>> "%VERIFY_PS1%" echo     }
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo     $attempts++
>> "%VERIFY_PS1%" echo     $left = 3 - $attempts
>> "%VERIFY_PS1%" echo     if ($attempts -lt 3) {
>> "%VERIFY_PS1%" echo         [System.Windows.Forms.MessageBox]::Show('Incorrect password. Attempts remaining: ' + $left, 'HOTS Hosts', 'OK', 'Error') ^| Out-Null
>> "%VERIFY_PS1%" echo     } else {
>> "%VERIFY_PS1%" echo         [System.Windows.Forms.MessageBox]::Show('Too many failed attempts. Operation aborted.', 'HOTS Hosts', 'OK', 'Error') ^| Out-Null
>> "%VERIFY_PS1%" echo     }
>> "%VERIFY_PS1%" echo }
>> "%VERIFY_PS1%" echo.
>> "%VERIFY_PS1%" echo if ($verified) { exit 0 } else { exit 1 }

powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%VERIFY_PS1%"
set "PWCHECK_RESULT=%errorlevel%"
del /f /q "%VERIFY_PS1%" >nul 2>&1
if "%PWCHECK_RESULT%"=="2" (
    echo [hots_uninstall] "HOTS Hosts.exe" not found next to this script - not running from the install folder, aborting for safety, no changes made.
    pause
    exit /b 1
)
if not "%PWCHECK_RESULT%"=="0" (
    echo [hots_uninstall] Password verification failed or was cancelled - aborting, no changes made.
    pause
    exit /b 1
)
echo [hots_uninstall] Verified - proceeding with cleanup.

echo [hots_uninstall] Removing hosts file lock, app-block entries, restore-point block, DoH policies and password key...

> "%PS1_FILE%" echo $ErrorActionPreference = 'SilentlyContinue'
>> "%PS1_FILE%" echo $sid = New-Object System.Security.Principal.SecurityIdentifier('S-1-5-32-545')
>> "%PS1_FILE%" echo $blockerCmd = 'C:\Windows\System32\__hots_blocked__.exe'
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo function Remove-HotsDenyAcl($path) {
>> "%PS1_FILE%" echo     if (-not (Test-Path -LiteralPath $path)) { return }
>> "%PS1_FILE%" echo     try {
>> "%PS1_FILE%" echo         $acl = Get-Acl -LiteralPath $path
>> "%PS1_FILE%" echo         $toRemove = @($acl.Access ^| Where-Object { $_.AccessControlType -eq 'Deny' -and ($_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value -eq $sid.Value) })
>> "%PS1_FILE%" echo         foreach ($rule in $toRemove) { $acl.RemoveAccessRule($rule) ^| Out-Null }
>> "%PS1_FILE%" echo         if ($toRemove.Count -gt 0) { Set-Acl -LiteralPath $path -AclObject $acl }
>> "%PS1_FILE%" echo     } catch {}
>> "%PS1_FILE%" echo }
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo Remove-HotsDenyAcl 'C:\Windows\System32\drivers\etc\hosts'
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo $appState = Join-Path $env:APPDATA 'HOTS Hosts\appblock_state.json'
>> "%PS1_FILE%" echo if (Test-Path $appState) {
>> "%PS1_FILE%" echo     try {
>> "%PS1_FILE%" echo         $apps = Get-Content -LiteralPath $appState -Raw ^| ConvertFrom-Json
>> "%PS1_FILE%" echo         foreach ($a in $apps) { if ($a.locked_path) { Remove-HotsDenyAcl $a.locked_path } }
>> "%PS1_FILE%" echo     } catch {}
>> "%PS1_FILE%" echo }
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo $ifeoRoot = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options'
>> "%PS1_FILE%" echo if (Test-Path $ifeoRoot) {
>> "%PS1_FILE%" echo     Get-ChildItem $ifeoRoot ^| ForEach-Object {
>> "%PS1_FILE%" echo         $dbg = (Get-ItemProperty -LiteralPath $_.PSPath -Name Debugger -ErrorAction SilentlyContinue).Debugger
>> "%PS1_FILE%" echo         if ($dbg -eq $blockerCmd) { Remove-Item -LiteralPath $_.PSPath -Force -ErrorAction SilentlyContinue }
>> "%PS1_FILE%" echo     }
>> "%PS1_FILE%" echo }
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo function Remove-HotsRestorePointBlock {
>> "%PS1_FILE%" echo     $rstruiKey = Join-Path $ifeoRoot 'rstrui.exe'
>> "%PS1_FILE%" echo     if (Test-Path $rstruiKey) {
>> "%PS1_FILE%" echo         Remove-Item -LiteralPath $rstruiKey -Force -ErrorAction SilentlyContinue
>> "%PS1_FILE%" echo     }
>> "%PS1_FILE%" echo     $srPolicyKey = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\SystemRestore'
>> "%PS1_FILE%" echo     if (Test-Path $srPolicyKey) {
>> "%PS1_FILE%" echo         Remove-ItemProperty -LiteralPath $srPolicyKey -Name 'DisableSR' -ErrorAction SilentlyContinue
>> "%PS1_FILE%" echo         Remove-ItemProperty -LiteralPath $srPolicyKey -Name 'DisableConfig' -ErrorAction SilentlyContinue
>> "%PS1_FILE%" echo     }
>> "%PS1_FILE%" echo }
>> "%PS1_FILE%" echo Remove-HotsRestorePointBlock
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo function Remove-HotsRegValue($path, $name) {
>> "%PS1_FILE%" echo     if (Test-Path $path) {
>> "%PS1_FILE%" echo         Remove-ItemProperty -LiteralPath $path -Name $name -ErrorAction SilentlyContinue
>> "%PS1_FILE%" echo     }
>> "%PS1_FILE%" echo }
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo Remove-HotsRegValue 'HKLM:\SOFTWARE\Policies\Google\Chrome' 'DnsOverHttpsMode'
>> "%PS1_FILE%" echo Remove-HotsRegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'DnsOverHttpsMode'
>> "%PS1_FILE%" echo Remove-HotsRegValue 'HKLM:\SOFTWARE\Policies\BraveSoftware\Brave' 'DnsOverHttpsMode'
>> "%PS1_FILE%" echo Remove-HotsRegValue 'HKLM:\SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS' 'Enabled'
>> "%PS1_FILE%" echo Remove-HotsRegValue 'HKLM:\SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS' 'Locked'
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo $ffDohKey = 'HKLM:\SOFTWARE\Policies\Mozilla\Firefox\DNSOverHTTPS'
>> "%PS1_FILE%" echo if ((Test-Path $ffDohKey) -and (-not (Get-ItemProperty -LiteralPath $ffDohKey -ErrorAction SilentlyContinue ^| Get-Member -MemberType NoteProperty ^| Where-Object { $_.Name -notmatch '^PS' }))) {
>> "%PS1_FILE%" echo     Remove-Item -LiteralPath $ffDohKey -Force -ErrorAction SilentlyContinue
>> "%PS1_FILE%" echo }
>> "%PS1_FILE%" echo.
>> "%PS1_FILE%" echo Remove-Item -LiteralPath 'HKLM:\SOFTWARE\HOTS Hosts' -Recurse -Force -ErrorAction SilentlyContinue
>> "%PS1_FILE%" echo Remove-Item -LiteralPath 'HKCU:\SOFTWARE\HOTS Hosts' -Recurse -Force -ErrorAction SilentlyContinue

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1_FILE%"
if %errorlevel% neq 0 (
    echo [hots_uninstall] WARNING: cleanup script reported an error - continuing anyway.
) else (
    echo [hots_uninstall] hosts file lock, app-block entries, restore-point block, DoH policies and password key removed.
)
del /f /q "%PS1_FILE%" >nul 2>&1

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

echo [hots_uninstall] Done.

endlocal
exit /b 0
