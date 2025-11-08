# Tests - Face Recognition vs DeepFace Comparison

This folder contains all comparison-related files, datasets, and results.

## 📂 Structure

```
tests/
├── 📊 comparison_results/          # Complete comparison documentation & results
│   ├── INDEX.md                    # Navigation guide (START HERE!)
│   ├── README.md                   # Full documentation (30+ pages)
│   ├── QUICKSTART.md               # Step-by-step reproduction guide
│   ├── STRUCTURE.md                # Project structure overview
│   ├── graphics/                   # 6 professional visualizations (PNG, 300 DPI)
│   └── data/                       # Structured JSON results
│
├── 🧪 Test Scripts
│   ├── test_celebrity_blind.py     # Main comparison test
│   ├── generate_comparison_graphics.py  # Graphics generator
│   └── resize_celebrity_dataset.py # Image preprocessing utility
│
└── 📁 Datasets
    ├── test_dataset/               # Training data (30 celebrities)
    └── celebrity_dataset/          # Testing data (429 images, 45 celebrities)
```

---

## 🚀 Quick Start

### 1. View Results
```powershell
# Read documentation
comparison_results/INDEX.md
```

### 2. Run Comparison Test
```powershell
cd tests
python test_celebrity_blind.py test_dataset celebrity_dataset
```

### 3. Generate Graphics
```powershell
cd tests
python generate_comparison_graphics.py
```

---

## 📊 Results Summary

**Winner:** Face Recognition 🏆

| Metric | Face Recognition | DeepFace | 
|--------|------------------|----------|
| Accuracy | **77.6%** | 54.1% |
| F1 Score | **0.813** | 0.477 |
| Recall | **72.7%** | 31.5% |

**Full documentation:** [comparison_results/README.md](comparison_results/README.md)

---

## 📝 Files Description

### Test Scripts
- **test_celebrity_blind.py**: Blind recognition test with known/unknown celebrities
- **generate_comparison_graphics.py**: Creates 6 professional comparison charts
- **resize_celebrity_dataset.py**: Preprocesses images to 300×300 pixels

### Datasets
- **test_dataset/**: 30 known celebrities for training (1-3 photos each)
- **celebrity_dataset/**: 45 celebrities for testing (30 known + 15 unknown, ~10 photos each)

### Results
- **comparison_results/**: Complete documentation, graphics, and structured data
  - All markdown documentation
  - 6 PNG graphics (300 DPI)
  - JSON results file

---

## ⚙️ Requirements

All requirements are in `../requirements.txt`:
- face-recognition==1.3.0
- deepface==0.0.95
- tensorflow==2.20.0
- scikit-learn==1.7.2
- pandas==2.3.2
- matplotlib==3.10.6
- seaborn==0.13.2

---

## 🎯 Use Cases

### Reproduce the Test
1. Ensure datasets are in place (`test_dataset/` and `celebrity_dataset/`)
2. Run: `python test_celebrity_blind.py test_dataset celebrity_dataset`
3. View results in terminal and `comparison_results/`

### Create Your Own Test
1. Prepare training dataset (known faces)
2. Prepare test dataset (mix of known + unknown faces)
3. Run: `python test_celebrity_blind.py your_train your_test`

### Generate Graphics Only
1. Run: `python generate_comparison_graphics.py`
2. Graphics saved in `comparison_results/graphics/`

---

## 📚 Documentation

**Start here:** [comparison_results/INDEX.md](comparison_results/INDEX.md)

**Full analysis:** [comparison_results/README.md](comparison_results/README.md)

**Quick guide:** [comparison_results/QUICKSTART.md](comparison_results/QUICKSTART.md)

---

**This folder contains everything needed for the Face Recognition vs DeepFace comparison!**
