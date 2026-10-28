# Construction PPE Datasets

This directory holds dataset metadata. Raw images, labels, and videos are **not committed to git** (see `.gitignore`).

---

## Recommended Datasets for PPE Detection

### 1. Hard Hat Workers (Roboflow Universe)
- **URL**: https://universe.roboflow.com/object-detection/hard-hat-workers
- **Classes**: `helmet`, `person`, `vest` (varies by version)
- **Format**: YOLOv8 / YOLO format bounding boxes
- **License**: MIT / CC BY 4.0 (check specific dataset version)
- **Size**: ~7,000 images

### 2. Construction Site Safety Dataset (Roboflow)
- **URL**: https://universe.roboflow.com/construction-site-safety
- **Classes**: `Hardhat`, `Mask`, `NO-Hardhat`, `NO-Mask`, `NO-Safety Vest`, `Person`, `Safety Cone`, `Safety Vest`, `machinery`, `vehicle`
- **Format**: YOLOv8
- **License**: CC BY 4.0
- **Size**: ~3,000+ images

### 3. PPE Detection Dataset (Kaggle)
- **URL**: https://www.kaggle.com/datasets/snehilsanyal/construction-site-safety-image-dataset-roboflow
- **Notes**: Good variety of lighting conditions and camera angles

---

## Dataset Preparation Instructions

### Step 1 – Download
1. Create a free Roboflow account at https://roboflow.com
2. Navigate to the chosen dataset
3. Select **YOLOv8** export format
4. Download the zip and extract to `datasets/`

### Step 2 – Directory structure expected by training scripts
```
datasets/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
├── labels/
│   ├── train/
│   ├── val/
│   └── test/
└── data.yaml
```

### Step 3 – Verify `data.yaml`
```yaml
path: ../datasets
train: images/train
val: images/val
test: images/test

nc: 10  # number of classes
names:
  - Hardhat
  - Mask
  - NO-Hardhat
  - NO-Mask
  - NO-Safety Vest
  - Person
  - Safety Cone
  - Safety Vest
  - machinery
  - vehicle
```

---

## Annotation Format (YOLO)

Each label file (`.txt`) has one row per object:
```
class_id  cx  cy  width  height
```
All values are normalized (0.0–1.0) relative to image size.

---

## Important Notes

- **Never mix train/val/test frames from the same video clip** to avoid data leakage.
- Augmentation (flip, rotate, brightness) should be applied only to the training set.
- Keep a held-out test set that the model never sees during training or validation.
