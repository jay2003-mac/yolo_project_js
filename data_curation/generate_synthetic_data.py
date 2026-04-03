#!/usr/bin/env python3
"""
Synthetic X-ray Screw Dataset Generator
Generates synthetic X-ray images, 3D screw models, and keypoint annotations
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
import cv2
from PIL import Image, ImageDraw
import random
from typing import Dict, Tuple, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ScrewGenerator:
    """Generate 3D screw models and keypoints"""
    
    # ISO standard screw dimensions (in mm)
    SCREW_SPECS = {
        'm3': {
            'diameter': 3.0,
            'head_diameter': 5.5,
            'head_height': 2.0,
            'length': 16.0,
        },
        'm4': {
            'diameter': 4.0,
            'head_diameter': 7.0,
            'head_height': 2.7,
            'length': 20.0,
        },
        'm5': {
            'diameter': 5.0,
            'head_diameter': 8.5,
            'head_height': 3.5,
            'length': 25.0,
        },
        'm6': {
            'diameter': 6.0,
            'head_diameter': 10.0,
            'head_height': 4.0,
            'length': 30.0,
        },
    }
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_ply_model(self, screw_type: str, filename: str = None):
        """Generate a 3D screw model in PLY format"""
        specs = self.SCREW_SPECS[screw_type]
        
        # Create vertices for a simplified screw
        vertices = []
        
        # Head (cylinder)
        head_r = specs['head_diameter'] / 2
        head_h = specs['head_height']
        n_sides = 20
        for i in range(n_sides):
            angle = 2 * np.pi * i / n_sides
            x = head_r * np.cos(angle)
            y = head_r * np.sin(angle)
            # Top of head
            vertices.append([x, y, head_h])
            # Bottom of head
            vertices.append([x, y, 0])
        
        # Body (tapered cylinder)
        body_r = specs['diameter'] / 2
        body_l = specs['length']
        for i in range(n_sides):
            angle = 2 * np.pi * i / n_sides
            # Taper from head to body
            x = body_r * np.cos(angle)
            y = body_r * np.sin(angle)
            vertices.append([x, y, -body_l])
        
        vertices = np.array(vertices, dtype=np.float32)
        
        # Create faces (simple triangulation)
        faces = []
        # Head faces
        for i in range(n_sides - 1):
            v0 = i * 2
            v1 = (i + 1) * 2
            faces.append([3, v0, v1, v0 + 1])
            faces.append([3, v1, v1 + 1, v0 + 1])
        
        # Save as PLY
        if filename is None:
            filename = f"{screw_type}.ply"
        ply_path = self.output_dir / filename
        
        self._write_ply(ply_path, vertices, faces)
        print(f"✓ Generated 3D model: {ply_path}")
        return str(ply_path)
    
    @staticmethod
    def _write_ply(filepath: Path, vertices: np.ndarray, faces: List):
        """Write vertices and faces to PLY file"""
        with open(filepath, 'w') as f:
            # Header
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(vertices)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write(f"element face {len(faces)}\n")
            f.write("property list uchar int vertex_indices\n")
            f.write("end_header\n")
            
            # Vertices
            for v in vertices:
                f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            
            # Faces
            for face in faces:
                f.write(f"{' '.join(map(str, face))}\n")


class ImageGenerator:
    """Generate synthetic X-ray-like images"""
    
    def __init__(self, image_size: Tuple = (640, 480)):
        self.width, self.height = image_size
        self.camera_matrix = np.array([
            [1200, 0, self.width / 2],
            [0, 1200, self.height / 2],
            [0, 0, 1]
        ], dtype=np.float32)
    
    def render_screw(self, screw_type: str, 
                     position: np.ndarray = None,
                     rotation: np.ndarray = None) -> Tuple[Image.Image, List]:
        """
        Render a synthetic screw image
        
        Returns:
            (image, keypoints) - PIL Image and list of 9 2D keypoints
        """
        if position is None:
            position = np.array([0, 0, 150], dtype=np.float32)
        
        if rotation is None:
            # Random rotation (Euler angles in radians)
            rotation = np.array([
                np.random.uniform(-np.pi/4, np.pi/4),
                np.random.uniform(-np.pi/4, np.pi/4),
                np.random.uniform(0, 2*np.pi)
            ], dtype=np.float32)
        
        # Create base image (X-ray style - white background)
        img = Image.new('RGB', (self.width, self.height), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)
        
        # Generate screw 3D points (simplified geometry)
        specs = ScrewGenerator.SCREW_SPECS[screw_type]
        
        # Create 9 keypoints: center + 8 box corners
        keypoints_3d = self._generate_keypoints_3d(specs)
        
        # Apply rotation and translation
        keypoints_3d = self._apply_transform(keypoints_3d, rotation, position)
        
        # Project to 2D using camera matrix
        keypoints_2d = self._project_to_2d(keypoints_3d)
        
        # Draw screw outline
        self._draw_screw_outline(draw, keypoints_2d, specs)
        
        # Add noise (realistic X-ray artifacts)
        img_array = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, 5, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        
        return img, keypoints_2d
    
    @staticmethod
    def _generate_keypoints_3d(specs: Dict) -> np.ndarray:
        """Generate 3D coordinates for 9 keypoints"""
        h_d = specs['head_diameter'] / 2
        b_r = specs['diameter'] / 2
        h_h = specs['head_height']
        length = specs['length']
        
        keypoints = np.array([
            [0, 0, 0],          # 0: center
            [h_d, 0, h_h],      # 1: head corner
            [h_d, 0, -length],  # 2: body corner
            [-h_d, 0, h_h],     # 3: head corner
            [-h_d, 0, -length], # 4: body corner
            [0, h_d, h_h],      # 5: head corner
            [0, h_d, -length],  # 6: body corner
            [0, -h_d, h_h],     # 7: head corner
            [0, -h_d, -length], # 8: body corner
        ], dtype=np.float32)
        
        return keypoints
    
    @staticmethod
    def _apply_transform(points: np.ndarray, rotation: np.ndarray, 
                        translation: np.ndarray) -> np.ndarray:
        """Apply 3D rotation and translation"""
        # Rotation matrix from Euler angles (ZYX convention)
        rx, ry, rz = rotation
        
        # Rx
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx), np.cos(rx)]
        ])
        
        # Ry
        Ry = np.array([
            [np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])
        
        # Rz
        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz), np.cos(rz), 0],
            [0, 0, 1]
        ])
        
        # Combined rotation
        R = Rz @ Ry @ Rx
        
        # Apply transformation
        transformed = (R @ points.T).T + translation
        return transformed
    
    def _project_to_2d(self, points_3d: np.ndarray) -> List[Tuple]:
        """Project 3D points to 2D image plane"""
        points_2d = []
        
        for point in points_3d:
            # Camera projection
            p_img = self.camera_matrix @ point
            x = int(p_img[0] / p_img[2])
            y = int(p_img[1] / p_img[2])
            
            # Clamp to image bounds
            x = max(0, min(x, self.width - 1))
            y = max(0, min(y, self.height - 1))
            
            points_2d.append((x, y))
        
        return points_2d
    
    @staticmethod
    def _draw_screw_outline(draw: ImageDraw.ImageDraw, 
                           keypoints: List[Tuple], specs: Dict):
        """Draw screw outline on image"""
        if len(keypoints) < 2:
            return
        
        # Draw circle at center
        center = keypoints[0]
        radius = int(specs['head_diameter'] / 2 * 2)
        draw.ellipse(
            [center[0] - radius, center[1] - radius,
             center[0] + radius, center[1] + radius],
            outline=(50, 50, 50), width=2
        )
        
        # Draw lines connecting corners
        for i in range(1, len(keypoints)):
            p1 = keypoints[i]
            draw.point(p1, fill=(50, 50, 50))


class DatasetGenerator:
    """Orchestrate full dataset generation"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.data_root = self.project_root / 'data' / 'XRAY_SCREWS'
    
    def generate_dataset(self, num_images_per_screw: int = 50):
        """Generate complete synthetic dataset"""
        print("\n" + "="*60)
        print("GENERATING SYNTHETIC DATASET")
        print("="*60)
        
        screw_types = ['m3', 'm4', 'm5', 'm6']
        class_id_map = {st: i for i, st in enumerate(screw_types)}
        
        for screw_type in screw_types:
            print(f"\n📦 Generating {screw_type.upper()} dataset...")
            self._generate_screw_dataset(
                screw_type, 
                class_id_map[screw_type],
                num_images_per_screw
            )
        
        # Create camera config
        self._create_camera_config()
        
        print("\n" + "="*60)
        print("✅ SYNTHETIC DATASET GENERATION COMPLETE!")
        print("="*60)
    
    def _generate_screw_dataset(self, screw_type: str, class_id: int, 
                               num_images: int):
        """Generate dataset for one screw type"""
        screw_dir = self.data_root / screw_type
        images_dir = screw_dir / 'JPEGImages'
        annotations_dir = screw_dir / 'Annotations'
        
        images_dir.mkdir(parents=True, exist_ok=True)
        annotations_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate 3D model
        screw_gen = ScrewGenerator(str(screw_dir))
        screw_gen.generate_ply_model(screw_type)
        
        # Generate images
        img_gen = ImageGenerator()
        image_names = []
        
        for i in range(num_images):
            # Random pose
            position = np.array([
                np.random.uniform(-10, 10),
                np.random.uniform(-10, 10),
                np.random.uniform(100, 200)
            ], dtype=np.float32)
            
            rotation = np.array([
                np.random.uniform(-np.pi/3, np.pi/3),
                np.random.uniform(-np.pi/3, np.pi/3),
                np.random.uniform(0, 2*np.pi)
            ], dtype=np.float32)
            
            # Render image
            img, keypoints_2d = img_gen.render_screw(screw_type, position, rotation)
            
            # Save image
            img_name = f"{screw_type}_{i:04d}.jpg"
            img_path = images_dir / img_name
            img.save(str(img_path), 'JPEG', quality=95)
            image_names.append(img_name)
            
            # Create annotation
            self._create_annotation(
                keypoints_2d, class_id, annotations_dir, img_name
            )
            
            if (i + 1) % 10 == 0:
                print(f"  Generated {i + 1}/{num_images} images")
        
        # Create train/test split
        self._create_train_test_splits(
            screw_dir, image_names, test_ratio=0.2
        )
        
        print(f"✓ {screw_type}: {num_images} images generated")
    
    @staticmethod
    def _create_annotation(keypoints_2d: List[Tuple], class_id: int,
                          annotations_dir: Path, img_name: str):
        """Create YOLO format annotation file"""
        # Convert image filename to txt
        txt_name = img_name.rsplit('.', 1)[0] + '.txt'
        txt_path = annotations_dir / txt_name
        
        # Normalize keypoints to [0, 1]
        # Assuming image size 640x480
        keypoints_norm = []
        for x, y in keypoints_2d:
            keypoints_norm.append(x / 640.0)
            keypoints_norm.append(y / 480.0)
        
        # Write YOLO format: class_id x0 y0 x1 y1 ... x8 y8 w h
        with open(txt_path, 'w') as f:
            annotation = f"{class_id} "
            annotation += " ".join(f"{k:.6f}" for k in keypoints_norm)
            annotation += " 1.0 1.0\n"  # width and height factors
            f.write(annotation)
    
    @staticmethod
    def _create_train_test_splits(screw_dir: Path, image_names: List[str],
                                  test_ratio: float = 0.2):
        """Create train.txt and test.txt files"""
        # Shuffle and split
        random.shuffle(image_names)
        split_idx = int(len(image_names) * (1 - test_ratio))
        
        train_names = image_names[:split_idx]
        test_names = image_names[split_idx:]
        
        # Save train.txt (with relative paths)
        train_path = screw_dir / 'train.txt'
        with open(train_path, 'w') as f:
            for name in train_names:
                f.write(f"JPEGImages/{name}\n")
        
        # Save test.txt
        test_path = screw_dir / 'test.txt'
        with open(test_path, 'w') as f:
            for name in test_names:
                f.write(f"JPEGImages/{name}\n")
        
        print(f"  Train/test split: {len(train_names)} train, {len(test_names)} test")
    
    def _create_camera_config(self):
        """Create camera calibration config file"""
        camera_config = {
            "fx": 1200.0,
            "fy": 1200.0,
            "u0": 320.0,
            "v0": 240.0,
            "resolution": [640, 480],
            "source": "synthetic_data"
        }
        
        config_path = self.project_root / 'configs' / 'screws' / 'screw_camera.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(camera_config, f, indent=2)
        
        print(f"✓ Created camera config: {config_path}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    print("\n🔧 Synthetic X-ray Screw Dataset Generator")
    print(f"📁 Project root: {project_root}")
    
    generator = DatasetGenerator(str(project_root))
    generator.generate_dataset(num_images_per_screw=50)
    
    print("\n📝 Next steps:")
    print("1. Run: python data_curation/validate_dataset.py --dataset data/XRAY_SCREWS/m3")
    print("2. Update hyperparameters in: configs/hyp.single.yaml")
    print("3. Train model: python train.py --data configs/screws/m3.yaml --batch 32")


if __name__ == '__main__':
    main()
