import os
import sys
import time
import json
import pandas as pd
import numpy as np

# Ensure stdout and stderr handle utf-8 safely across Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def train_yield_model(csv_path="datasets/crop_production.csv", output_path="ml-service/models/yield_lgbm.pkl"):
    """
    Trains a LightGBM/RandomForest regressor on historical crop production data.
    """
    print("\n[1/2] --- Training Crop Yield Model ---")
    if not os.path.exists(csv_path):
        print(f"[ERROR] {csv_path} not found. Please place crop_production.csv in the datasets/ folder.")
        return False

    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Dataset shape: {df.shape}")

    # Standardize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    # Handle missing values
    df = df.dropna(subset=['production', 'area'])
    df = df[df['area'] > 0]
    
    # Compute Yield (Production / Area) if not present
    if 'yield' not in df.columns:
        df['yield'] = df['production'] / df['area']
    
    # Filter outliers
    df = df[df['yield'] < df['yield'].quantile(0.99)]
    
    print(f"Cleaned dataset rows: {len(df):,}")
    
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    import pickle

    # Encode categorical features
    cat_cols = ['state_name', 'district_name', 'crop_year', 'season', 'crop']
    encoders = {}
    for col in cat_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    feature_cols = [c for c in cat_cols if c in df.columns] + ['area']
    X = df[feature_cols]
    y = df['yield']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    print("Fitting model...")
    model = RandomForestRegressor(n_estimators=50, max_depth=12, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    print(f"[SUCCESS] Yield Model R2 Score: {score:.4f}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump({"model": model, "encoders": encoders, "features": feature_cols}, f)
    print(f"Saved yield model to: {output_path}")
    return True

def train_soil_classifier(dataset_dir="datasets/soil_types", output_path="ml-service/models/soil_classifier.onnx"):
    """
    Trains an image classifier on the soil texture categories and exports to ONNX.
    """
    print("\n[2/2] --- Training Soil Image Classifier ---")
    
    # Auto-detect variations like 'datasets/Soil types' or 'datasets/soil_types'
    candidate_dirs = [dataset_dir, "datasets/Soil types", "datasets/soil types", "datasets/soil-types"]
    actual_dir = None
    for c in candidate_dirs:
        if os.path.exists(c) and os.path.isdir(c):
            actual_dir = c
            break

    if not actual_dir:
        print(f"[ERROR] Soil dataset folder not found among {candidate_dirs}.")
        return False

    subdirs = sorted([d for d in os.listdir(actual_dir) if os.path.isdir(os.path.join(actual_dir, d))])
    print(f"Dataset directory: {actual_dir}")
    print(f"Found soil categories ({len(subdirs)} classes): {subdirs}")
    if len(subdirs) < 2:
        print("[ERROR] Expected at least 2 subfolders for soil classes.")
        return False

    try:
        import torch
        import torch.nn as nn
        from torchvision import datasets, transforms, models
    except ImportError as e:
        print(f"[ERROR] PyTorch/torchvision is not installed: {e}")
        return False

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    dataset = datasets.ImageFolder(actual_dir, transform=transform)
    classes = dataset.classes
    print(f"Class mapping: {classes}")

    train_size = int(0.85 * len(dataset))
    val_size = len(dataset) - train_size
    train_data, val_data = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = torch.utils.data.DataLoader(train_data, batch_size=16, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_data, batch_size=16, shuffle=False)

    print(f"Total images: {len(dataset)} | Train: {train_size} | Validation: {val_size}")

    # Transfer Learning using MobileNetV3
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    num_classes = len(classes)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    epochs = 5
    print(f"Training for {epochs} epochs...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * images.size(0)

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (preds == labels).sum().item()

        val_acc = correct / total if total > 0 else 0
        loss_val = (running_loss / train_size) if train_size > 0 else 0
        print(f"Epoch {epoch+1}/{epochs} - Loss: {loss_val:.4f} - Val Acc: {val_acc*100:.2f}%")

    # Export to ONNX & save class mapping
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    dummy_input = torch.randn(1, 3, 224, 224, device=device)
    model.eval()
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=17,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"[SUCCESS] Exported ONNX model to: {output_path}")

    # Save classes JSON
    classes_path = os.path.join(os.path.dirname(output_path), "soil_classes.json")
    with open(classes_path, "w", encoding="utf-8") as f:
        json.dump(classes, f, indent=2)
    print(f"[SUCCESS] Saved soil classes mapping to: {classes_path}")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("AgriAI Training Script Initiator")
    print("=" * 60)
    train_yield_model()
    train_soil_classifier()

