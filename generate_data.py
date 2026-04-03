#!/usr/bin/env python3
"""
Quick Data Generation Script for X-Ray Screw Detection
Simplified interface for generating synthetic datasets with preset configurations
"""

import argparse
import sys
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic X-ray screw dataset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
QUICK PRESETS:
  python generate_data.py quick      Generate 50 images/type (200 total) - Fast test
  python generate_data.py small      Generate 100 images/type (400 total)
  python generate_data.py medium     Generate 300 images/type (1,200 total) - Recommended
  python generate_data.py large      Generate 500 images/type (2,000 total)
  python generate_data.py extra      Generate 1,000 images/type (4,000 total)

CUSTOM:
  python generate_data.py --num-images 250

EXAMPLES:
  python generate_data.py medium          # Standard dataset (1,200 images)
  python generate_data.py large --validate # Generate and validate afterward
  python generate_data.py --num-images 750 # Custom size
        """
    )
    
    subparsers = parser.add_subparsers(dest='preset', help='Preset configuration')
    
    # Presets
    subparsers.add_parser('quick', help='Fast test (50 images/type)')
    subparsers.add_parser('small', help='Small dataset (100 images/type)')
    subparsers.add_parser('medium', help='Medium dataset (300 images/type) [Recommended]')
    subparsers.add_parser('large', help='Large dataset (500 images/type)')
    subparsers.add_parser('extra', help='Extra large (1,000 images/type)')
    
    # Custom option
    custom_parser = subparsers.add_parser('custom', help='Custom number of images')
    
    # Global options
    parser.add_argument('--num-images', type=int, dest='num_images_custom',
                       help='Custom number of images per screw type')
    parser.add_argument('--validate', action='store_true',
                       help='Validate dataset after generation')
    parser.add_argument('--screw-type', default='m3',
                       choices=['m3', 'm4', 'm5', 'm6'],
                       help='Screw type to validate (default: m3)')
    
    args = parser.parse_args()
    
    # Determine number of images
    preset_map = {
        'quick': 50,
        'small': 100,
        'medium': 300,
        'large': 500,
        'extra': 1000,
        'custom': args.num_images_custom
    }
    
    if args.preset:
        num_images = preset_map.get(args.preset)
    elif args.num_images_custom:
        num_images = args.num_images_custom
    else:
        parser.print_help()
        return
    
    if not num_images:
        print("❌ Invalid number of images")
        return
    
    # Print info
    total = num_images * 4
    print("\n" + "="*60)
    print("📦 X-Ray Screw Detection - Data Generator")
    print("="*60)
    print(f"Images per screw type: {num_images}")
    print(f"Total images: {total}")
    print(f"Screw types: M3, M4, M5, M6")
    print("="*60 + "\n")
    
    # Generate data
    print("🚀 Starting generation...")
    project_root = Path(__file__).parent
    
    cmd = [
        sys.executable,
        str(project_root / 'data_curation' / 'generate_synthetic_data.py'),
        '--num-images', str(num_images)
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n❌ Generation failed!")
        sys.exit(1)
    
    print("\n✅ Generation completed successfully!")
    
    # Optional: Validate
    if args.validate:
        print(f"\n🔍 Validating {args.screw_type.upper()} dataset...")
        validate_cmd = [
            sys.executable,
            str(project_root / 'data_curation' / 'validate_dataset.py'),
            '--dataset', str(project_root / 'data' / 'XRAY_SCREWS' / args.screw_type)
        ]
        subprocess.run(validate_cmd)
    
    print("\n📊 Dataset ready!")
    print(f"   Location: data/XRAY_SCREWS/")
    print(f"   Size: {total} images")
    print(f"\n💡 Next step: python main.py train")


if __name__ == '__main__':
    main()
