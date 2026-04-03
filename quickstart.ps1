# X-Ray Screw Detection - PowerShell Quick Commands
# Usage: .\quickstart.ps1 [command] [args...]

param(
    [string]$Command = "",
    [string[]]$Args = @()
)

$Python = ".\.venv\Scripts\python.exe"
$Main = "main.py"

function Show-Help {
    Write-Host "`n$('='*60)" -ForegroundColor Cyan
    Write-Host "  X-Ray Screw Detection - Quick Start" -ForegroundColor Cyan
    Write-Host "$('='*60)`n" -ForegroundColor Cyan
    
    Write-Host "AVAILABLE COMMANDS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  .\quickstart.ps1 generate [size]  - Generate synthetic data" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 validate [type]  - Validate dataset" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 train [args...]  - Train model (M3)" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 train-all [size] - Train all screw types" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 list             - List trained models" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 status           - Show project status" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 camera           - Show camera config" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "DATASET SIZE OPTIONS:" -ForegroundColor Yellow
    Write-Host "  50   - Quick test (200 total images)" -ForegroundColor Gray
    Write-Host "  100  - Small dataset (400 total images)" -ForegroundColor Gray
    Write-Host "  300  - Medium dataset (1,200 total images) [Recommended]" -ForegroundColor Gray
    Write-Host "  500  - Large dataset (2,000 total images)" -ForegroundColor Gray
    Write-Host "  1000 - Extra large (4,000 total images)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\quickstart.ps1 generate         # Generate 50 per type" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 generate 300     # Generate 300 per type (1,200 total)" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 generate 500     # Generate 500 per type (2,000 total)" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 train            # Train M3 model" -ForegroundColor Green
    Write-Host "  .\quickstart.ps1 train m4 50 16   # Train M4, 50 epochs, batch 16" -ForegroundColor Green
    Write-Host ""
}

function Invoke-Command {
    param([string]$Cmd, [string[]]$CmdArgs)
    
    switch($Cmd) {
        "generate" {
            $numImages = if ($CmdArgs.Count -gt 0) { $CmdArgs[0] } else { "50" }
            $total = [int]$numImages * 4
            Write-Host "Generating synthetic dataset ($numImages images per type, $total total)..." -ForegroundColor Cyan
            & $Python $Main generate --num-images $numImages
        }
        "validate" {
            $type = if ($CmdArgs.Count -gt 0) { $CmdArgs[0] } else { "m3" }
            Write-Host "Validating $type dataset..." -ForegroundColor Cyan
            & $Python $Main validate --type $type
        }
        "train" {
            $type = if ($CmdArgs.Count -gt 0) { $CmdArgs[0] } else { "m3" }
            $epochs = if ($CmdArgs.Count -gt 1) { $CmdArgs[1] } else { "20" }
            $batch = if ($CmdArgs.Count -gt 2) { $CmdArgs[2] } else { "32" }
            Write-Host "Training $type model (epochs=$epochs, batch=$batch)..." -ForegroundColor Cyan
            & $Python $Main train --type $type --epochs $epochs --batch $batch
        }
        "train-all" {
            $epochs = if ($CmdArgs.Count -gt 0) { $CmdArgs[0] } else { "20" }
            Write-Host "Training all screw types (epochs=$epochs)..." -ForegroundColor Cyan
            & $Python $Main train-all --epochs $epochs
        }
        "list" {
            & $Python $Main list
        }
        "status" {
            & $Python $Main status
        }
        "camera" {
            & $Python $Main camera
        }
        "help" {
            & $Python $Main help
        }
        default {
            if ($Cmd -ne "") {
                Write-Host "Unknown command: $Cmd" -ForegroundColor Red
            }
            Show-Help
        }
    }
}

# Main execution
if ($Command -eq "") {
    Show-Help
} else {
    Invoke-Command -Cmd $Command -CmdArgs $Args
}
