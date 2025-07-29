# PowerShell Profile Configuration
$env:PYTHONIOENCODING="UTF-8"
$env:PATH="$env:PATH;C:\Windows\System32"
Set-StrictMode -Version Latest
function global:prompt {
    "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
}
