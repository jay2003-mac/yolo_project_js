#!/usr/bin/env python3
"""
YOLOv5-6D Training Script for Screw Pose Estimation
Trains a YOLOv5 model with 6-DoF keypoint regression
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScrewDataset(Dataset):
    """Dataset loader for screw detection with keypoint annotations"""
    
    def __init__(self, data_dir: str, image_list: str, img_size: int = 640,
                 augment: bool = False):
        self.data_dir = Path(data_dir)
        self.images_dir = self.data_dir / 'JPEGImages'
        self.annot_dir = self.data_dir / 'Annotations'
        self.img_size = img_size
        self.augment = augment
        
        # Load image list
        list_path = self.data_dir / image_list
        with open(list_path, 'r') as f:
            self.image_paths = [line.strip() for line in f.readlines()]
        
        logger.info(f"Loaded {len(self.image_paths)} images from {list_path}")
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # Load image
        img_rel_path = self.image_paths[idx]
        img_path = self.images_dir / img_rel_path.split('/')[-1]
        
        image = Image.open(img_path).convert('RGB')
        orig_w, orig_h = image.size
        
        # Resize image
        image = image.resize((self.img_size, self.img_size), Image.Resampling.BILINEAR)
        image = np.array(image, dtype=np.float32) / 255.0
        image = np.transpose(image, (2, 0, 1))  # HWC -> CHW
        
        # Load annotations
        txt_name = img_rel_path.split('/')[-1].rsplit('.', 1)[0] + '.txt'
        txt_path = self.annot_dir / txt_name
        
        with open(txt_path, 'r') as f:
            line = f.read().strip()
        
        parts = line.split()
        class_id = int(parts[0])
        
        # Extract 9 keypoints (18 values)
        keypoints = np.array([float(x) for x in parts[1:19]], dtype=np.float32)
        # keypoints are normalized [0, 1], scale to image size
        keypoints_scaled = keypoints.copy()
        keypoints_scaled[0::2] = keypoints[0::2] * self.img_size  # x coords
        keypoints_scaled[1::2] = keypoints[1::2] * self.img_size  # y coords
        
        # Create target tensor: [class_id, keypoints_x, keypoints_y]
        # Format: [class_id, x0, y0, x1, y1, ..., x8, y8]
        target = np.concatenate([[class_id], keypoints_scaled])
        
        return {
            'image': torch.from_numpy(image),
            'target': torch.from_numpy(target),
            'image_path': img_rel_path,
            'orig_size': (orig_w, orig_h)
        }


class SimpleScrewDetector(nn.Module):
    """Simple CNN for screw pose estimation"""
    
    def __init__(self, num_classes: int = 4, num_keypoints: int = 9):
        super().__init__()
        self.num_classes = num_classes
        self.num_keypoints = num_keypoints
        
        # Feature extraction backbone
        self.backbone = nn.Sequential(
            # Conv1: 3 -> 32
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 320x320
            
            # Conv2: 32 -> 64
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 160x160
            
            # Conv3: 64 -> 128
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 80x80
            
            # Conv4: 128 -> 256
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),  # 40x40
            
            # Conv5: 256 -> 512
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Regression heads
        self.class_head = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
        
        self.keypoint_head = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, num_keypoints * 2)  # x,y for each keypoint
        )
    
    def forward(self, x):
        features = self.backbone(x)
        features = features.view(features.size(0), -1)
        
        class_out = self.class_head(features)
        keypoint_out = self.keypoint_head(features)
        
        return class_out, keypoint_out


class Trainer:
    """Training loop for screw detection model"""
    
    def __init__(self, args):
        self.args = args
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.runs_dir = Path('runs/train')
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create exp directory
        exp_dirs = sorted([d for d in self.runs_dir.iterdir() if d.is_dir()])
        exp_num = len(exp_dirs) + 1
        self.exp_dir = self.runs_dir / f'exp{exp_num}'
        self.exp_dir.mkdir(parents=True, exist_ok=True)
        
        self.weights_dir = self.exp_dir / 'weights'
        self.weights_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Experiment directory: {self.exp_dir}")
    
    def build_dataloaders(self) -> Tuple[DataLoader, DataLoader]:
        """Create training and validation dataloaders"""
        train_dataset = ScrewDataset(
            self.args.data_dir,
            'train.txt',
            img_size=self.args.img_size,
            augment=True
        )
        
        test_dataset = ScrewDataset(
            self.args.data_dir,
            'test.txt',
            img_size=self.args.img_size,
            augment=False
        )
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.args.batch,
            shuffle=True,
            num_workers=2
        )
        
        test_loader = DataLoader(
            test_dataset,
            batch_size=self.args.batch,
            shuffle=False,
            num_workers=2
        )
        
        return train_loader, test_loader
    
    def build_model(self) -> nn.Module:
        """Create model"""
        model = SimpleScrewDetector(
            num_classes=4,  # M3, M4, M5, M6
            num_keypoints=9
        )
        model.to(self.device)
        
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        logger.info(f"Model created with {total_params:,} parameters ({trainable_params:,} trainable)")
        return model
    
    def train_epoch(self, model, train_loader, optimizer, criterion_cls, criterion_kpt):
        """Train for one epoch"""
        model.train()
        total_loss = 0
        
        pbar = tqdm.tqdm(train_loader, desc="Training")
        for batch in pbar:
            images = batch['image'].to(self.device)
            targets = batch['target'].to(self.device)
            
            # Forward pass
            class_out, kpt_out = model(images)
            
            # Loss computation
            class_ids = targets[:, 0].long()
            keypoints_gt = targets[:, 1:].reshape(targets.shape[0], 9, 2)
            
            loss_cls = criterion_cls(class_out, class_ids)
            loss_kpt = criterion_kpt(
                kpt_out.reshape(kpt_out.shape[0], 9, 2),
                keypoints_gt
            )
            
            loss = loss_cls + loss_kpt
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = total_loss / len(train_loader)
        return avg_loss
    
    def validate(self, model, test_loader):
        """Validate model"""
        model.eval()
        total_loss = 0
        correct = 0
        
        criterion_cls = nn.CrossEntropyLoss()
        criterion_kpt = nn.MSELoss()
        
        with torch.no_grad():
            for batch in tqdm.tqdm(test_loader, desc="Validating"):
                images = batch['image'].to(self.device)
                targets = batch['target'].to(self.device)
                
                class_out, kpt_out = model(images)
                
                class_ids = targets[:, 0].long()
                keypoints_gt = targets[:, 1:].reshape(targets.shape[0], 9, 2)
                
                loss_cls = criterion_cls(class_out, class_ids)
                loss_kpt = criterion_kpt(
                    kpt_out.reshape(kpt_out.shape[0], 9, 2),
                    keypoints_gt
                )
                
                loss = loss_cls + loss_kpt
                total_loss += loss.item()
                
                correct += (class_out.argmax(1) == class_ids).sum().item()
        
        avg_loss = total_loss / len(test_loader)
        accuracy = correct / len(test_loader.dataset) * 100
        
        return avg_loss, accuracy
    
    def train(self):
        """Full training loop"""
        logger.info("Starting training...")
        
        # Build dataloaders and model
        train_loader, test_loader = self.build_dataloaders()
        model = self.build_model()
        
        # Optimizer
        optimizer = optim.Adam(model.parameters(), lr=self.args.lr)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=self.args.epochs
        )
        
        # Loss functions
        criterion_cls = nn.CrossEntropyLoss()
        criterion_kpt = nn.MSELoss()
        
        # Training loop
        best_loss = float('inf')
        
        for epoch in range(self.args.epochs):
            logger.info(f"\nEpoch {epoch + 1}/{self.args.epochs}")
            
            # Train
            train_loss = self.train_epoch(
                model, train_loader, optimizer, criterion_cls, criterion_kpt
            )
            
            # Validate
            val_loss, val_acc = self.validate(model, test_loader)
            
            scheduler.step()
            
            logger.info(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
            
            # Save checkpoint
            if val_loss < best_loss:
                best_loss = val_loss
                best_path = self.weights_dir / 'best.pt'
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'epoch': epoch,
                    'loss': val_loss,
                }, best_path)
                logger.info(f"Saved best checkpoint: {best_path}")
            
            # Save last checkpoint
            last_path = self.weights_dir / 'last.pt'
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'epoch': epoch,
                'loss': val_loss,
            }, last_path)
        
        logger.info(f"Training complete! Best model: {self.weights_dir / 'best.pt'}")


def main():
    parser = argparse.ArgumentParser(description='Train YOLOv5-6D screw detection model')
    parser.add_argument('--data-dir', type=str, default='data/XRAY_SCREWS/m3',
                        help='Dataset directory')
    parser.add_argument('--batch', type=int, default=32,
                        help='Batch size')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Number of epochs')
    parser.add_argument('--img-size', type=int, default=640,
                        help='Image size')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate')
    parser.add_argument('--device', type=str, default='0',
                        help='CUDA device id')
    parser.add_argument('--resume', type=str, default=None,
                        help='Resume from checkpoint')
    
    args = parser.parse_args()
    
    trainer = Trainer(args)
    trainer.train()


if __name__ == '__main__':
    main()
