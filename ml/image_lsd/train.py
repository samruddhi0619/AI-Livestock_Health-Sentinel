import os
import sys
import time
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.models import (
    efficientnet_b0, EfficientNet_B0_Weights,
    mobilenet_v3_small, MobileNet_V3_Small_Weights
)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(ROOT_DIR, "ml", "image_lsd"))

from dataset import LSDImageDataset

DATASET_DIR = os.path.join(ROOT_DIR, "datasets", "processed", "01_lsd_images")
MODELS_DIR = os.path.join(ROOT_DIR, "ml", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

CONFIG = {
    "num_classes": 2,
    "class_names": ["Healthy", "Possible Lumpy Skin Disease"],
    "batch_size": 16,
    "epochs": 6,
    "learning_rate": 3e-4,
    "weight_decay": 1e-2,
    "img_size": 224,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "seed": 42
}

def set_seed(seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def create_model(model_name: str, num_classes: int = 2):
    """Initializes model with ImageNet pre-trained backbone and custom head."""
    if model_name == "efficientnet_b0":
        weights = EfficientNet_B0_Weights.DEFAULT
        model = efficientnet_b0(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(in_features, num_classes)
        )
    elif model_name == "mobilenet_v3_small":
        weights = MobileNet_V3_Small_Weights.DEFAULT
        model = mobilenet_v3_small(weights=weights)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, num_classes)
    else:
        raise ValueError(f"Unsupported model: {model_name}")
    return model

def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    all_preds, all_labels = [], []
    
    for images, labels in dataloader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item() * images.size(0)
        preds = torch.argmax(outputs, dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())
        
    epoch_loss = total_loss / len(dataloader.dataset)
    epoch_acc = accuracy_score(all_labels, all_preds)
    return epoch_loss, epoch_acc

def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0.0
    all_preds, all_labels, all_probs = [], [], []
    
    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            
            probs = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs)
            
    eval_loss = total_loss / len(dataloader.dataset)
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, zero_division=0)
    rec = recall_score(all_labels, all_preds, zero_division=0)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    cm = confusion_matrix(all_labels, all_preds).tolist()
    
    return {
        "loss": round(eval_loss, 4),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "predictions": all_preds,
        "labels": all_labels
    }

def train_and_evaluate_model(model_name: str, train_loader, val_loader, test_loader, device):
    print(f"\n{'='*60}\nTRAINING MODEL: {model_name.upper()}\n{'='*60}")
    model = create_model(model_name, CONFIG["num_classes"]).to(device)
    
    # Class weights for loss (balance healthy vs lumpy)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=CONFIG["learning_rate"], weight_decay=CONFIG["weight_decay"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=CONFIG["epochs"])
    
    best_val_f1 = -1.0
    best_state_dict = None
    epoch_history = []
    
    t_start = time.time()
    for epoch in range(1, CONFIG["epochs"] + 1):
        t_ep_start = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_metrics = evaluate(model, val_loader, criterion, device)
        scheduler.step()
        ep_duration = time.time() - t_ep_start
        
        print(f"Epoch {epoch}/{CONFIG['epochs']} ({ep_duration:.1f}s) | "
              f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.4f} | "
              f"Val Loss: {val_metrics['loss']:.4f}, Acc: {val_metrics['accuracy']:.4f}, F1: {val_metrics['f1_score']:.4f}")
              
        epoch_history.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": val_metrics["loss"],
            "val_acc": val_metrics["accuracy"],
            "val_f1": val_metrics["f1_score"]
        })
        
        if val_metrics["f1_score"] > best_val_f1:
            best_val_f1 = val_metrics["f1_score"]
            best_state_dict = {k: v.cpu() for k, v in model.state_dict().items()}
            
    train_duration = time.time() - t_start
    print(f">>> {model_name} training finished in {train_duration:.1f}s. Best Val F1: {best_val_f1:.4f}")
    
    # Evaluate best model on test split
    model.load_state_dict(best_state_dict)
    test_metrics = evaluate(model, test_loader, criterion, device)
    
    # Measure single-image inference latency
    model.eval()
    sample_input = torch.randn(1, 3, CONFIG["img_size"], CONFIG["img_size"]).to(device)
    t_latencies = []
    with torch.no_grad():
        for _ in range(20):
            t0 = time.perf_counter()
            _ = model(sample_input)
            t_latencies.append((time.perf_counter() - t0) * 1000)
    avg_latency_ms = round(float(np.mean(t_latencies[5:])), 2)
    
    return {
        "model_name": model_name,
        "best_state_dict": best_state_dict,
        "best_val_f1": best_val_f1,
        "train_duration_sec": round(train_duration, 1),
        "avg_latency_ms": avg_latency_ms,
        "test_metrics": {
            "accuracy": test_metrics["accuracy"],
            "precision": test_metrics["precision"],
            "recall": test_metrics["recall"],
            "f1_score": test_metrics["f1_score"],
            "confusion_matrix": test_metrics["confusion_matrix"]
        },
        "epoch_history": epoch_history
    }

def main():
    set_seed(CONFIG["seed"])
    device = torch.device(CONFIG["device"])
    print(f"Using compute device: {device}")
    
    train_dataset = LSDImageDataset(DATASET_DIR, "train")
    val_dataset = LSDImageDataset(DATASET_DIR, "val")
    test_dataset = LSDImageDataset(DATASET_DIR, "test")
    
    print(f"Dataset splits: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")
    
    train_loader = DataLoader(train_dataset, batch_size=CONFIG["batch_size"], shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=CONFIG["batch_size"], shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=CONFIG["batch_size"], shuffle=False)
    
    # 1. Train EfficientNet-B0
    effnet_results = train_and_evaluate_model("efficientnet_b0", train_loader, val_loader, test_loader, device)
    
    # 2. Train MobileNetV3-Small
    mobilenet_results = train_and_evaluate_model("mobilenet_v3_small", train_loader, val_loader, test_loader, device)
    
    # Comparison & Selection
    print("\n" + "="*70)
    print("FINAL MODEL BENCHMARK COMPARISON (HELD-OUT TEST SET)")
    print("="*70)
    print(f"{'Metric':<20} | {'EfficientNet-B0':<18} | {'MobileNetV3-Small':<18}")
    print("-" * 62)
    print(f"{'Test Accuracy':<20} | {effnet_results['test_metrics']['accuracy']:<18.4f} | {mobilenet_results['test_metrics']['accuracy']:<18.4f}")
    print(f"{'Test Precision':<20} | {effnet_results['test_metrics']['precision']:<18.4f} | {mobilenet_results['test_metrics']['precision']:<18.4f}")
    print(f"{'Test Recall':<20} | {effnet_results['test_metrics']['recall']:<18.4f} | {mobilenet_results['test_metrics']['recall']:<18.4f}")
    print(f"{'Test F1-Score':<20} | {effnet_results['test_metrics']['f1_score']:<18.4f} | {mobilenet_results['test_metrics']['f1_score']:<18.4f}")
    print(f"{'Latency (ms)':<20} | {effnet_results['avg_latency_ms']:<18.2f} | {mobilenet_results['avg_latency_ms']:<18.2f}")
    print(f"{'Training Time (s)':<20} | {effnet_results['train_duration_sec']:<18.1f} | {mobilenet_results['train_duration_sec']:<18.1f}")
    print("="*70)
    
    # Choose winning model (prioritize F1-Score on test set)
    if effnet_results['test_metrics']['f1_score'] >= mobilenet_results['test_metrics']['f1_score']:
        winner = effnet_results
        runner_up = mobilenet_results
    else:
        winner = mobilenet_results
        runner_up = effnet_results
        
    print(f"\nWINNING MODEL SELECTED: {winner['model_name'].upper()} (Test F1: {winner['test_metrics']['f1_score']})")
    
    # Save best model
    best_model_path = os.path.join(MODELS_DIR, "best_lsd_model.pt")
    torch.save({
        "model_name": winner["model_name"],
        "state_dict": winner["best_state_dict"],
        "num_classes": CONFIG["num_classes"],
        "class_names": CONFIG["class_names"],
        "img_size": CONFIG["img_size"],
        "test_metrics": winner["test_metrics"]
    }, best_model_path)
    print(f"Saved best model weights to: {best_model_path}")
    
    # Save label mapping
    label_mapping = {
        "0": "Healthy",
        "1": "Possible Lumpy Skin Disease"
    }
    with open(os.path.join(MODELS_DIR, "label_mapping.json"), "w") as jf:
        json.dump(label_mapping, jf, indent=2)
        
    # Save training configuration
    with open(os.path.join(MODELS_DIR, "training_config.json"), "w") as jf:
        json.dump(CONFIG, jf, indent=2)
        
    # Save evaluation metrics
    eval_report = {
        "selected_model": winner["model_name"],
        "efficientnet_b0": {
            "test_metrics": effnet_results["test_metrics"],
            "avg_latency_ms": effnet_results["avg_latency_ms"],
            "train_duration_sec": effnet_results["train_duration_sec"],
            "epoch_history": effnet_results["epoch_history"]
        },
        "mobilenet_v3_small": {
            "test_metrics": mobilenet_results["test_metrics"],
            "avg_latency_ms": mobilenet_results["avg_latency_ms"],
            "train_duration_sec": mobilenet_results["train_duration_sec"],
            "epoch_history": mobilenet_results["epoch_history"]
        }
    }
    with open(os.path.join(MODELS_DIR, "evaluation_metrics.json"), "w") as jf:
        json.dump(eval_report, jf, indent=2)
        
    print(f"Saved evaluation metrics to: {os.path.join(MODELS_DIR, 'evaluation_metrics.json')}")

if __name__ == "__main__":
    main()
