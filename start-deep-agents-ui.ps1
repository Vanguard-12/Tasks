$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$UiRoot = Join-Path $ProjectRoot "ui"
$LangGraph = Join-Path $ProjectRoot ".venv\Scripts\langgraph.exe"
$Next = Join-Path $UiRoot "node_modules\.bin\next.cmd"
$BundledNodeBin = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin"

if (-not (Test-Path $LangGraph)) {
    throw "LangGraph CLI was not found at $LangGraph. Run: .venv\Scripts\python.exe -m pip install -e ."
}

if (-not (Test-Path $UiRoot)) {
    throw "Deep Agents UI folder was not found at $UiRoot."
}

if (-not (Test-Path $Next)) {
    throw "Next.js was not found at $Next. Install UI dependencies first."
}

$extraPath = ""
if (-not (Get-Command node -ErrorAction SilentlyContinue) -and (Test-Path $BundledNodeBin)) {
    $extraPath = "$BundledNodeBin;"
}

$apiCommand = "cd `"$ProjectRoot`"; & `"$LangGraph`" dev --no-browser --no-reload --allow-blocking --port 2025"
$uiCommand = "`$env:PATH='$extraPath' + `$env:PATH; cd `"$UiRoot`"; & `"$Next`" dev --turbopack"

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $apiCommand
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $uiCommand

Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"
