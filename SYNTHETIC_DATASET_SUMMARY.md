# Synthetic Dataset Generation - Complete ✅

**Generated:** April 2, 2026  
**Dataset Size:** 200 synthetic X-ray screw images (50 per screw type)  
**Screw Types:** M3, M4, M5, M6

## What Was Created

### 📁 Directory Structure
```
data/XRAY_SCREWS/
├── m3/
│   ├── JPEGImages/          ✅ 50 synthetic X-ray images
│   ├── Annotations/         ✅ 50 annotation files (YOLO format)
│   ├── m3.ply              ✅ 3D screw model (PLY format)
│   ├── train.txt           ✅ 40 training image paths
│   ├── test.txt            ✅ 10 test image paths
│   └── training_range.txt  ✅ Pose range for training
├── m4/
│   ├── JPEGImages/         ✅ 50 images
│   ├── Annotations/        ✅ 50 annotations
│   ├── m4.ply             ✅ 3D model
│   ├── train.txt          ✅ Split files
│   └── test.txt           ✅ Split files
├── m5/                      (similar structure)
├── m6/                      (similar structure)
└── VOC_background/          (ready for background images)
```

### 📋 Dataset Details

**Image Count:** 200 total
- M3: 50 images (40 train, 10 test)
- M4: 50 images (40 train, 10 test)
- M5: 50 images (40 train, 10 test)
- M6: 50 images (40 train, 10 test)

**Image Format:** 
- JPEG, 640×480 pixels
- Synthetic X-ray style (grayscale-like with noise)
- Realistic camera projection with 3D geometry

**Annotation Format:** YOLO 6-DoF Keypoint Format
```
class_id x0 y0 x1 y1 x2 y2 ... x8 y8 width_norm height_norm
```
- class_id: 0=M3, 1=M4, 2=M5, 3=M6
- 9 keypoints per image: center + 8 corners
- Normalized coordinates [0, 1]
- Example: `0 0.428 0.525 0.428 0.473 0.519 0.575 ... 1.0 1.0`

### 🔧 Camera Calibration

**File:** `configs/screws/screw_camera.json`

```json
{
  "fx": 1200.0,
  "fy": 1200.0,
  "u0": 320.0,
  "v0": 240.0,
  "resolution": [640, 480],
  "source": "synthetic_data"
}
```

**Parameters:**
- `fx, fy`: Focal length (pixels) - typical for medium-resolution detectors
- `u0, v0`: Principal point (image center)
- Resolution: 640×480 pixels (standard X-ray detector size)

### 🎯 3D Screw Models

Each screw type has a PLY file with realistic dimensions:

| Model | Diameter | Head Diameter | Head Height | Length |
|-------|----------|---------------|-------------|--------|
| M3.ply | 3.0 mm | 5.5 mm | 2.0 mm | 16 mm |
| M4.ply | 4.0 mm | 7.0 mm | 2.7 mm | 20 mm |
| M5.ply | 5.0 mm | 8.5 mm | 3.5 mm | 25 mm |
| M6.ply | 6.0 mm | 10.0 mm | 4.0 mm | 30 mm |

## Next Steps

### ✅ STEP 1: Validate Dataset Quality

Check if annotations are correct and images load properly:

```bash
python data_curation/validate_dataset.py --dataset data/XRAY_SCREWS/m3 --visualize
```

This will:
- Load all images and annotations
- Check for missing files
- Verify keypoint validity
- Optionally display annotated images

### ✅ STEP 2: Prepare for Training

Create combined dataset config if training on all screw types:

```bash
# For single screw type (easier to debug):
python train.py --data configs/screws/m3.yaml --batch 32 --epochs 20 --device 0

# For all screw types:
python train.py --data configs/screws/screw_all.yaml --batch 32 --epochs 20 --device 0
```

### ✅ STEP 3: Train the Model

```bash
# Start training!
python train.py \
  --cfg models/yolov5s_screw_bifpn.yaml \
  --data configs/screws/m3.yaml \
  --batch 32 \
  --epochs 50 \
  --img 640 \
  --device 0 \
  --optimizer Adam
```

### ✅ STEP 4: Monitor Training

```bash
tensorboard --logdir runs/
# Open http://localhost:6006
```

## Annotation Format Details

Each image has corresponding `.txt` file in `Annotations/` folder.

**9 Keypoints Layout:**
```
      8 ─────────────── 7
     /│              /│
    6 ─────────────── 5 │
    │ 4 ────────────│── 3
    │/              │ /
    0 ────────────── 1
    
Keypoint 0: Center of screw head
Keypoint 1-8: Eight corners of 3D bounding box
```

**Example annotation file (m3_0000.txt):**
```
0 0.428125 0.525000 0.428125 0.472917 0.518750 0.575000 0.409375 0.556250 0.496875 0.666667 0.448437 0.522917 0.540625 0.627083 0.389062 0.506250 0.475000 0.612500 1.0 1.0
│ └─────── center ────────┘ └──────────── corner 1-8 ───────────────────────┘ └ norm factors┘
└ class_id (0=M3)
```

## Important Notes

1. **Synthetic vs Real Data**: This dataset is perfect for prototyping but won't match real X-ray image statistics. Performance on synthetic data may be 2-3x better than on real data.

2. **Domain Gap**: Once you have real X-ray images, you'll likely need to:
   - Fine-tune the model on real data
   - Adjust hyperparameters
   - Add data augmentation for real image characteristics

3. **Camera Calibration**: For real deployment, you MUST update `screw_camera.json` with your actual X-ray detector calibration values.

4. **Expanding the Dataset**: To add more images:
   ```bash
   python data_curation/generate_synthetic_data.py  # (modify num_images_per_screw)
   ```

## Quick Commands Reference

```bash
# Validate and visualize dataset
python data_curation/validate_dataset.py --dataset data/XRAY_SCREWS/m3 --visualize

# Train M3 model
python train.py --data configs/screws/m3.yaml --batch 32 --epochs 50 --device 0

# Test trained model
python test.py --weights runs/train/exp/weights/best.pt --data configs/screws/m3.yaml

# Run inference
python detect.py --weights runs/train/exp/weights/best.pt --source data/XRAY_SCREWS/m3/JPEGImages/ --static-camera configs/screws/screw_camera.json
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | `pip install -r requirements.txt` |
| CUDA not found | Use `--device cpu` for CPU training |
| Out of memory | Reduce `--batch` size (16 or 8) |
| Low accuracy | Increase `--epochs` (100+), use larger model |

---

**Status:** ✅ Ready to train!

Next command to run:
```bash
python data_curation/validate_dataset.py --dataset data/XRAY_SCREWS/m3 --visualize
```
