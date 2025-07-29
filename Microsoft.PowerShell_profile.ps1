--# Enhanced Intelligent PowerShell Profile with AI Capabilities

# 1. Core AI Setup
$env:PYTHONIOENCODING = "UTF-8"
$env:AI_CONTEXT_PATH = "$env:USERPROFILE\.ai_context"
$env:CHAT_HISTORY_PATH = "$env:USERPROFILE\.chat_history"

# 2. AI File System Integration
function Get-AIFile {
  param([string]$path)
  python -c "from aifiles import analyze_file; analyze_file('$path')"
}

function New-AIChatFile {
  param([string]$content)
  $timestamp = Get-Date -Format "yyyyMMddHHmmss"
  $filePath = "$env:CHAT_HISTORY_PATH\chat_$timestamp.txt"
  $content | Out-File -FilePath $filePath -Encoding UTF8
  return $filePath
}

# 3. Enhanced Command Processing
function Invoke-AICommand {
  param([string]$command)

  # Get context-aware command suggestion
  $aiCommand = python -c "from pipelines import analyze_task; analyze_task('$command')"

  # Log to chat history
  $logEntry = "[$(Get-Date)] COMMAND: $command`nAI SUGGESTION: $aiCommand"
  New-AIChatFile -content $logEntry | Out-Null

  # Execute with error handling
  try {
    Invoke-Expression $aiCommand
  }
  catch {
    Write-Host "AI Suggestion Failed: $_" -ForegroundColor Red
    return $false
  }
  return $true
}

# 4. System Automation Functions
function Invoke-SystemCheck {
  python -c "from healthcheck import system_health_check; system_health_check()"
}

function Start-AIChatSession {
  while ($true) {
    $input = Read-Host "`n[AI Assistant] How can I help you?"
    if ($input -eq "exit") { break }
    Invoke-AICommand $input
  }
}

# 5. Initialize Environment
if (-not (Test-Path $env:AI_CONTEXT_PATH)) {
  python -c "from ai_context import initialize; initialize()"
}

# Start in chat mode by default
Start-AIChatSession
