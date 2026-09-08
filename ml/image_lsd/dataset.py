import os
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def get_transforms(split: str, img_size: int = 224):
    """
    Returns torchvision transforms.
    Augmentation is applied STRICTLY to training data.
    Validation and test sets undergo purely deterministic normalization.
    """
    if split == 'train':
        return transforms.Compose([
            transforms.RandomResizedCrop(img_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
    else:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])

class LSDImageDataset(Dataset):
    """
    PyTorch Dataset loading preprocessed images for Healthy vs Lumpy Skin Disease classification.
    """
    def __init__(self, root_dir: str, split: str, transform=None):
        self.split_dir = os.path.join(root_dir, split)
        self.transform = transform or get_transforms(split)
        self.samples = []
        
        # Standardize class mapping
        # 0: Healthy (healthycows or Normal_Skin)
        # 1: Possible Lumpy Skin Disease (lumpycows or Lumpy_Skin)
        for entry in os.listdir(self.split_dir):
            class_path = os.path.join(self.split_dir, entry)
            if not os.path.isdir(class_path):
                continue
                
            entry_lower = entry.lower()
            if 'healthy' in entry_lower or 'normal' in entry_lower:
                label = 0
            elif 'lumpy' in entry_lower:
                label = 1
            else:
                continue
                
            for fname in os.listdir(class_path):
                if any(fname.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                    fpath = os.path.join(class_path, fname)
                    self.samples.append((fpath, label))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        path, label = self.samples[idx]
        with Image.open(path) as img:
            img = img.convert('RGB')
            if self.transform:
                img = self.transform(img)
        return img, label
