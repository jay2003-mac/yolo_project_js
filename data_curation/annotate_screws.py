#!/usr/bin/env python3
"""
Interactive annotation tool for 6-DoF screw keypoint labeling
Click 9 points: 1 center + 8 corners of screw head bounding box
"""

import cv2
import numpy as np
from pathlib import Path
import json

class ScrewAnnotator:
    """Interactive GUI for annotating screw keypoints in X-ray images"""
    
    def __init__(self, image_dir, output_dir, class_id=0):
        self.image_dir = Path(image_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.class_id = class_id
        
        self.keypoints = []
        self.current_image = None
        self.original_image = None
        self.current_file = None
        self.image_files = sorted(self.image_dir.glob("*.jpg")) + sorted(self.image_dir.glob("*.png"))
        self.current_idx = 0
        
        self.POINT_LABELS = [
            "Center",
            "Corner 1", "Corner 2", "Corner 3", "Corner 4",
            "Corner 5", "Corner 6", "Corner 7", "Corner 8"
        ]
    
    def click_event(self, event, x, y, flags, param):
        """Mouse callback for clicking keypoints"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.keypoints) < 9:
                self.keypoints.append((x, y))
                
                # Draw point
                color = (0, 255, 0) if len(self.keypoints) == 1 else (0, 255, 255)
                cv2.circle(self.current_image, (x, y), 8, color, -1)
                cv2.circle(self.current_image, (x, y), 8, (0, 0, 255), 2)
                
                # Add label
                label = f"{len(self.keypoints)-1}"
                cv2.putText(self.current_image, label, (x+10, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Update display
                self.display_instructions()
    
    def display_instructions(self):
        """Show current annotaton state"""
        h, w = self.current_image.shape[:2]
        
        # Add semi-transparent overlay
        overlay = self.current_image.copy()
        cv2.rectangle(overlay, (0, 0), (400, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, self.current_image, 0.7, 0, self.current_image)
        
        # Add text
        texts = [
            f"File: {self.current_file.name}",
            f"Progress: {self.current_idx + 1}/{len(self.image_files)}",
            "",
            f"Points: {len(self.keypoints)}/9",
        ]
        
        if len(self.keypoints) < 9:
            texts.append(f"Next: {self.POINT_LABELS[len(self.keypoints)]}")
        
        for i, text in enumerate(texts):
            cv2.putText(self.current_image, text, (10, 30 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Help text
        help_texts = ["S:Save", "D:Delete last", "R:Reset", "N:Next", "P:Prev", "Q:Quit"]
        for i, text in enumerate(help_texts):
            x = 10 + (i % 3) * 130
            y = h - 40 if i < 3 else h - 10
            cv2.putText(self.current_image, text, (x, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 0), 1)
        
        cv2.imshow('Screw Keypoint Annotation', self.current_image)
    
    def save_annotation(self):
        """Save annotation in YOLO format"""
        if len(self.keypoints) != 9:
            print(f"  ❌ Cannot save: need 9 points, got {len(self.keypoints)}")
            return False
        
        h, w = self.original_image.shape[:2]
        
        # Normalize to [0, 1]
        normalized = []
        for x, y in self.keypoints:
            normalized.extend([x / w, y / h])
        
        # Format: class_id + 18 normalized coords + image_dims
        line = f"{self.class_id} "
        line += " ".join(f"{coord:.6f}" for coord in normalized)
        line += f" 1.0 1.0"  # placeholder for width/height
        
        # Save
        txt_path = self.output_dir / f"{self.current_file.stem}.txt"
        with open(txt_path, 'w') as f:
            f.write(line)
        
        print(f"✓ Saved: {txt_path}")
        
        # Also save visualization
        vis_path = self.output_dir / f"{self.current_file.stem}_vis.jpg"
        cv2.imwrite(str(vis_path), self.current_image)
        
        return True
    
    def delete_last_point(self):
        """Remove last clicked point"""
        if self.keypoints:
            self.keypoints.pop()
            print(f"  Deleted last point. Remaining: {len(self.keypoints)}")
    
    def reset_points(self):
        """Clear all points and reload image"""
        self.keypoints = []
        self.current_image = self.original_image.copy()
        print(f"  Reset. Ready for new annotation.")
    
    def load_next_image(self):
        """Load next image"""
        if self.current_idx < len(self.image_files) - 1:
            self.current_idx += 1
            self.load_image()
            return True
        return False
    
    def load_prev_image(self):
        """Load previous image"""
        if self.current_idx > 0:
            self.current_idx -= 1
            self.load_image()
            return True
        return False
    
    def load_image(self):
        """Load and display image"""
        self.current_file = self.image_files[self.current_idx]
        self.original_image = cv2.imread(str(self.current_file))
        
        if self.original_image is None:
            print(f"  ❌ Failed to load: {self.current_file}")
            return False
        
        self.current_image = self.original_image.copy()
        self.keypoints = []
        
        # Check if already annotated
        txt_path = self.output_dir / f"{self.current_file.stem}.txt"
        if txt_path.exists():
            print(f"⚠️  Already annotated: {self.current_file.name}")
        
        print(f"\nLoading: {self.current_file.name}")
        return True
    
    def run(self):
        """Main annotation loop"""
        print("=" * 60)
        print("X-Ray Screw Keypoint Annotation Tool")
        print("=" * 60)
        print(f"\nFound {len(self.image_files)} images")
        
        if not self.image_files:
            print("❌ No images found!")
            return
        
        # Load first image
        if not self.load_image():
            return
        
        self.display_instructions()
        cv2.setMouseCallback('Screw Keypoint Annotation', self.click_event)
        
        while True:
            key = cv2.waitKey(0)
            
            if key == ord('s'):  # Save
                if self.save_annotation():
                    self.load_next_image()
                    self.display_instructions()
            
            elif key == ord('d'):  # Delete last point
                self.delete_last_point()
                self.reset_points()
                self.display_instructions()
            
            elif key == ord('r'):  # Reset
                self.reset_points()
                self.display_instructions()
            
            elif key == ord('n'):  # Next
                if self.load_next_image():
                    self.display_instructions()
                else:
                    print("🏁 Reached end of image list")
            
            elif key == ord('p'):  # Previous
                if self.load_prev_image():
                    self.display_instructions()
                else:
                    print("📍 Already at first image")
            
            elif key == ord('q'):  # Quit
                print("\n✅ Annotation session ended")
                break
        
        cv2.destroyAllWindows()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Annotate screw keypoints in X-ray images")
    parser.add_argument("--images", default="data/XRAY_SCREWS/m3/JPEGImages",
                       help="Directory containing images to annotate")
    parser.add_argument("--output", default="data/XRAY_SCREWS/m3/Annotations",
                       help="Directory to save annotations")
    parser.add_argument("--class-id", type=int, default=0,
                       help="Class ID for the screw type")
    
    args = parser.parse_args()
    
    annotator = ScrewAnnotator(args.images, args.output, args.class_id)
    annotator.run()

if __name__ == "__main__":
    main()
