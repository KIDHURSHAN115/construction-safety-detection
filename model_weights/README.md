# Model Weights

Model weight files (`.pt`, `.pth`, `.onnx`) are **not committed to git** because they are large binary files.

---

## How to Obtain Model Weights

### Phase 1 – YOLOv8 Nano (COCO pretrained)

YOLOv8 weights are downloaded automatically by Ultralytics on first use.

```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")  # Downloads automatically to this folder
```

After first run, move `yolov8n.pt` to `model_weights/yolov8n.pt` and update the path in `backend/app/config.py`.

### Phase 2 – PPE-specific Fine-tuned Model

After training on the construction PPE dataset, save the best checkpoint here:

```
model_weights/
├── yolov8n.pt               # Base COCO model (person detection)
├── ppe_detector.pt          # Fine-tuned PPE model (after Phase 2 training)
└── README.md
```

---

## Model Performance Targets (measured, not guaranteed)

| Metric | Target | Notes |
|--------|--------|-------|
| mAP@0.5 (PPE) | > 0.70 | Measured on held-out test set |
| Inference FPS | > 10 | On CPU, 640px input |
| Person detection recall | > 0.85 | At confidence ≥ 0.4 |

Actual results will be documented in `docs/model_evaluation.md` after training.

---

## Model Versions

| File | Classes | Source | Notes |
|------|---------|--------|-------|
| `yolov8n.pt` | 80 COCO classes | Ultralytics | Auto-downloaded |
| `ppe_detector.pt` | See datasets/README | Custom training | Phase 2 |

---

## Important

- Do not share model weights trained on proprietary data.
- Check Ultralytics AGPL-3.0 license terms for commercial use.
- Custom-trained models inherit the license of their training data.
