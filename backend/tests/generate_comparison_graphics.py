"""
generate_comparison_graphics.py
--------------------------------
Gera gráficos de comparação entre Face Recognition e DeepFace.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from pathlib import Path

# Configurar estilo
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

# Resultados do teste (podem ser carregados de JSON)
RESULTS = {
    "face_recognition": {
        "accuracy": 0.776,
        "precision": 0.920,
        "recall": 0.727,
        "specificity": 0.874,
        "f1_score": 0.813,
        "tp": 208,
        "fn": 78,
        "tn": 125,
        "fp": 18,
        "total_known": 286,
        "total_unknown": 143,
        "avg_confidence": 27.5,
        "avg_time": 0.3051
    },
    "deepface": {
        "accuracy": 0.541,
        "precision": 0.989,
        "recall": 0.315,
        "specificity": 0.993,
        "f1_score": 0.477,
        "tp": 90,
        "fn": 196,
        "tn": 142,
        "fp": 1,
        "total_known": 286,
        "total_unknown": 143,
        "avg_confidence": 16.8,
        "avg_time": 0.2184
    }
}

OUTPUT_DIR = Path(__file__).parent / "comparison_results" / "graphics"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_metrics_comparison():
    """Gráfico de barras comparando métricas principais."""
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Specificity']
    fr_values = [
        RESULTS['face_recognition']['accuracy'],
        RESULTS['face_recognition']['precision'],
        RESULTS['face_recognition']['recall'],
        RESULTS['face_recognition']['f1_score'],
        RESULTS['face_recognition']['specificity']
    ]
    df_values = [
        RESULTS['deepface']['accuracy'],
        RESULTS['deepface']['precision'],
        RESULTS['deepface']['recall'],
        RESULTS['deepface']['f1_score'],
        RESULTS['deepface']['specificity']
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    bars1 = ax.bar(x - width/2, fr_values, width, label='Face Recognition', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, df_values, width, label='DeepFace (Facenet512)', color='#A23B72', alpha=0.8)
    
    ax.set_xlabel('Métricas', fontsize=13, fontweight='bold')
    ax.set_ylabel('Score (0-1)', fontsize=13, fontweight='bold')
    ax.set_title('Comparação de Métricas: Face Recognition vs DeepFace', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=12)
    ax.legend(fontsize=12, loc='upper right')
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', alpha=0.3)
    
    # Adicionar valores nas barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'metrics_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Salvo: {OUTPUT_DIR / 'metrics_comparison.png'}")
    plt.close()

def save_confusion_matrices():
    """Gráfico com matrizes de confusão lado a lado."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Face Recognition
    fr_cm = np.array([
        [RESULTS['face_recognition']['tp'], RESULTS['face_recognition']['fn']],
        [RESULTS['face_recognition']['fp'], RESULTS['face_recognition']['tn']]
    ])
    
    sns.heatmap(fr_cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax1,
                xticklabels=['Predicted\nKnown', 'Predicted\nUnknown'],
                yticklabels=['Actual\nKnown', 'Actual\nUnknown'],
                annot_kws={'size': 16, 'weight': 'bold'})
    ax1.set_title('Face Recognition\nConfusion Matrix', fontsize=14, fontweight='bold', pad=15)
    
    # DeepFace
    df_cm = np.array([
        [RESULTS['deepface']['tp'], RESULTS['deepface']['fn']],
        [RESULTS['deepface']['fp'], RESULTS['deepface']['tn']]
    ])
    
    sns.heatmap(df_cm, annot=True, fmt='d', cmap='Purples', cbar=False, ax=ax2,
                xticklabels=['Predicted\nKnown', 'Predicted\nUnknown'],
                yticklabels=['Actual\nKnown', 'Actual\nUnknown'],
                annot_kws={'size': 16, 'weight': 'bold'})
    ax2.set_title('DeepFace (Facenet512)\nConfusion Matrix', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'confusion_matrices.png', dpi=300, bbox_inches='tight')
    print(f"✓ Salvo: {OUTPUT_DIR / 'confusion_matrices.png'}")
    plt.close()

def save_performance_comparison():
    """Gráfico radar comparando todos os aspectos."""
    categories = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Specificity']
    
    fr_values = [
        RESULTS['face_recognition']['accuracy'],
        RESULTS['face_recognition']['precision'],
        RESULTS['face_recognition']['recall'],
        RESULTS['face_recognition']['f1_score'],
        RESULTS['face_recognition']['specificity']
    ]
    
    df_values = [
        RESULTS['deepface']['accuracy'],
        RESULTS['deepface']['precision'],
        RESULTS['deepface']['recall'],
        RESULTS['deepface']['f1_score'],
        RESULTS['deepface']['specificity']
    ]
    
    # Número de variáveis
    N = len(categories)
    
    # Ângulos para cada eixo
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    fr_values += fr_values[:1]
    df_values += df_values[:1]
    angles += angles[:1]
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Plot
    ax.plot(angles, fr_values, 'o-', linewidth=2, label='Face Recognition', color='#2E86AB')
    ax.fill(angles, fr_values, alpha=0.25, color='#2E86AB')
    
    ax.plot(angles, df_values, 'o-', linewidth=2, label='DeepFace', color='#A23B72')
    ax.fill(angles, df_values, alpha=0.25, color='#A23B72')
    
    # Configurar eixos
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
    ax.grid(True)
    
    # Título e legenda
    ax.set_title('Radar de Performance: Face Recognition vs DeepFace', 
                 fontsize=16, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'performance_radar.png', dpi=300, bbox_inches='tight')
    print(f"✓ Salvo: {OUTPUT_DIR / 'performance_radar.png'}")
    plt.close()

def save_true_false_comparison():
    """Gráfico empilhado mostrando TP, FN, TN, FP."""
    models = ['Face Recognition', 'DeepFace']
    
    # Resultados conhecidos (TP + FN)
    tp_values = [RESULTS['face_recognition']['tp'], RESULTS['deepface']['tp']]
    fn_values = [RESULTS['face_recognition']['fn'], RESULTS['deepface']['fn']]
    
    # Resultados desconhecidos (TN + FP)
    tn_values = [RESULTS['face_recognition']['tn'], RESULTS['deepface']['tn']]
    fp_values = [RESULTS['face_recognition']['fp'], RESULTS['deepface']['fp']]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Gráfico de Conhecidos
    x = np.arange(len(models))
    width = 0.5
    
    bars1 = ax1.bar(x, tp_values, width, label='True Positives (Correto)', color='#06D6A0')
    bars2 = ax1.bar(x, fn_values, width, bottom=tp_values, label='False Negatives (Não reconheceu)', color='#EF476F')
    
    ax1.set_ylabel('Número de Faces', fontsize=12, fontweight='bold')
    ax1.set_title('Faces Conhecidas (286 total)', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=12)
    ax1.legend(fontsize=11)
    ax1.set_ylim(0, 300)
    
    # Adicionar valores
    for i, (tp, fn) in enumerate(zip(tp_values, fn_values)):
        ax1.text(i, tp/2, f'{tp}', ha='center', va='center', fontsize=14, fontweight='bold', color='white')
        ax1.text(i, tp + fn/2, f'{fn}', ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    # Gráfico de Desconhecidos
    bars3 = ax2.bar(x, tn_values, width, label='True Negatives (Rejeitou)', color='#06D6A0')
    bars4 = ax2.bar(x, fp_values, width, bottom=tn_values, label='False Positives (Erro)', color='#EF476F')
    
    ax2.set_ylabel('Número de Faces', fontsize=12, fontweight='bold')
    ax2.set_title('Faces Desconhecidas (143 total)', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, fontsize=12)
    ax2.legend(fontsize=11)
    ax2.set_ylim(0, 150)
    
    # Adicionar valores
    for i, (tn, fp) in enumerate(zip(tn_values, fp_values)):
        ax2.text(i, tn/2, f'{tn}', ha='center', va='center', fontsize=14, fontweight='bold', color='white')
        if fp > 0:
            ax2.text(i, tn + fp/2, f'{fp}', ha='center', va='center', fontsize=14, fontweight='bold', color='white')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'tp_fp_tn_fn_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Salvo: {OUTPUT_DIR / 'tp_fp_tn_fn_comparison.png'}")
    plt.close()

def save_speed_comparison():
    """Gráfico comparando velocidade de processamento."""
    models = ['Face Recognition', 'DeepFace']
    times = [
        RESULTS['face_recognition']['avg_time'] * 1000,  # converter para ms
        RESULTS['deepface']['avg_time'] * 1000
    ]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.bar(models, times, color=['#2E86AB', '#A23B72'], alpha=0.8, width=0.5)
    
    ax.set_ylabel('Tempo Médio (ms)', fontsize=13, fontweight='bold')
    ax.set_title('Velocidade de Processamento por Imagem', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, max(times) * 1.2)
    
    # Adicionar valores
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
               f'{height:.1f}ms', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'speed_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Salvo: {OUTPUT_DIR / 'speed_comparison.png'}")
    plt.close()

def save_summary_table():
    """Criar imagem com tabela resumida de resultados."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = [
        ['Métrica', 'Face Recognition', 'DeepFace', 'Vencedor'],
        ['Accuracy', f"{RESULTS['face_recognition']['accuracy']:.1%}", 
         f"{RESULTS['deepface']['accuracy']:.1%}", '🏆 Face Recognition'],
        ['Precision', f"{RESULTS['face_recognition']['precision']:.1%}", 
         f"{RESULTS['deepface']['precision']:.1%}", '🏆 DeepFace'],
        ['Recall', f"{RESULTS['face_recognition']['recall']:.1%}", 
         f"{RESULTS['deepface']['recall']:.1%}", '🏆 Face Recognition'],
        ['F1 Score', f"{RESULTS['face_recognition']['f1_score']:.3f}", 
         f"{RESULTS['deepface']['f1_score']:.3f}", '🏆 Face Recognition'],
        ['Specificity', f"{RESULTS['face_recognition']['specificity']:.1%}", 
         f"{RESULTS['deepface']['specificity']:.1%}", '🏆 DeepFace'],
        ['True Positives', f"{RESULTS['face_recognition']['tp']}/286", 
         f"{RESULTS['deepface']['tp']}/286", '🏆 Face Recognition'],
        ['False Positives', str(RESULTS['face_recognition']['fp']), 
         str(RESULTS['deepface']['fp']), '🏆 DeepFace'],
        ['Velocidade (ms)', f"{RESULTS['face_recognition']['avg_time']*1000:.1f}", 
         f"{RESULTS['deepface']['avg_time']*1000:.1f}", '🏆 DeepFace']
    ]
    
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                    colWidths=[0.25, 0.25, 0.25, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 3)
    
    # Estilizar cabeçalho
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#2C3E50')
        cell.set_text_props(weight='bold', color='white', size=14)
    
    # Estilizar células
    for i in range(1, len(table_data)):
        for j in range(4):
            cell = table[(i, j)]
            if j == 3:  # Coluna vencedor
                cell.set_facecolor('#E8F5E9' if 'Face Recognition' in table_data[i][j] else '#FFF3E0')
            else:
                cell.set_facecolor('#F8F9FA' if i % 2 == 0 else 'white')
            cell.set_text_props(size=11)
    
    plt.title('Tabela Comparativa: Face Recognition vs DeepFace', 
              fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'summary_table.png', dpi=300, bbox_inches='tight')
    print(f"✓ Salvo: {OUTPUT_DIR / 'summary_table.png'}")
    plt.close()

if __name__ == "__main__":
    print("Gerando gráficos de comparação...\n")
    
    save_metrics_comparison()
    save_confusion_matrices()
    save_performance_comparison()
    save_true_false_comparison()
    save_speed_comparison()
    save_summary_table()
    
    print(f"\n✓ Todos os gráficos foram salvos em: {OUTPUT_DIR}")
    print("\nGráficos gerados:")
    print("  1. metrics_comparison.png - Comparação de métricas")
    print("  2. confusion_matrices.png - Matrizes de confusão")
    print("  3. performance_radar.png - Radar de performance")
    print("  4. tp_fp_tn_fn_comparison.png - Comparação TP/FP/TN/FN")
    print("  5. speed_comparison.png - Velocidade de processamento")
    print("  6. summary_table.png - Tabela resumida")
