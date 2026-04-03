#!/usr/bin/env python3
"""
Validate X-ray screw detection dataset
Checks image-annotation pairs, coordinate ranges, format consistency, etc.
"""

import cv2
import numpy as np
from pathlib import Path
import json

class DatasetValidator:
    """Validate dataset for training readiness"""
    
    def __init__(self, dataset_dir):
        self.dataset_dir = Path(dataset_dir)
        self.images_dir = self.dataset_dir / "JPEGImages"
        self.annotations_dir = self.dataset_dir / "Annotations"
        self.issues = []
        self.warnings = []
        self.stats = {
            "total_images": 0,
            "images_with_annotations": 0,
            "images_without_annotations": 0,
            "keypoints_total": 0,
            "avg_image_shape": None,
            "coord_range": {"min": 1.0, "max": 0.0},
        }
    
    def validate_directories(self):
        """Check if required directories exist"""
        if not self.images_dir.exists():
            self.issues.append(f"Missing directory: {self.images_dir}")
            return False
        
        if not self.annotations_dir.exists():
            self.warnings.append(f"Annotations directory doesn't exist: {self.annotations_dir}")
            self.annotations_dir.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def validate_image_annotation_pairs(self):
        """Check that each image has a corresponding annotation"""
        image_files = list(self.images_dir.glob("*.jpg")) + list(self.images_dir.glob("*.png"))
        self.stats["total_images"] = len(image_files)
        
        if not image_files:
            self.issues.append(f"No images found in {self.images_dir}")
            return
        
        print(f"\n📊 Checking {len(image_files)} images...")
        
        image_shapes = []
        
        for img_path in image_files:
            txt_path = self.annotations_dir / f"{img_path.stem}.txt"
            
            if not txt_path.exists():
                self.warnings.append(f"No annotation for: {img_path.name}")
                self.stats["images_without_annotations"] += 1
            else:
                self.stats["images_with_annotations"] += 1
            
            image = cv2.imread(str(img_path))
            if image is None:
                self.issues.append(f"Cannot read image: {img_path.name}")
                continue
            
            image_shapes.append(image.shape)
            
            if image.ndim != 3:
                self.issues.append(f"Invalid image format (not 3-channel): {img_path.name}")
            
            if image.shape[2] != 3:
                self.issues.append(f"Invalid channel count: {img_path.name} has {image.shape[2]} channels")
        
        if image_shapes:
            avg_h = int(np.mean([s[0] for s in image_shapes]))
            avg_w = int(np.mean([s[1] for s in image_shapes]))
            self.stats["avg_image_shape"] = (avg_h, avg_w)
    
    def validate_annotations(self):
        """Check annotation file format and values"""
        annotation_files = list(self.annotations_dir.glob("*.txt"))
        
        print(f"\n✍️  Checking {len(annotation_files)} annotations...")
        
        for txt_path in annotation_files:
            try:
                with open(txt_path) as f:
                    line = f.read().strip()
                
                if not line:
                    self.issues.append(f"Empty annotation: {txt_path.name}")
                    continue
                
                parts = line.split()
                
                if len(parts) != 21:
                    self.issues.append(
                        f"Invalid format in {txt_path.name}: "
                        f"expected 21 values, got {len(parts)}"
                    )
                    continue
                
                try:
                    class_id = int(parts[0])
                    if class_id < 0:
                        self.issues.append(f"Negative class ID in {txt_path.name}")
                except ValueError:
                    self.issues.append(f"Non-integer class ID in {txt_path.name}")
                    continue
                
                try:
                    coords = [float(p) for p in parts[1:19]]
                    dims = [float(p) for p in parts[19:21]]
                    
                    for i, coord in enumerate(coords):
                        if coord < 0 or coord > 1:
                            self.warnings.append(
                                f"Out-of-range coordinate in {txt_path.name} "
                                f"(point {i}, value {coord:.3f})"
                            )
                        
                        self.stats["coord_range"]["min"] = min(self.stats["coord_range"]["min"], coord)
                        self.stats["coord_range"]["max"] = max(self.stats["coord_range"]["max"], coord)
                    
                    if dims[0] != 1.0 or dims[1] != 1.0:
                        self.warnings.append(
                            f"Unexpected dimensions in {txt_path.name}: {dims} "
                            f"(expected [1.0, 1.0])"
                        )
                    
                    self.stats["keypoints_total"] += 9
                    
                except ValueError as e:
                    self.issues.append(f"Non-numeric coordinates in {txt_path.name}: {e}")
            
            except Exception as e:
                self.issues.append(f"Error reading {txt_path.name}: {e}")
    
    def generate_report(self):
        """Print validation report"""
        print("\n" + "=" * 70)
        print("DATASET VALIDATION REPORT")
        print("=" * 70)
        
        print(f"\n📊 STATISTICS:")
        print(f"  Total images: {self.stats['total_images']}")
        print(f"  Annotated: {self.stats['images_with_annotations']}")
        print(f"  Missing annotations: {self.stats['images_without_annotations']}")
        print(f"  Total keypoints: {self.stats['keypoints_total']}")
        if self.stats['avg_image_shape']:
            print(f"  Average image shape: {self.stats['avg_image_shape']}")
        print(f"  Coordinate range: [{self.stats['coord_range']['min']:.4f}, {self.stats['coord_range']['max']:.4f}]")
        
        if self.issues:
            print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
            for issue in self.issues[:10]:
                print(f"   • {issue}")
            if len(self.issues) > 10:
                print(f"   ... and {len(self.issues) - 10} more")
        else:
            print(f"\n✅ No critical issues found")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"   • {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        
        print("\n" + "=" * 70)
        if not self.issues and self.stats['images_with_annotations'] > 10:
            print("✅ READY FOR TRAINING")
        elif not self.issues and self.stats['images_with_annotations'] >= 0:
            print("⚠️  READY FOR TRAINING BUT NEEDS MORE DATA (recommend >100 images)")
        else:
            print("❌ NOT READY FOR TRAINING (fix critical issues first)")
        print("=" * 70)
    
    def run(self):
        """Run full validation"""
        if not self.validate_directories():
            return
        
        self.validate_image_annotation_pairs()
        self.validate_annotations()
        self.generate_report()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate screw detection dataset")
    parser.add_argument("--dataset", default="data/XRAY_SCREWS/m3",
                       help="Dataset directory (e.g., data/XRAY_SCREWS/m3)")
    
    args = parser.parse_args()
    
    validator = DatasetValidator(args.dataset)
    validator.run()

if __name__ == "__main__":
    main()
