@echo off
setlocal DisableDelayedExpansion
set "PELICAN_PACKAGE_ROOT=%~dp0"
echo Preparing the offline Godot test project...
powershell.exe -NoLogo -NoProfile -Command "$ErrorActionPreference='Stop'; try { $root=$env:PELICAN_PACKAGE_ROOT; $code=[IO.File]::ReadAllText([IO.Path]::Combine($root,'prepare.ps1'),[Text.Encoding]::UTF8); & ([ScriptBlock]::Create($code)) -PackageRoot $root } catch { Write-Host ('PREPARATION FAILED: '+$_.Exception.Message); exit 1 }"
set "PREPARE_RESULT=%ERRORLEVEL%"
echo.
if not "%PREPARE_RESULT%"=="0" echo Preparation failed. Read the error above. No existing modified project files were replaced.
pause
exit /b %PREPARE_RESULT%
