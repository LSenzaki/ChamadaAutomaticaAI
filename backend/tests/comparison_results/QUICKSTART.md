# Quick Start Guide: Face Recognition vs DeepFace Comparison

This guide will help you reproduce the comparison test between Face Recognition and DeepFace.

---

## 📋 Prerequisites

### 1. Python Environment
- Python 3.11 or higher
- pip package manager

### 2. Install Dependencies

```powershell
# Navigate to backend directory
cd backend

# Install required packages
pip install face-recognition==1.3.0
pip install deepface==0.0.95
pip install tensorflow==2.20.0
pip install scikit-learn==1.7.2
pip install pandas==2.3.2
pip install matplotlib==3.10.6
pip install seaborn==0.13.2
pip install pillow
```

Or install from requirements.txt:
```powershell
pip install -r requirements.txt
```

---

## 📁 Dataset Preparation

### Option 1: Use Provided Datasets

If you already have the datasets:
- `tests/test_dataset/` - 30 celebrities for training
- `tests/celebrity_dataset/` - 45 celebrities (30 known + 15 unknown) for testing

### Option 2: Create Your Own Datasets

#### Training Dataset Structure
```
test_dataset/
├── person1/
│   └── photo.jpg
├── person2/
│   └── photo.jpg
└── ... (at least 2-3 people)
```

#### Testing Dataset Structure
```
celebrity_dataset/
├── person1/          # Known person (in training)
│   ├── test1.jpg
│   └── test2.jpg
├── unknown_person1/  # Unknown person (not in training)
│   ├── photo1.jpg
│   └── photo2.jpg
└── ...
```

### Image Requirements
- Format: JPG, JPEG, or PNG
- Minimum size: 300×300 pixels (will be resized automatically)
- Face clearly visible
- One person per image

---

## 🖼️ Resize Images (Optional but Recommended)

To prevent memory issues with large images:

```powershell
python tests/resize_celebrity_dataset.py
```

This will:
- Resize all images to 300×300 pixels
- Convert PNG with transparency to RGB
- Save space and improve processing speed

**Custom size:**
```powershell
python tests/resize_celebrity_dataset.py 500  # Resize to 500×500
```

---

## 🧪 Run the Comparison Test

### Full Test (Recommended)

Run the complete blind celebrity test:

```powershell
cd tests
python test_celebrity_blind.py test_dataset celebrity_dataset
```

**Expected duration:** 2-3 minutes for 429 images

**Output:**
- Real-time progress for each test
- Detailed results showing TP, FP, TN, FN
- Final metrics: Accuracy, Precision, Recall, F1 Score
- Winner declaration

### Sample Output
```
================================================================================
RESULTADOS FINAIS
================================================================================

FACE RECOGNITION:
  Accuracy:                0.776 (77.6%)
  Precision:               0.920
  Recall (Sensitivity):    0.727
  F1 Score:                0.813

DEEPFACE (Facenet512):
  Accuracy:                0.541 (54.1%)
  Precision:               0.989
  Recall (Sensitivity):    0.315
  F1 Score:                0.477

🏆 VENCEDOR: FACE RECOGNITION
```

---

## 📊 Generate Visualizations

Create all comparison charts:

```powershell
cd tests
python generate_comparison_graphics.py
```

**Generates 6 graphics:**
1. `metrics_comparison.png` - Bar chart comparing metrics
2. `confusion_matrices.png` - Confusion matrices side by side
3. `performance_radar.png` - Radar chart of all metrics
4. `tp_fp_tn_fn_comparison.png` - True/False Positives/Negatives
5. `speed_comparison.png` - Processing time comparison
6. `summary_table.png` - Complete results table

**Output location:** `tests/comparison_results/graphics/`

---

## 📈 View Results

### 1. Graphics
All charts are saved in:
```
tests/comparison_results/graphics/
```

Open them with any image viewer.

### 2. JSON Data
Structured results are available in:
```
tests/comparison_results/data/test_results.json
```

### 3. Documentation
Read the full analysis:
```
tests/comparison_results/README.md
```

---

## 🔧 Troubleshooting

### Memory Errors
**Problem:** `"bad allocation"` or `"Insufficient memory"`

**Solution:** Resize images first:
```powershell
cd tests
python resize_celebrity_dataset.py
```

### Module Not Found
**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:** Run from the `tests` directory:
```powershell
cd tests
python test_celebrity_blind.py test_dataset celebrity_dataset
```

### Face Detection Failures
**Problem:** `"Face could not be detected"`

**Causes:**
- Image too small
- Face not clearly visible
- Profile shot
- Poor lighting

**Solution:** These are counted as failures in the metrics. Ensure training images have clear, frontal faces.

### Slow Processing
**Problem:** Test takes too long

**Solutions:**
1. Resize images to 300×300
2. Use fewer test images
3. Close other applications to free CPU

---

## 📝 Customization

### Test with Your Own Images

1. Create training dataset:
```
my_training_dataset/
├── john_doe/
│   └── john.jpg
├── jane_smith/
│   └── jane.jpg
└── ...
```

2. Create test dataset with known + unknown people

3. Run test:
```powershell
cd tests
python test_celebrity_blind.py my_training_dataset my_test_dataset
```

### Change Image Size

Edit `resize_celebrity_dataset.py`:
```python
target_size = (500, 500)  # Change from (300, 300)
```

### Modify Comparison Thresholds

Edit `app/services/face_service.py` or `deepface_service.py`:
```python
# Face Recognition threshold (default: 0.6)
tolerance = 0.5  # Lower = stricter

# DeepFace threshold (default: varies by model)
threshold = 0.4  # Lower = stricter
```

---

## 🎯 Expected Results

### Face Recognition
- **Accuracy:** ~75-80%
- **Precision:** ~90-95%
- **Recall:** ~70-75%
- **F1 Score:** ~0.80-0.85

### DeepFace (Facenet512)
- **Accuracy:** ~50-60%
- **Precision:** ~95-99%
- **Recall:** ~30-35%
- **F1 Score:** ~0.45-0.50

**Winner:** Face Recognition (better overall performance)

---

## 🚀 Advanced Usage

### Run Via API

Start the FastAPI server:
```powershell
uvicorn app.main:app --reload
```

Access API endpoints:
- POST `/comparison/register/{model}` - Register face
- POST `/comparison/recognize/{model}` - Recognize face
- GET `/comparison/compare` - Compare both models
- GET `/comparison/metrics/{model}` - Get metrics

API documentation: http://localhost:8000/docs

### Generate Custom Graphics

Edit `tests/generate_comparison_graphics.py` to:
- Add new chart types
- Change colors and styles
- Adjust figure sizes
- Export to different formats (SVG, PDF)

---

## 📚 Additional Resources

- **Full Documentation:** `tests/comparison_results/README.md`
- **Test Results:** `tests/comparison_results/data/test_results.json`
- **Graphics:** `tests/comparison_results/graphics/`

### Library Documentation
- Face Recognition: https://github.com/ageitgey/face_recognition
- DeepFace: https://github.com/serengil/deepface
- scikit-learn Metrics: https://scikit-learn.org/stable/modules/model_evaluation.html

---

## ✅ Checklist

- [ ] Python 3.11+ installed
- [ ] All dependencies installed
- [ ] Datasets prepared (training + testing)
- [ ] Images resized to 300×300
- [ ] Test executed successfully
- [ ] Graphics generated
- [ ] Results reviewed

---

## 🤝 Support

If you encounter issues:

1. Check this troubleshooting section
2. Verify all prerequisites are met
3. Ensure datasets are properly structured
4. Check Python version and dependencies
5. Review error messages carefully

---

## 🎓 Learning Outcomes

After completing this comparison, you will understand:

- ✅ How to evaluate facial recognition models
- ✅ Difference between Precision, Recall, and F1 Score
- ✅ When to use Face Recognition vs DeepFace
- ✅ How to handle real-world facial recognition challenges
- ✅ Importance of balanced metrics in ML evaluation

---

**Time to Complete:** ~30 minutes (including dataset preparation)

**Difficulty:** Intermediate

**Good luck! 🚀**
