# Face Recognition vs DeepFace: Comparison Index

## 📂 Directory Structure

```
comparison_results/
├── README.md                          # 📖 Full comparison documentation
├── QUICKSTART.md                      # 🚀 Step-by-step reproduction guide
├── INDEX.md                           # 📑 This file
├── graphics/                          # 📊 All visualization charts
│   ├── metrics_comparison.png         # Bar chart: metrics comparison
│   ├── confusion_matrices.png         # Side-by-side confusion matrices
│   ├── performance_radar.png          # Radar chart: all metrics
│   ├── tp_fp_tn_fn_comparison.png    # True/False Positives/Negatives
│   ├── speed_comparison.png           # Processing speed comparison
│   └── summary_table.png              # Complete results table
└── data/
    └── test_results.json              # Structured test results
```

---

## 🎯 Quick Navigation

### Want to understand the results?
👉 **[Read the Full Documentation](README.md)**

### Want to reproduce the test?
👉 **[Follow the Quick Start Guide](QUICKSTART.md)**

### Want to see visualizations?
👉 **[View Graphics Folder](graphics/)**

### Want raw data?
👉 **[Check JSON Results](data/test_results.json)**

---

## 📊 Key Results at a Glance

| Metric | Face Recognition | DeepFace | Winner |
|--------|------------------|----------|--------|
| **Accuracy** | **77.6%** | 54.1% | 🏆 Face Recognition |
| **F1 Score** | **0.813** | 0.477 | 🏆 Face Recognition |
| **Recall** | **72.7%** | 31.5% | 🏆 Face Recognition |
| **Precision** | 92.0% | **98.9%** | 🏆 DeepFace |
| **Speed** | 305ms | **218ms** | 🏆 DeepFace |

### 🏆 Overall Winner: Face Recognition
- Better accuracy by 23.5 percentage points
- Better balance between finding faces and avoiding false alarms
- Suitable for production use

---

## 📈 Visual Summary

### Metrics Comparison
![Metrics](graphics/metrics_comparison.png)

### Confusion Matrices
![Confusion Matrices](graphics/confusion_matrices.png)

### Performance Radar
![Radar](graphics/performance_radar.png)

---

## 🔬 Test Details

- **Total Images Tested:** 429
- **Known Celebrities:** 30 (286 images)
- **Unknown Celebrities:** 15 (143 images)
- **Image Size:** 300×300 pixels
- **Test Type:** Blind recognition test
- **Date:** November 8, 2025

---

## 📝 Files Description

### Documentation
- **README.md**: Complete analysis with methodology, results, and recommendations (20+ pages)
- **QUICKSTART.md**: Step-by-step guide to reproduce the test (~5 pages)
- **INDEX.md**: This navigation file

### Graphics (PNG, 300 DPI)
1. **metrics_comparison.png**: Bar chart showing Accuracy, Precision, Recall, F1, Specificity
2. **confusion_matrices.png**: True Positives, False Negatives, True Negatives, False Positives
3. **performance_radar.png**: Radar visualization of all performance metrics
4. **tp_fp_tn_fn_comparison.png**: Detailed breakdown of classification results
5. **speed_comparison.png**: Processing time per image comparison
6. **summary_table.png**: Complete results in table format

### Data
- **test_results.json**: Machine-readable test results with all metrics, confusion matrices, and metadata

---

## 🚀 Quick Commands

### Run the Test
```powershell
cd tests
python test_celebrity_blind.py test_dataset celebrity_dataset
```

### Generate Graphics
```powershell
cd tests
python generate_comparison_graphics.py
```

### Resize Images
```powershell
cd tests
python resize_celebrity_dataset.py
```

---

## 💡 Key Findings

1. **Face Recognition is 43% more accurate** (77.6% vs 54.1%)
2. **DeepFace missed 68.5% of known faces** (196 out of 286)
3. **Face Recognition had only 18 false positives** out of 143 unknown faces
4. **DeepFace had only 1 false positive** but at the cost of poor recall
5. **Face Recognition provides better balance** for real-world use

---

## 🎓 Educational Value

This comparison demonstrates:
- ✅ How to properly evaluate ML models
- ✅ Importance of balanced metrics (not just accuracy)
- ✅ Difference between Precision and Recall
- ✅ Real-world testing methodology
- ✅ When to choose which model

---

## 📞 Support

For questions about this comparison:
- Repository: LSenzaki/Integrador
- Branch: face_recognitionXdeepface

---

## 📅 Changelog

**November 8, 2025**
- Initial comparison completed
- 429 images tested
- 6 visualizations generated
- Documentation published

---

**Estimated Reading Time:**
- INDEX.md: 2 minutes
- QUICKSTART.md: 10 minutes
- README.md: 30 minutes
- Complete study: 1 hour

**Start here:** [README.md](README.md) 📖
