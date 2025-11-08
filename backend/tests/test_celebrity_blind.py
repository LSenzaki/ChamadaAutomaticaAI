"""
test_celebrity_blind.py
-----------------------
Teste cego: cadastra com test_dataset e tenta reconhecer celebridades misturadas.
Celebridades podem ser conhecidas (no treino) ou desconhecidas.
"""
import os
import sys
import time
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile

# Adicionar o diretório backend ao path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services import face_service
from app.services.deepface_service import get_deepface_encoding, recognize_face_deepface
from app.services.test_dataset import TestDataset

def criar_upload_file(file_path):
    """Cria um objeto UploadFile a partir de um caminho de arquivo."""
    with open(file_path, 'rb') as f:
        content = f.read()
    
    return UploadFile(
        filename=os.path.basename(file_path),
        file=BytesIO(content)
    )

def teste_celebrity_blind(train_dataset_path, celebrity_dataset_path, deepface_model="Facenet512"):
    """
    Teste cego com celebridades misturadas.
    """
    print("=" * 80)
    print("TESTE CEGO COM CELEBRIDADES - Face Recognition vs DeepFace")
    print("=" * 80)
    
    # Carregar datasets
    print(f"\n[1/4] Carregando datasets...")
    print(f"  Training: {train_dataset_path}")
    print(f"  Testing:  {celebrity_dataset_path}")
    
    train_dataset = TestDataset(train_dataset_path)
    celebrity_dataset = TestDataset(celebrity_dataset_path)
    
    print(f"✓ Training: {len(train_dataset.students)} pessoas")
    print(f"✓ Celebrity Test: {len(celebrity_dataset.students)} pessoas")
    
    # Cadastrar faces
    print(f"\n[2/4] Cadastrando faces do training dataset...")
    known_faces_fr = []
    known_faces_df = []
    student_mapping = {}
    known_names = set()
    
    for idx, (student_name, images) in enumerate(train_dataset.students.items()):
        if not images:
            continue
            
        student_id = idx + 1
        student_mapping[student_id] = student_name
        known_names.add(student_name.lower())
        train_image = images[0]
        
        try:
            # Face Recognition
            upload_file_fr = criar_upload_file(train_image)
            fr_encoding = face_service.get_face_encoding(upload_file_fr)
            if fr_encoding is not None:
                known_faces_fr.append({'student_id': student_id, 'vector': fr_encoding.tolist()})
            
            # DeepFace
            upload_file_df = criar_upload_file(train_image)
            df_encoding = get_deepface_encoding(upload_file_df, model_name=deepface_model)
            if df_encoding is not None:
                known_faces_df.append({'student_id': student_id, 'vector': df_encoding.tolist()})
        except Exception as e:
            print(f"  ✗ {student_name}: {e}")
    
    print(f"✓ {len(known_faces_fr)} faces cadastradas (FR), {len(known_faces_df)} (DF)")
    print(f"✓ Pessoas conhecidas: {', '.join(sorted(known_names))}")
    
    # Função para normalizar nomes (remover acentos, underscores, espaços, apostrofos)
    def normalize_name(name):
        import unicodedata
        # Remover acentos
        name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
        # Lowercase, remover underscores, espaços, apostrofos
        name = name.lower().replace('_', '').replace(' ', '').replace("'", '').replace('-', '')
        return name
    
    # Criar mapeamento normalizado
    normalized_known = {}
    for sid, sname in student_mapping.items():
        norm_name = normalize_name(sname)
        normalized_known[norm_name] = (sid, sname)
    
    # Testar com celebrity dataset
    print(f"\n[3/4] Testando reconhecimento no celebrity dataset...")
    
    results = {
        'face_recognition': {
            'predictions': [],
            'confidences': [],
            'times': [],
            'known_correct': 0,
            'known_wrong': 0,
            'known_not_recognized': 0,
            'unknown_recognized': 0,
            'unknown_not_recognized': 0,
            'total_known': 0,
            'total_unknown': 0
        },
        'deepface': {
            'predictions': [],
            'confidences': [],
            'times': [],
            'known_correct': 0,
            'known_wrong': 0,
            'known_not_recognized': 0,
            'unknown_recognized': 0,
            'unknown_not_recognized': 0,
            'total_known': 0,
            'total_unknown': 0
        }
    }
    
    test_count = 0
    
    for celebrity_name, images in celebrity_dataset.students.items():
        # Normalizar nome para comparação
        norm_celebrity = normalize_name(celebrity_name)
        is_known = norm_celebrity in normalized_known
        
        if is_known:
            true_id, original_name = normalized_known[norm_celebrity]
        else:
            true_id = None
            original_name = None
        
        for img_path in images:
            test_count += 1
            status_text = f"CONHECIDO como {original_name}" if is_known else "DESCONHECIDO"
            print(f"\n  Teste {test_count}: {celebrity_name} ({status_text})")
            
            # Face Recognition
            try:
                upload_file_fr = criar_upload_file(img_path)
                start_time = time.time()
                fr_encoding = face_service.get_face_encoding(upload_file_fr)
                fr_pred_id = None
                fr_confidence = 0.0
                
                if fr_encoding is not None:
                    fr_result = face_service.recognize_face(fr_encoding, known_faces_fr)
                    if fr_result:
                        fr_pred_id, fr_confidence = fr_result
                
                fr_time = time.time() - start_time
                
                results['face_recognition']['predictions'].append(fr_pred_id)
                results['face_recognition']['confidences'].append(fr_confidence)
                results['face_recognition']['times'].append(fr_time)
                
                if is_known:
                    results['face_recognition']['total_known'] += 1
                    if fr_pred_id == true_id:
                        results['face_recognition']['known_correct'] += 1
                        status_fr = f"✓ Correto ID={fr_pred_id}"
                    elif fr_pred_id is None:
                        results['face_recognition']['known_not_recognized'] += 1
                        status_fr = "✗ Não reconhecido"
                    else:
                        results['face_recognition']['known_wrong'] += 1
                        predicted_name = student_mapping.get(fr_pred_id, 'Unknown')
                        status_fr = f"✗ Errado: {predicted_name}"
                else:
                    results['face_recognition']['total_unknown'] += 1
                    if fr_pred_id is None:
                        results['face_recognition']['unknown_not_recognized'] += 1
                        status_fr = "✓ Corretamente rejeitado"
                    else:
                        results['face_recognition']['unknown_recognized'] += 1
                        predicted_name = student_mapping.get(fr_pred_id, 'Unknown')
                        status_fr = f"✗ Falso Positivo: {predicted_name}"
                
                print(f"    FR: {status_fr} (conf={fr_confidence:.1f}%, tempo={fr_time:.3f}s)")
                
            except Exception as e:
                print(f"    FR: ✗ Erro: {e}")
                results['face_recognition']['predictions'].append(None)
                results['face_recognition']['confidences'].append(0.0)
                results['face_recognition']['times'].append(0.0)
                if is_known:
                    results['face_recognition']['total_known'] += 1
                    results['face_recognition']['known_not_recognized'] += 1
                else:
                    results['face_recognition']['total_unknown'] += 1
                    results['face_recognition']['unknown_not_recognized'] += 1
            
            # DeepFace
            try:
                upload_file_df = criar_upload_file(img_path)
                start_time = time.time()
                df_encoding = get_deepface_encoding(upload_file_df, model_name=deepface_model)
                df_pred_id = None
                df_confidence = 0.0
                
                if df_encoding is not None:
                    df_result = recognize_face_deepface(
                        df_encoding, known_faces_df,
                        model_name=deepface_model,
                        distance_metric="cosine"
                    )
                    if df_result:
                        df_pred_id, df_confidence, _ = df_result
                
                df_time = time.time() - start_time
                
                results['deepface']['predictions'].append(df_pred_id)
                results['deepface']['confidences'].append(df_confidence)
                results['deepface']['times'].append(df_time)
                
                if is_known:
                    results['deepface']['total_known'] += 1
                    if df_pred_id == true_id:
                        results['deepface']['known_correct'] += 1
                        status_df = f"✓ Correto ID={df_pred_id}"
                    elif df_pred_id is None:
                        results['deepface']['known_not_recognized'] += 1
                        status_df = "✗ Não reconhecido"
                    else:
                        results['deepface']['known_wrong'] += 1
                        predicted_name = student_mapping.get(df_pred_id, 'Unknown')
                        status_df = f"✗ Errado: {predicted_name}"
                else:
                    results['deepface']['total_unknown'] += 1
                    if df_pred_id is None:
                        results['deepface']['unknown_not_recognized'] += 1
                        status_df = "✓ Corretamente rejeitado"
                    else:
                        results['deepface']['unknown_recognized'] += 1
                        predicted_name = student_mapping.get(df_pred_id, 'Unknown')
                        status_df = f"✗ Falso Positivo: {predicted_name}"
                
                print(f"    DF: {status_df} (conf={df_confidence:.1f}%, tempo={df_time:.3f}s)")
                
            except Exception as e:
                print(f"    DF: ✗ Erro: {e}")
                results['deepface']['predictions'].append(None)
                results['deepface']['confidences'].append(0.0)
                results['deepface']['times'].append(0.0)
                if is_known:
                    results['deepface']['total_known'] += 1
                    results['deepface']['known_not_recognized'] += 1
                else:
                    results['deepface']['total_unknown'] += 1
                    results['deepface']['unknown_not_recognized'] += 1
    
    # Calcular métricas
    print(f"\n[4/4] Calculando métricas finais...")
    
    print("\n" + "=" * 80)
    print("RESULTADOS FINAIS")
    print("=" * 80)
    
    for model_name in ['face_recognition', 'deepface']:
        r = results[model_name]
        
        # True Positives: conhecidos reconhecidos corretamente
        tp = r['known_correct']
        # False Negatives: conhecidos não reconhecidos ou reconhecidos errado
        fn = r['known_not_recognized'] + r['known_wrong']
        # True Negatives: desconhecidos corretamente rejeitados
        tn = r['unknown_not_recognized']
        # False Positives: desconhecidos incorretamente reconhecidos
        fp = r['unknown_recognized']
        
        total = tp + fn + tn + fp
        
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        avg_confidence = sum(r['confidences']) / len(r['confidences']) if r['confidences'] else 0
        avg_time = sum(r['times']) / len(r['times']) if r['times'] else 0
        
        print(f"\n{'FACE RECOGNITION' if model_name == 'face_recognition' else 'DEEPFACE (' + deepface_model + ')'}:")
        print(f"  --- Matriz de Confusão ---")
        print(f"  True Positives (TP):     {tp} / {r['total_known']} conhecidos")
        print(f"  False Negatives (FN):    {fn}")
        print(f"    - Não reconhecidos:    {r['known_not_recognized']}")
        print(f"    - Reconhecidos errado: {r['known_wrong']}")
        print(f"  True Negatives (TN):     {tn} / {r['total_unknown']} desconhecidos")
        print(f"  False Positives (FP):    {fp}")
        print(f"  --- Métricas ---")
        print(f"  Accuracy:                {accuracy:.3f} ({accuracy*100:.1f}%)")
        print(f"  Precision:               {precision:.3f}")
        print(f"  Recall (Sensitivity):    {recall:.3f}")
        print(f"  Specificity:             {specificity:.3f}")
        print(f"  F1 Score:                {f1_score:.3f}")
        print(f"  --- Desempenho ---")
        print(f"  Confiança Média:         {avg_confidence:.1f}%")
        print(f"  Tempo Médio:             {avg_time:.4f}s")
    
    # Comparação
    print("\n" + "=" * 80)
    print("COMPARAÇÃO")
    print("=" * 80)
    
    fr = results['face_recognition']
    df = results['deepface']
    
    fr_tp = fr['known_correct']
    fr_fn = fr['known_not_recognized'] + fr['known_wrong']
    fr_tn = fr['unknown_not_recognized']
    fr_fp = fr['unknown_recognized']
    fr_total = fr_tp + fr_fn + fr_tn + fr_fp
    fr_accuracy = (fr_tp + fr_tn) / fr_total if fr_total > 0 else 0
    fr_precision = fr_tp / (fr_tp + fr_fp) if (fr_tp + fr_fp) > 0 else 0
    fr_recall = fr_tp / (fr_tp + fr_fn) if (fr_tp + fr_fn) > 0 else 0
    fr_f1 = 2 * (fr_precision * fr_recall) / (fr_precision + fr_recall) if (fr_precision + fr_recall) > 0 else 0
    
    df_tp = df['known_correct']
    df_fn = df['known_not_recognized'] + df['known_wrong']
    df_tn = df['unknown_not_recognized']
    df_fp = df['unknown_recognized']
    df_total = df_tp + df_fn + df_tn + df_fp
    df_accuracy = (df_tp + df_tn) / df_total if df_total > 0 else 0
    df_precision = df_tp / (df_tp + df_fp) if (df_tp + df_fp) > 0 else 0
    df_recall = df_tp / (df_tp + df_fn) if (df_tp + df_fn) > 0 else 0
    df_f1 = 2 * (df_precision * df_recall) / (df_precision + df_recall) if (df_precision + df_recall) > 0 else 0
    
    print(f"  Accuracy:    FR {fr_accuracy:.3f} vs DF {df_accuracy:.3f} → {'FR VENCE' if fr_accuracy > df_accuracy else 'DF VENCE' if df_accuracy > fr_accuracy else 'EMPATE'}")
    print(f"  Precision:   FR {fr_precision:.3f} vs DF {df_precision:.3f} → {'FR VENCE' if fr_precision > df_precision else 'DF VENCE' if df_precision > fr_precision else 'EMPATE'}")
    print(f"  Recall:      FR {fr_recall:.3f} vs DF {df_recall:.3f} → {'FR VENCE' if fr_recall > df_recall else 'DF VENCE' if df_recall > fr_recall else 'EMPATE'}")
    print(f"  F1 Score:    FR {fr_f1:.3f} vs DF {df_f1:.3f} → {'FR VENCE' if fr_f1 > df_f1 else 'DF VENCE' if df_f1 > fr_f1 else 'EMPATE'}")
    
    print("\n" + "=" * 80)
    if fr_accuracy > df_accuracy and fr_f1 > df_f1:
        print("🏆 VENCEDOR: FACE RECOGNITION")
        print(f"   Melhor accuracy ({fr_accuracy:.1%} vs {df_accuracy:.1%})")
        print(f"   Melhor F1 Score ({fr_f1:.3f} vs {df_f1:.3f})")
    elif df_accuracy > fr_accuracy and df_f1 > fr_f1:
        print("🏆 VENCEDOR: DEEPFACE")
        print(f"   Melhor accuracy ({df_accuracy:.1%} vs {fr_accuracy:.1%})")
        print(f"   Melhor F1 Score ({df_f1:.3f} vs {fr_f1:.3f})")
    else:
        print("⚖️  RESULTADO MISTO - Analisar métricas específicas")
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\nUso:")
        print("  python test_celebrity_blind.py <train_dataset> <celebrity_dataset> [model]")
        print("\nExemplo:")
        print("  python test_celebrity_blind.py test_dataset celebrity_dataset")
        print("  python test_celebrity_blind.py test_dataset celebrity_dataset Facenet512")
        sys.exit(1)
    
    train_path = sys.argv[1]
    celebrity_path = sys.argv[2]
    model = sys.argv[3] if len(sys.argv) > 3 else "Facenet512"
    
    for path in [train_path, celebrity_path]:
        if not Path(path).exists():
            print(f"\n✗ Erro: Dataset não encontrado em {path}")
            sys.exit(1)
    
    teste_celebrity_blind(train_path, celebrity_path, model)
