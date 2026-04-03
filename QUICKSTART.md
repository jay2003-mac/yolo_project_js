# 🚀 Quick Start Guide

This document explains how to easily run all project commands using simple scripts.

## Choose Your Method

### Option 1: **PowerShell (Windows)** ⭐ RECOMMENDED FOR YOU

```powershell
# Show help
.\quickstart.ps1

# Generate data
.\quickstart.ps1 generate

# Validate dataset
.\quickstart.ps1 validate

# Train M3 model
.\quickstart.ps1 train

# Train M4 with custom settings (50 epochs, batch 16)
.\quickstart.ps1 train m4 50 16

# Train all screw types
.\quickstart.ps1 train-all

# List trained models
.\quickstart.ps1 list

# Show project status
.\quickstart.ps1 status
```

---

### Option 2: **Batch File (Windows)**

```batch
REM Show help
quickstart

REM Generate data
quickstart generate

REM Validate
quickstart validate

REM Train M3
quickstart train

REM Train M4 with 50 epochs, batch 16
quickstart train m4 50 16

REM Train all
quickstart train-all

REM List models
quickstart list
```

---

### Option 3: **Python Direct (All Platforms)**

```bash
python main.py generate
python main.py validate --type m3
python main.py train --type m3 --epochs 20 --batch 32
python main.py train-all --epochs 50
python main.py list
python main.py status
```

---

### Option 4: **Make (Linux/Mac)**

```bash
make help          # Show all commands
make generate      # Generate data
make validate      # Validate M3
make train         # Train M3
make train-all     # Train all types
make list          # List models
make status        # Show status
```

---

## Complete Workflow Example

### Windows PowerShell:
```powershell
# 1. Generate synthetic data (one-time setup)
.\quickstart.ps1 generate

# 2. Validate the data
.\quickstart.ps1 validate

# 3. Train model for M3 screws (default: 20 epochs)
.\quickstart.ps1 train

# 4. View available trained models
.\quickstart.ps1 list

# 5. Train other screw types
.\quickstart.ps1 train m4 20 32
.\quickstart.ps1 train m5 20 32
.\quickstart.ps1 train m6 20 32

# 6. Train all screw types together
.\quickstart.ps1 train-all 50

# 7. Check project status
.\quickstart.ps1 status
```

### Windows Batch:
```batch
quickstart generate
quickstart validate
quickstart train
quickstart list
quickstart status
```

### Linux/Mac:
```bash
make generate
make validate
make train
make train-all
make list
make status
```

---

## Available Commands

### Data Management

| Command | Purpose |
|---------|---------|
| `generate` | Create synthetic X-ray screw images (50 per type) |
| `validate [--type m3]` | Check dataset integrity and format |
| `camera` | Show camera calibration parameters |
| `status` | Display project overview |

### Training

| Command | Purpose |
|---------|---------|
| `train [type] [epochs] [batch]` | Train single screw type (default: M3, 20 epochs, 32 batch) |
| `train m4 50 16` | Train M4 with 50 epochs and batch size 16 |
| `train-all [epochs]` | Train all 4 screw types in sequence |

### Monitoring

| Command | Purpose |
|---------|---------|
| `list` | Show all trained model checkpoints |
| `status` | Summarize project state |

---

## Command Examples

### Generate Synthetic Data
```powershell
# One-time setup for the entire project
.\quickstart.ps1 generate
# Output: 200 images (50 per screw type), automatically annotated
```

### Validate Before Training
```powershell
# Check M3 dataset is valid
.\quickstart.ps1 validate

# Output should show:
# ✓ 50 total images
# ✓ 50 annotations
# ✓ All keypoints valid
```

### Quick Training (20 epochs)
```powershell
# Train M3 model quickly (good for testing)
.\quickstart.ps1 train

# Or with more epochs for better accuracy
.\quickstart.ps1 train m3 50 32
```

### Full Training Pipeline
```powershell
# Train all 4 screw types with 50 epochs each
.\quickstart.ps1 train-all 50

# Roughly 1-2 hours depending on your GPU
```

---

## Output Locations

After running commands, outputs appear in:

```
runs/train/
├── exp1/
│   └── weights/
│       ├── best.pt          # Best model (lowest loss)
│       └── last.pt          # Final checkpoint
├── exp2/
│   └── weights/
│       ├── best.pt
│       └── last.pt
└── ...
```

**To use a trained model:**
```powershell
python detect.py --weights runs/train/exp1/weights/best.pt --source data/XRAY_SCREWS/m3/JPEGImages/
```

---

## Troubleshooting

### "Python not found"
```powershell
# Ensure you're in the project directory
cd C:\Users\jayas\Desktop\Yolo\xray-screw-detection

# Or use full path
C:\Users\jayas\Desktop\Yolo\xray-screw-detection\.venv\Scripts\python.exe main.py generate
```

### "Module not found" errors
```powershell
# Reinstall dependencies
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### Training is slow
```powershell
# Use smaller batch size on slower hardware
.\quickstart.ps1 train m3 10 8   # 10 epochs, batch 8

# Or use CPU if GPU unavailable
python main.py train --batch 8 --device -1
```

### Out of memory
```powershell
# Reduce batch size
.\quickstart.ps1 train m3 20 8   # batch 8 instead of 32
```

---

## Next Steps

1. ✅ Run: `.\quickstart.ps1 generate`
2. ✅ Run: `.\quickstart.ps1 validate`
3. ✅ Run: `.\quickstart.ps1 train` (start with M3)
4. ✅ Check results: `.\quickstart.ps1 list`
5. ✅ Expand: Train other screw types

---

## Advanced Usage

### Custom Training Parameters
```powershell
# High accuracy (long training)
.\quickstart.ps1 train m3 100 32

# Fast training (quick testing)
.\quickstart.ps1 train m3 5 8

# Balanced speed/accuracy
.\quickstart.ps1 train m3 50 16
```

### Train All with Custom Epochs
```powershell
# PowerShell
.\quickstart.ps1 train-all 100

# Batch
quickstart train-all 100

# Python
python main.py train-all --epochs 100 --batch 16
```

### Check Project Status
```powershell
# See everything at a glance
.\quickstart.ps1 status

# Expected output:
# - Number of images per screw type
# - Available trained models
# - Camera calibration settings
```

---

## Questions?

See: `PROJECT_STATUS.md` for a detailed overview of the entire project.

---

**Recommended First Command:**
```powershell
.\quickstart.ps1 status
```
This shows your current project state!
