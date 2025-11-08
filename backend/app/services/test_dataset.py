"""
app/services/test_dataset.py
-----------------------------
Utilitários para criar e gerenciar datasets de teste para comparação de modelos.
"""
import os
import json
from typing import List, Dict, Tuple
from pathlib import Path
import shutil

class TestDataset:
    """
    Classe para gerenciar datasets de teste estruturados.
    
    Estrutura esperada:
    test_dataset/
        student_1/
            face_1.jpg
            face_2.jpg
            ...
        student_2/
            face_1.jpg
            ...
    """
    
    def __init__(self, dataset_path: str):
        """
        Inicializa o dataset.
        
        Args:
            dataset_path: Caminho para o diretório do dataset
        """
        self.dataset_path = Path(dataset_path)
        self.students = {}
        self.load_dataset()
    
    def load_dataset(self):
        """Carrega a estrutura do dataset."""
        if not self.dataset_path.exists():
            print(f"Diretório do dataset não encontrado: {self.dataset_path}")
            return
        
        for student_dir in self.dataset_path.iterdir():
            if student_dir.is_dir():
                student_id = student_dir.name
                images = [
                    str(img) for img in student_dir.glob("*")
                    if img.suffix.lower() in ['.jpg', '.jpeg', '.png']
                ]
                if images:
                    self.students[student_id] = images
        
        print(f"Dataset carregado: {len(self.students)} alunos, "
              f"{sum(len(imgs) for imgs in self.students.values())} imagens")
    
    def get_test_pairs(self, images_per_student: int = None) -> List[Tuple[str, str, int]]:
        """
        Gera pares de teste (imagem, ground_truth_id).
        
        Args:
            images_per_student: Número de imagens por aluno (None = todas)
        
        Returns:
            Lista de tuplas (image_path, student_name, student_numeric_id)
        """
        test_pairs = []
        student_mapping = {}
        
        for idx, (student_name, images) in enumerate(self.students.items()):
            student_numeric_id = idx + 1
            student_mapping[student_name] = student_numeric_id
            
            imgs_to_test = images[:images_per_student] if images_per_student else images
            
            for img_path in imgs_to_test:
                test_pairs.append((img_path, student_name, student_numeric_id))
        
        return test_pairs
    
    def split_train_test(self, test_ratio: float = 0.3) -> Tuple[Dict, Dict]:
        """
        Divide o dataset em treino e teste.
        
        Args:
            test_ratio: Proporção de imagens para teste
        
        Returns:
            Tupla (train_dict, test_dict) com mapeamento student_id -> images
        """
        import random
        
        train_data = {}
        test_data = {}
        
        for student_id, images in self.students.items():
            random.shuffle(images)
            split_point = int(len(images) * (1 - test_ratio))
            
            if split_point == 0:
                split_point = 1  # Garantir pelo menos 1 imagem de treino
            
            train_data[student_id] = images[:split_point]
            test_data[student_id] = images[split_point:]
        
        return train_data, test_data
    
    def create_sample_dataset(self, output_path: str, num_students: int = 5, 
                            images_per_student: int = 3):
        """
        Cria um dataset de exemplo para testes.
        
        Args:
            output_path: Onde criar o dataset
            num_students: Número de alunos
            images_per_student: Imagens por aluno
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Criar estrutura de diretórios
        for i in range(1, num_students + 1):
            student_dir = output_path / f"student_{i}"
            student_dir.mkdir(exist_ok=True)
        
        print(f"Estrutura de dataset criada em: {output_path}")
        print(f"Por favor, adicione {images_per_student} imagens em cada pasta student_X")
    
    def validate_dataset(self) -> Dict:
        """
        Valida o dataset e retorna estatísticas.
        
        Returns:
            Dicionário com estatísticas de validação
        """
        stats = {
            "total_students": len(self.students),
            "total_images": sum(len(imgs) for imgs in self.students.values()),
            "students_details": {}
        }
        
        for student_id, images in self.students.items():
            stats["students_details"][student_id] = {
                "num_images": len(images),
                "image_paths": images
            }
        
        # Verificar se há alunos com poucas imagens
        min_images = min(len(imgs) for imgs in self.students.values()) if self.students else 0
        max_images = max(len(imgs) for imgs in self.students.values()) if self.students else 0
        
        stats["min_images_per_student"] = min_images
        stats["max_images_per_student"] = max_images
        stats["avg_images_per_student"] = stats["total_images"] / stats["total_students"] if stats["total_students"] > 0 else 0
        
        # Avisos
        warnings = []
        if min_images < 2:
            warnings.append("Alguns alunos têm menos de 2 imagens - pode afetar a comparação")
        if max_images - min_images > 5:
            warnings.append("Grande variação no número de imagens entre alunos")
        
        stats["warnings"] = warnings
        
        return stats
    
    def export_metadata(self, output_file: str):
        """
        Exporta metadados do dataset para arquivo JSON.
        
        Args:
            output_file: Caminho do arquivo de saída
        """
        metadata = self.validate_dataset()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadados exportados para: {output_file}")

def prepare_comparison_dataset(
    source_dir: str,
    output_dir: str,
    train_ratio: float = 0.7
) -> Tuple[str, str]:
    """
    Prepara um dataset para comparação, dividindo em treino e teste.
    
    Args:
        source_dir: Diretório com imagens organizadas por aluno
        output_dir: Diretório de saída
        train_ratio: Proporção de dados para treino
    
    Returns:
        Tupla (train_path, test_path)
    """
    dataset = TestDataset(source_dir)
    train_data, test_data = dataset.split_train_test(test_ratio=1-train_ratio)
    
    # Criar estrutura de saída
    train_path = Path(output_dir) / "train"
    test_path = Path(output_dir) / "test"
    
    train_path.mkdir(parents=True, exist_ok=True)
    test_path.mkdir(parents=True, exist_ok=True)
    
    # Copiar imagens de treino
    for student_id, images in train_data.items():
        student_train_dir = train_path / student_id
        student_train_dir.mkdir(exist_ok=True)
        
        for img_path in images:
            shutil.copy2(img_path, student_train_dir / Path(img_path).name)
    
    # Copiar imagens de teste
    for student_id, images in test_data.items():
        student_test_dir = test_path / student_id
        student_test_dir.mkdir(exist_ok=True)
        
        for img_path in images:
            shutil.copy2(img_path, student_test_dir / Path(img_path).name)
    
    print(f"Dataset preparado:")
    print(f"  Treino: {train_path}")
    print(f"  Teste: {test_path}")
    
    return str(train_path), str(test_path)
