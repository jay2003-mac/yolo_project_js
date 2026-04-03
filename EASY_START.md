# Easy-to-Use Scripts - Setup Complete! ✅

You now have **3 ways** to run all project commands with simple, easy-to-remember syntax.

---

## 🎯 **Quick Start (Choose One)**

### **Option 1: PowerShell (Recommended for Windows)**
```powershell
.\quickstart.ps1 status          # Check what you have
.\quickstart.ps1 generate        # Create synthetic data
.\quickstart.ps1 validate        # Verify data quality
.\quickstart.ps1 train           # Train M3 model
.\quickstart.ps1 train-all 50    # Train all types (50 epochs)
.\quickstart.ps1 list            # See trained models
```

### **Option 2: Batch File (Windows)**
```batch
quickstart status
quickstart generate
quickstart validate
quickstart train
quickstart train-all
quickstart list
```

### **Option 3: Python Direct (All Platforms)**
```bash
python main.py status
python main.py generate
python main.py validate
python main.py train --epochs 20
python main.py train-all --epochs 50
python main.py list
```

---

## 📋 **All Available Commands**

### Basic Commands
| Command | What it does |
|---------|------------|
| `status` | Show project overview (datasets, models, camera config) |
| `help` | Show detailed help menu |

### Data Handling
| Command | What it does |
|---------|------------|
| `generate` | Create 200 synthetic X-ray images (50 per screw type) |
| `validate` | Check if data is valid and ready for training |
| `camera` | Display camera calibration settings |

### Training Models
| Command | What it does |
|---------|------------|
| `train` | Train M3 model (default: 20 epochs, batch 32) |
| `train m4 50 16` | Train M4 with 50 epochs, batch size 16 |
| `train-all 30` | Train all 4 screw types with 30 epochs each |

### Model Management
| Command | What it does |
|---------|------------|
| `list` | Show all trained models and their locations |

---

## 🚀 **Step-by-Step Examples**

### Example 1: First Time Setup
```powershell
# 1. Check current state
.\quickstart.ps1 status

# 2. Generate synthetic data (if not done)
.\quickstart.ps1 generate

# 3. Validate the data
.\quickstart.ps1 validate

# 4. Train your first model
.\quickstart.ps1 train

# 5. See results
.\quickstart.ps1 list
```

### Example 2: Train All Screw Types
```powershell
# Quick training (10 epochs each)
.\quickstart.ps1 train-all 10

# Better accuracy (50 epochs each)
.\quickstart.ps1 train-all 50

# Production quality (100 epochs each)
.\quickstart.ps1 train-all 100
```

### Example 3: Custom Training
```powershell
# Train M4 with specific parameters
.\quickstart.ps1 train m4 50 32    # 50 epochs, batch 32

# Train M5 quickly for testing
.\quickstart.ps1 train m5 5 8      # 5 epochs, batch 8

# Train M6 with more accuracy
.\quickstart.ps1 train m6 100 16   # 100 epochs, batch 16
```

---

## 📊 **Before You Start Training**

Run this to see current state:
```powershell
.\quickstart.ps1 status
```

Expected output:
```
✓ Datasets:
  M3: 50 images
  M4: 50 images
  M5: 50 images
  M6: 50 images

✓ Trained Models:
  (none yet - train your first one!)

✓ Camera Configuration:
  fx=1200.0, fy=1200.0
  u0=320.0, v0=240.0
```

---

## 🎬 **Now Run Your First Training!**

### Simple (fastest):
```powershell
.\quickstart.ps1 train
# Trains M3 model with default settings (20 epochs)
# Takes ~2 minutes
```

### Balanced:
```powershell
.\quickstart.ps1 train m3 50 32
# Trains M3 model with 50 epochs, batch 32
# Takes ~5 minutes
# Better accuracy than simple version
```

### High Quality:
```powershell
.\quickstart.ps1 train m3 100 32
# Trains M3 model with 100 epochs
# Takes ~10 minutes
# Best accuracy
```

---

## 📈 **After Training Completes**

1. **View results:**
   ```powershell
   .\quickstart.ps1 list
   ```
   This shows where your trained model was saved!

2. **Train other screw types:**
   ```powershell
   .\quickstart.ps1 train m4
   .\quickstart.ps1 train m5
   .\quickstart.ps1 train m6
   ```

3. **Train all together:**
   ```powershell
   .\quickstart.ps1 train-all 50
   ```

4. **Use the trained model:**
   ```bash
   python detect.py --weights runs/train/exp1/weights/best.pt \
     --source data/XRAY_SCREWS/m3/JPEGImages/
   ```

---

## ⚙️ **Under the Hood**

These scripts call the Python backend:

```
quickstart.ps1 / quickstart.bat
        ↓
main.py (command dispatcher)
        ↓
train.py / validate.py / generate_synthetic_data.py
        ↓
Actual training happens here
```

---

## 💾 **File Structure**

Created for you:
- ✅ `main.py` - Main command dispatcher (what scripts call)
- ✅ `quickstart.ps1` - PowerShell interface (BEST FOR YOU)
- ✅ `quickstart.bat` - Batch file interface
- ✅ `Makefile` - Make interface (for Linux/Mac users)
- ✅ `QUICKSTART.md` - Detailed documentation

---

## 🔍 **Troubleshooting**

### "Command not found" or "not recognized"
Solution: Make sure you're in the project directory:
```powershell
cd C:\Users\jayas\Desktop\Yolo\xray-screw-detection
.\quickstart.ps1 train
```

### Training is slow
Solution: Use smaller batch size:
```powershell
.\quickstart.ps1 train m3 20 8  # batch 8 instead of 32
```

### Out of memory errors
Solution: Reduce batch size even more:
```powershell
.\quickstart.ps1 train m3 20 4  # batch 4
```

### Need to see full help
```powershell
.\quickstart.ps1 help
```

---

## 📝 **Recommended Workflow**

```powershell
# Day 1: Setup and test
.\quickstart.ps1 status           # Check what's ready
.\quickstart.ps1 validate         # Verify data
.\quickstart.ps1 train            # Quick test (20 epochs)
.\quickstart.ps1 list             # See the model

# Day 2+: Full training
.\quickstart.ps1 train-all 50     # Train all types with 50 epochs
.\quickstart.ps1 status           # Check results
```

---

## ✨ **Next Steps**

**Right now, run this:**
```powershell
.\quickstart.ps1 train
```

This will:
1. Load the 40 training images
2. Train the CNN model on M3 screws
3. Validate on 10 test images
4. Save the best model
5. Display results

**ETA: ~2 minutes**

After it completes:
```powershell
.\quickstart.ps1 list
```

This shows where your model was saved!

---

## 🎓 **Learning Resources**

- `QUICKSTART.md` - Detailed command guide
- `PROJECT_STATUS.md` - Project overview
- `SYNTHETIC_DATASET_SUMMARY.md` - Dataset documentation
- `train.py` - Training script (read to understand model)
- `main.py` - Command dispatcher (see how commands work)

---

**You're all set! 🚀**

Run this now:
```powershell
.\quickstart.ps1 train
```

Then check back here:
```powershell
.\quickstart.ps1 list
```

Happy training! 🎉
