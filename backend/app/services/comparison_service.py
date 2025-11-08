"""
app/services/comparison_service.py
-----------------------------------
Serviço para comparar modelos de reconhecimento facial (face_recognition vs DeepFace).
Calcula métricas: Cohen's Kappa, Macro F1, Precision, Recall, Accuracy.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.metrics import (
    cohen_kappa_score, 
    f1_score, 
    precision_score, 
    recall_score, 
    accuracy_score,
    confusion_matrix,
    classification_report
)
import json
import time
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo
import matplotlib.pyplot as plt
import seaborn as sns
import os

class ModelComparison:
    """Classe para comparar dois modelos de reconhecimento facial."""
    
    def __init__(self):
        self.results = {
            "face_recognition": {
                "predictions": [],
                "ground_truth": [],
                "confidence_scores": [],
                "processing_times": [],
                "errors": []
            },
            "deepface": {
                "predictions": [],
                "ground_truth": [],
                "confidence_scores": [],
                "processing_times": [],
                "errors": []
            },
            "metadata": {
                "total_tests": 0,
                "timestamp": None,
                "deepface_model": None,
                "deepface_detector": None,
                "deepface_metric": None
            }
        }
    
    def add_prediction(
        self, 
        model_name: str,
        predicted_id: Optional[int],
        true_id: int,
        confidence: float,
        processing_time: float,
        error: Optional[str] = None
    ):
        """
        Adiciona uma predição ao conjunto de resultados.
        
        Args:
            model_name: 'face_recognition' ou 'deepface'
            predicted_id: ID previsto pelo modelo (None se não reconhecido)
            true_id: ID verdadeiro (ground truth)
            confidence: Confiança da predição
            processing_time: Tempo de processamento em segundos
            error: Mensagem de erro, se houver
        """
        if model_name not in self.results:
            raise ValueError(f"Modelo desconhecido: {model_name}")
        
        self.results[model_name]["predictions"].append(predicted_id if predicted_id else -1)
        self.results[model_name]["ground_truth"].append(true_id)
        self.results[model_name]["confidence_scores"].append(confidence)
        self.results[model_name]["processing_times"].append(processing_time)
        if error:
            self.results[model_name]["errors"].append(error)
    
    def calculate_metrics(self, model_name: str) -> Dict:
        """
        Calcula todas as métricas para um modelo específico.
        
        Args:
            model_name: Nome do modelo
        
        Returns:
            Dicionário com todas as métricas calculadas
        """
        data = self.results[model_name]
        y_true = np.array(data["ground_truth"])
        y_pred = np.array(data["predictions"])
        confidence_scores = np.array(data["confidence_scores"])
        
        # Identificar predições válidas e falhas
        valid_indices = y_pred != -1
        valid_predictions = int(np.sum(valid_indices))
        failed_predictions = int(np.sum(~valid_indices))
        
        # Confiança média apenas de predições válidas (que retornaram resultado)
        valid_confidences = confidence_scores[valid_indices]
        avg_confidence_valid = float(np.mean(valid_confidences)) if len(valid_confidences) > 0 else 0.0
        
        # Confiança média de TODAS as predições (falhas = 0% confiança)
        avg_confidence_all = float(np.mean(confidence_scores)) if len(confidence_scores) > 0 else 0.0
        
        metrics = {
            "total_predictions": len(y_true),
            "valid_predictions": valid_predictions,
            "failed_predictions": failed_predictions,
            "avg_confidence_all": avg_confidence_all,  # Média incluindo falhas
            "avg_confidence_valid": avg_confidence_valid,  # Média apenas de predições válidas
            "avg_processing_time": float(np.mean(data["processing_times"])) if data["processing_times"] else 0.0,
            "total_processing_time": float(np.sum(data["processing_times"])) if data["processing_times"] else 0.0,
        }
        
        # ACCURACY REAL: incluindo falhas como erros
        # Falhas contam como predições incorretas
        correct_predictions = int(np.sum(y_true[valid_indices] == y_pred[valid_indices]))
        metrics["accuracy"] = float(correct_predictions / len(y_true)) if len(y_true) > 0 else 0.0
        metrics["correct_predictions"] = correct_predictions
        metrics["incorrect_predictions"] = len(y_true) - correct_predictions
        
        # Métricas apenas para predições válidas (para comparação com metodologia antiga)
        if valid_predictions > 0:
            y_true_valid = y_true[valid_indices]
            y_pred_valid = y_pred[valid_indices]
            
            # Accuracy apenas de predições válidas
            metrics["accuracy_valid_only"] = float(accuracy_score(y_true_valid, y_pred_valid))
            
            # Precision, Recall, F1 (Macro)
            metrics["precision_macro"] = float(precision_score(y_true_valid, y_pred_valid, average='macro', zero_division=0))
            metrics["recall_macro"] = float(recall_score(y_true_valid, y_pred_valid, average='macro', zero_division=0))
            metrics["f1_macro"] = float(f1_score(y_true_valid, y_pred_valid, average='macro', zero_division=0))
            
            # Precision, Recall, F1 (Weighted)
            metrics["precision_weighted"] = float(precision_score(y_true_valid, y_pred_valid, average='weighted', zero_division=0))
            metrics["recall_weighted"] = float(recall_score(y_true_valid, y_pred_valid, average='weighted', zero_division=0))
            metrics["f1_weighted"] = float(f1_score(y_true_valid, y_pred_valid, average='weighted', zero_division=0))
            
            # Cohen's Kappa (apenas válidos)
            metrics["cohen_kappa"] = float(cohen_kappa_score(y_true_valid, y_pred_valid))
            
            # Confusion Matrix
            cm = confusion_matrix(y_true_valid, y_pred_valid)
            metrics["confusion_matrix"] = cm.tolist()
            
            # Classification Report
            unique_labels = np.unique(np.concatenate([y_true_valid, y_pred_valid]))
            report = classification_report(y_true_valid, y_pred_valid, labels=unique_labels, output_dict=True, zero_division=0)
            metrics["classification_report"] = report
            
            # True Positives, False Positives (apenas para válidos)
            metrics["true_positives"] = int(np.sum(y_true_valid == y_pred_valid))
            metrics["false_positives"] = int(np.sum((y_true_valid != y_pred_valid) & (y_pred_valid != -1)))
        else:
            # Sem predições válidas
            metrics["accuracy_valid_only"] = 0.0
            metrics["precision_macro"] = 0.0
            metrics["recall_macro"] = 0.0
            metrics["f1_macro"] = 0.0
            metrics["cohen_kappa"] = 0.0
            metrics["confusion_matrix"] = []
            metrics["true_positives"] = 0
            metrics["false_positives"] = 0
        
        return metrics
    
    def compare_models(self) -> Dict:
        """
        Compara os dois modelos e retorna um relatório completo.
        
        Returns:
            Dicionário com comparação completa e métricas
        """
        fr_metrics = self.calculate_metrics("face_recognition")
        df_metrics = self.calculate_metrics("deepface")
        
        comparison = {
            "face_recognition": fr_metrics,
            "deepface": df_metrics,
            "comparison": {
                "accuracy_diff": df_metrics["accuracy"] - fr_metrics["accuracy"],
                "f1_macro_diff": df_metrics["f1_macro"] - fr_metrics["f1_macro"],
                "cohen_kappa_diff": df_metrics["cohen_kappa"] - fr_metrics["cohen_kappa"],
                "speed_diff": fr_metrics["avg_processing_time"] - df_metrics["avg_processing_time"],
                "winner_accuracy": "deepface" if df_metrics["accuracy"] > fr_metrics["accuracy"] else "face_recognition",
                "winner_f1": "deepface" if df_metrics["f1_macro"] > fr_metrics["f1_macro"] else "face_recognition",
                "winner_speed": "deepface" if df_metrics["avg_processing_time"] < fr_metrics["avg_processing_time"] else "face_recognition"
            },
            "metadata": self.results["metadata"]
        }
        
        return comparison
    
    def generate_report(self, output_dir: str = "comparison_reports") -> str:
        """
        Gera um relatório visual completo com gráficos e salva em arquivo.
        
        Args:
            output_dir: Diretório onde salvar os arquivos
        
        Returns:
            Caminho do arquivo JSON com o relatório
        """
        os.makedirs(output_dir, exist_ok=True)
        
        comparison = self.compare_models()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salvar JSON
        json_path = os.path.join(output_dir, f"comparison_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)
        
        # Gerar gráficos
        self._generate_plots(comparison, output_dir, timestamp)
        
        return json_path
    
    def _generate_plots(self, comparison: Dict, output_dir: str, timestamp: str):
        """Gera gráficos comparativos."""
        
        # Configurar estilo
        sns.set_theme(style="whitegrid")
        
        # 1. Gráfico de barras comparando métricas principais
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        metrics_to_plot = ['accuracy', 'f1_macro', 'precision_macro', 'recall_macro']
        titles = ['Accuracy', 'F1 Score (Macro)', 'Precision (Macro)', 'Recall (Macro)']
        
        for idx, (metric, title) in enumerate(zip(metrics_to_plot, titles)):
            ax = axes[idx // 2, idx % 2]
            
            fr_value = comparison['face_recognition'][metric]
            df_value = comparison['deepface'][metric]
            
            bars = ax.bar(['Face Recognition', 'DeepFace'], [fr_value, df_value], 
                         color=['#3498db', '#e74c3c'])
            ax.set_ylabel('Score')
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_ylim(0, 1)
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"metrics_comparison_{timestamp}.png"), dpi=300)
        plt.close()
        
        # 2. Cohen's Kappa e Processing Time
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Cohen's Kappa
        kappa_fr = comparison['face_recognition']['cohen_kappa']
        kappa_df = comparison['deepface']['cohen_kappa']
        
        bars = axes[0].bar(['Face Recognition', 'DeepFace'], [kappa_fr, kappa_df],
                          color=['#3498db', '#e74c3c'])
        axes[0].set_ylabel('Cohen\'s Kappa Score')
        axes[0].set_title('Cohen\'s Kappa Comparison', fontsize=14, fontweight='bold')
        axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[0].set_ylim(-1, 1)
        
        for bar in bars:
            height = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}',
                        ha='center', va='bottom' if height > 0 else 'top', fontweight='bold')
        
        # Processing Time
        time_fr = comparison['face_recognition']['avg_processing_time']
        time_df = comparison['deepface']['avg_processing_time']
        
        bars = axes[1].bar(['Face Recognition', 'DeepFace'], [time_fr, time_df],
                          color=['#3498db', '#e74c3c'])
        axes[1].set_ylabel('Average Time (seconds)')
        axes[1].set_title('Processing Time Comparison', fontsize=14, fontweight='bold')
        
        for bar in bars:
            height = bar.get_height()
            axes[1].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.4f}s',
                        ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"kappa_time_{timestamp}.png"), dpi=300)
        plt.close()
        
        # 3. Confusion Matrices (se houver)
        if comparison['face_recognition'].get('confusion_matrix'):
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            
            for idx, (model_name, ax) in enumerate([('face_recognition', axes[0]), ('deepface', axes[1])]):
                cm = np.array(comparison[model_name]['confusion_matrix'])
                
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, cbar=True)
                ax.set_title(f'{model_name.replace("_", " ").title()} - Confusion Matrix', 
                           fontsize=14, fontweight='bold')
                ax.set_ylabel('True Label')
                ax.set_xlabel('Predicted Label')
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"confusion_matrices_{timestamp}.png"), dpi=300)
            plt.close()
        
        print(f"Gráficos salvos em: {output_dir}")
    
    def export_to_dataframe(self) -> pd.DataFrame:
        """
        Exporta os resultados para um DataFrame pandas.
        
        Returns:
            DataFrame com todos os resultados
        """
        data = []
        
        for i in range(len(self.results["face_recognition"]["predictions"])):
            row = {
                "test_id": i + 1,
                "ground_truth": self.results["face_recognition"]["ground_truth"][i],
                "fr_prediction": self.results["face_recognition"]["predictions"][i],
                "fr_confidence": self.results["face_recognition"]["confidence_scores"][i],
                "fr_time": self.results["face_recognition"]["processing_times"][i],
                "df_prediction": self.results["deepface"]["predictions"][i],
                "df_confidence": self.results["deepface"]["confidence_scores"][i],
                "df_time": self.results["deepface"]["processing_times"][i]
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def save_metadata(self, deepface_config: Dict):
        """Salva metadados da comparação."""
        self.results["metadata"]["timestamp"] = datetime.now().isoformat()
        self.results["metadata"]["total_tests"] = len(self.results["face_recognition"]["predictions"])
        self.results["metadata"].update(deepface_config)
