#!/usr/bin/env python3
"""
X-Ray Screw Detection - Easy Command-Line Interface
Simplified interface for managing the entire project workflow
"""

import argparse
import sys
import json
from pathlib import Path
import subprocess
import shutil


class ProjectManager:
    """Manage X-ray screw detection project tasks"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.data_root = self.project_root / 'data' / 'XRAY_SCREWS'
        self.runs_dir = self.project_root / 'runs' / 'train'
    
    def generate_data(self, num_images: int = 50):
        """Generate synthetic dataset"""
        print("\n" + "="*60)
        print(f"📦 Generating synthetic data ({num_images} images per screw type)")
        print(f"   Total: {num_images * 4} images")
        print("="*60)
        
        cmd = [
            sys.executable,
            str(self.project_root / 'data_curation' / 'generate_synthetic_data.py'),
            '--num-images', str(num_images)
        ]
        
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print("\n✅ Synthetic data generated successfully!")
        else:
            print("\n❌ Error generating synthetic data")
            return False
        
        return True
    
    def validate_data(self, screw_type: str = 'm3', visualize: bool = False):
        """Validate dataset"""
        dataset_dir = self.data_root / screw_type
        
        if not dataset_dir.exists():
            print(f"❌ Dataset not found: {dataset_dir}")
            return False
        
        print("\n" + "="*60)
        print(f"✍️  Validating {screw_type.upper()} dataset")
        print("="*60)
        
        cmd = [
            sys.executable,
            str(self.project_root / 'data_curation' / 'validate_dataset.py'),
            '--dataset', str(dataset_dir)
        ]
        
        if visualize:
            cmd.append('--visualize')
        
        result = subprocess.run(cmd)
        return result.returncode == 0
    
    def train(self, screw_type: str = 'm3', epochs: int = 20, batch: int = 32):
        """Train model for a screw type"""
        dataset_dir = self.data_root / screw_type
        
        if not dataset_dir.exists():
            print(f"❌ Dataset not found: {dataset_dir}")
            return False
        
        print("\n" + "="*60)
        print(f"🚀 Training model for {screw_type.upper()}")
        print(f"   Epochs: {epochs}, Batch: {batch}")
        print("="*60)
        
        cmd = [
            sys.executable,
            str(self.project_root / 'train.py'),
            '--data-dir', str(dataset_dir),
            '--epochs', str(epochs),
            '--batch', str(batch),
            '--img-size', '640'
        ]
        
        result = subprocess.run(cmd)
        if result.returncode == 0:
            self._show_model_path(screw_type)
        return result.returncode == 0
    
    def train_all(self, epochs: int = 20, batch: int = 32):
        """Train models for all screw types"""
        screw_types = ['m3', 'm4', 'm5', 'm6']
        failed = []
        
        for screw_type in screw_types:
            print(f"\n{'='*60}")
            print(f"Training {screw_type.upper()}...")
            if not self.train(screw_type, epochs, batch):
                failed.append(screw_type)
        
        print(f"\n{'='*60}")
        if failed:
            print(f"⚠️  Failed to train: {', '.join(failed)}")
        else:
            print("✅ All models trained successfully!")
        
        return len(failed) == 0
    
    def list_experiments(self):
        """List all trained models"""
        if not self.runs_dir.exists():
            print("No experiments found. Train a model first!")
            return
        
        print("\n" + "="*60)
        print("📊 Available Trained Models")
        print("="*60)
        
        exp_dirs = sorted([d for d in self.runs_dir.iterdir() if d.is_dir()])
        
        if not exp_dirs:
            print("No experiments found.")
            return
        
        for exp_dir in exp_dirs:
            weights_dir = exp_dir / 'weights'
            if weights_dir.exists():
                # Count model files
                best_model = weights_dir / 'best.pt'
                last_model = weights_dir / 'last.pt'
                
                exp_num = exp_dir.name
                print(f"\n{exp_num}/")
                
                if best_model.exists():
                    size = best_model.stat().st_size / (1024 * 1024)
                    print(f"  ✓ best.pt ({size:.2f} MB)")
                
                if last_model.exists():
                    size = last_model.stat().st_size / (1024 * 1024)
                    print(f"  ✓ last.pt ({size:.2f} MB)")
    
    def _show_model_path(self, screw_type: str = None):
        """Show path to trained model"""
        exp_dirs = sorted([d for d in self.runs_dir.iterdir() if d.is_dir()])
        if exp_dirs:
            latest = exp_dirs[-1]
            best_model = latest / 'weights' / 'best.pt'
            
            if best_model.exists():
                print(f"\n✅ Model saved: {best_model}")
                print(f"   Use for inference: python detect.py --weights {best_model}")
    
    def camera_config(self):
        """Show/edit camera calibration"""
        camera_file = self.project_root / 'configs' / 'screws' / 'screw_camera.json'
        
        if not camera_file.exists():
            print("❌ Camera config not found!")
            return
        
        print("\n" + "="*60)
        print("📷 Camera Calibration Parameters")
        print("="*60)
        
        with open(camera_file, 'r') as f:
            config = json.load(f)
        
        for key, value in config.items():
            print(f"{key:15s}: {value}")
    
    def setup_instructions(self):
        """Show setup instructions"""
        print("\n" + "="*60)
        print("🚀 X-Ray Screw Detection - Quick Start")
        print("="*60)
        
        print("""
AVAILABLE COMMANDS:

  python main.py generate [--num-images 50]
    → Generate synthetic dataset (default: 50 per type)

  python main.py validate [--type m3] [--visualize]
    → Validate dataset quality (optional: visualize annotations)

  python main.py train [--type m3] [--epochs 20] [--batch 32]
    → Train model for specific screw type

  python main.py train-all [--epochs 20] [--batch 32]
    → Train models for all screw types (M3, M4, M5, M6)

  python main.py list
    → List all trained models

  python main.py camera
    → Show camera calibration parameters

  python main.py help
    → Show this help message


QUICK START WORKFLOW:

  1. Generate synthetic data:
     python main.py generate

  2. Validate dataset:
     python main.py validate

  3. Train model:
     python main.py train --epochs 50

  4. View results:
     python main.py list

  5. Use trained model (later):
     python detect.py --weights runs/train/exp1/weights/best.pt \\
       --source data/XRAY_SCREWS/m3/JPEGImages


ADVANCED USAGE:

  Train M4 with custom settings:
    python main.py train --type m4 --epochs 100 --batch 16

  Train all screw types:
    python main.py train-all --epochs 50

  Update camera calibration:
    Edit: configs/screws/screw_camera.json
        """)
    
    def status(self):
        """Show project status"""
        print("\n" + "="*60)
        print("📊 Project Status")
        print("="*60)
        
        # Check datasets
        print("\n✓ Datasets:")
        for st in ['m3', 'm4', 'm5', 'm6']:
            st_dir = self.data_root / st
            if st_dir.exists():
                img_count = len(list((st_dir / 'JPEGImages').glob('*.jpg')))
                print(f"  {st.upper()}: {img_count} images")
        
        # Check models
        print("\n✓ Trained Models:")
        if self.runs_dir.exists():
            exp_dirs = sorted([d for d in self.runs_dir.iterdir() if d.is_dir()])
            if exp_dirs:
                for exp_dir in exp_dirs[-3:]:  # Show last 3
                    best = exp_dir / 'weights' / 'best.pt'
                    if best.exists():
                        print(f"  {exp_dir.name}: best.pt ✓")
            else:
                print("  No trained models yet")
        else:
            print("  No trained models yet")
        
        # Camera config
        print("\n✓ Camera Configuration:")
        camera_file = self.project_root / 'configs' / 'screws' / 'screw_camera.json'
        if camera_file.exists():
            with open(camera_file, 'r') as f:
                config = json.load(f)
                print(f"  fx={config['fx']}, fy={config['fy']}")
                print(f"  u0={config['u0']}, v0={config['v0']}")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='X-Ray Screw Detection Project Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py generate              # Generate synthetic data
  python main.py validate              # Validate dataset
  python main.py train --epochs 50     # Train model
  python main.py list                  # List trained models
  python main.py help                  # Show detailed help
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate synthetic dataset')
    generate_parser.add_argument('--num-images', type=int, default=50,
                               help='Number of images per screw type (default: 50)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate dataset')
    validate_parser.add_argument('--type', default='m3', 
                                choices=['m3', 'm4', 'm5', 'm6'],
                                help='Screw type to validate')
    validate_parser.add_argument('--visualize', action='store_true',
                                help='Visualize annotations')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train model')
    train_parser.add_argument('--type', default='m3',
                             choices=['m3', 'm4', 'm5', 'm6'],
                             help='Screw type to train')
    train_parser.add_argument('--epochs', type=int, default=20,
                             help='Number of epochs')
    train_parser.add_argument('--batch', type=int, default=32,
                             help='Batch size')
    
    # Train all command
    train_all_parser = subparsers.add_parser('train-all', help='Train all screw types')
    train_all_parser.add_argument('--epochs', type=int, default=20,
                                 help='Number of epochs')
    train_all_parser.add_argument('--batch', type=int, default=32,
                                 help='Batch size')
    
    # List command
    subparsers.add_parser('list', help='List trained models')
    
    # Camera command
    subparsers.add_parser('camera', help='Show camera configuration')
    
    # Status command
    subparsers.add_parser('status', help='Show project status')
    
    # Help command
    subparsers.add_parser('help', help='Show detailed help')
    
    args = parser.parse_args()
    
    manager = ProjectManager()
    
    # Handle commands
    if args.command == 'generate':
        manager.generate_data(args.num_images)
    
    elif args.command == 'validate':
        manager.validate_data(args.type, args.visualize)
    
    elif args.command == 'train':
        manager.train(args.type, args.epochs, args.batch)
    
    elif args.command == 'train-all':
        manager.train_all(args.epochs, args.batch)
    
    elif args.command == 'list':
        manager.list_experiments()
    
    elif args.command == 'camera':
        manager.camera_config()
    
    elif args.command == 'status':
        manager.status()
    
    elif args.command == 'help':
        manager.setup_instructions()
    
    else:
        # Default: show help
        manager.setup_instructions()
        parser.print_help()


if __name__ == '__main__':
    main()
