"""
resize_celebrity_dataset.py
---------------------------
Redimensiona todas as imagens do celebrity_dataset para 300x300 pixels.
Converte PNG para RGB para evitar problemas de transparência.
"""
import os
from pathlib import Path
from PIL import Image

def resize_images(dataset_path='celebrity_dataset', target_size=(300, 300)):
    """
    Redimensiona todas as imagens do dataset.
    
    Args:
        dataset_path: Caminho para o dataset
        target_size: Tamanho alvo (largura, altura)
    """
    base_path = Path(dataset_path)
    
    if not base_path.exists():
        print(f"✗ Pasta {dataset_path} não encontrada!")
        return
    
    # Buscar todas as pastas de celebridades
    celebrity_folders = [f for f in base_path.iterdir() if f.is_dir()]
    
    if not celebrity_folders:
        print("✗ Nenhuma pasta de celebridade encontrada!")
        return
    
    print(f"Redimensionando imagens para {target_size[0]}x{target_size[1]}...")
    print(f"Encontradas {len(celebrity_folders)} pastas de celebridades")
    
    total_images = 0
    resized_count = 0
    error_count = 0
    
    for celebrity_folder in celebrity_folders:
        # Buscar todas as imagens na pasta
        image_files = list(celebrity_folder.glob('*.jpg')) + \
                     list(celebrity_folder.glob('*.jpeg')) + \
                     list(celebrity_folder.glob('*.png')) + \
                     list(celebrity_folder.glob('*.JPG')) + \
                     list(celebrity_folder.glob('*.JPEG')) + \
                     list(celebrity_folder.glob('*.PNG'))
        
        if not image_files:
            continue
        
        celebrity_name = celebrity_folder.name
        print(f"\n  {celebrity_name}: {len(image_files)} imagens")
        
        for img_file in image_files:
            total_images += 1
            
            try:
                # Abrir imagem
                with Image.open(img_file) as img:
                    original_size = img.size
                    original_mode = img.mode
                    
                    # Converter para RGB se necessário (remove transparência)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Criar fundo branco
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        # Colar a imagem com alpha
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Redimensionar mantendo aspecto (thumbnail) ou forçando tamanho (resize)
                    # Usar resize para garantir exatamente 300x300
                    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                    
                    # Salvar como JPEG (substitui o arquivo original)
                    output_path = img_file.with_suffix('.jpg')
                    img_resized.save(output_path, 'JPEG', quality=95)
                    
                    # Se era PNG, remover arquivo original
                    if img_file.suffix.lower() == '.png' and output_path != img_file:
                        img_file.unlink()
                    
                    resized_count += 1
                    
                    if original_size[0] > target_size[0] or original_size[1] > target_size[1]:
                        print(f"    ✓ {img_file.name}: {original_size} → {target_size} ({original_mode} → RGB)")
                    
            except Exception as e:
                error_count += 1
                print(f"    ✗ Erro ao processar {img_file.name}: {e}")
    
    print(f"\n{'='*70}")
    print(f"RESUMO")
    print(f"{'='*70}")
    print(f"Total de imagens: {total_images}")
    print(f"Redimensionadas:  {resized_count} ✓")
    print(f"Erros:            {error_count} ✗")
    print(f"\n✓ Processo concluído!")
    print(f"✓ Todas as imagens agora têm {target_size[0]}x{target_size[1]} pixels")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        try:
            size = int(sys.argv[1])
            target = (size, size)
        except:
            print("Uso: python resize_celebrity_dataset.py [tamanho]")
            print("Exemplo: python resize_celebrity_dataset.py 300")
            sys.exit(1)
    else:
        target = (300, 300)
    
    print(f"Redimensionando para {target[0]}x{target[1]}...")
    resize_images(target_size=target)
