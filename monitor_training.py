#!/usr/bin/env python3
"""
Monitor training progress
Shows real-time updates of training metrics
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

def monitor_training(exp_dir='runs/train/exp3'):
    """Monitor training directory for progress"""
    
    exp_path = Path(exp_dir)
    weights_dir = exp_path / 'weights'
    
    print(f"\n{'='*60}")
    print(f"📊 Training Monitor")
    print(f"{'='*60}\n")
    print(f"Exp directory: {exp_dir}")
    print(f"Monitor started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    last_check = 0
    
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ", end='')
        
        # Check for model files
        best_model = weights_dir / 'best.pt'
        last_model = weights_dir / 'last.pt'
        
        if best_model.exists():
            size_mb = best_model.stat().st_size / (1024 * 1024)
            print(f"✓ best.pt ({size_mb:.2f}MB)", end='')
        
        if last_model.exists():
            size_mb = last_model.stat().st_size / (1024 * 1024)
            print(f" | ✓ last.pt ({size_mb:.2f}MB)", end='')
        
        if best_model.exists() or last_model.exists():
            print("\n✅ Training in progress - models being saved")
        else:
            print("⏳ Waiting for training to start saving models...")
        
        # Check for results file
        results_file = exp_path / 'results.json'
        if results_file.exists():
            try:
                with open(results_file) as f:
                    results = json.load(f)
                    if isinstance(results, list) and len(results) > 0:
                        latest = results[-1]
                        print(f"\n📈 Latest Epoch:")
                        for key, val in latest.items():
                            if isinstance(val, float):
                                print(f"   {key}: {val:.4f}")
                            else:
                                print(f"   {key}: {val}")
            except:
                pass
        
        # Wait before checking again
        time.sleep(5)
        
        print()

if __name__ == '__main__':
    try:
        monitor_training()
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped")
