"""
Script para criar executável do SectorFlow usando PyInstaller

Uso:
    python scripts/build_exe.py

Requisitos:
    pip install pyinstaller
"""

import os
import sys
import shutil
from pathlib import Path

# Adicionar diretório pai ao path para importar módulos
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from validadorers.const_app import APP_NAME, VERSION

def build_executable():
    """Criar executável com PyInstaller"""
    
    print("=" * 60)
    print(f"  Criando executavel: {APP_NAME} v{VERSION}")
    print("=" * 60)
    
    # Limpar builds anteriores
    dist_dir = parent_dir / "dist"
    build_dir = parent_dir / "build"
    
    if dist_dir.exists():
        print("\nRemovendo build anterior...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Configurar PyInstaller
    icon_path = parent_dir / "images" / "icon" / "Logo.png"
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--name", "SectorFlow",
        "--onefile",  # Executável único
        "--windowed",  # Sem console
        "--icon", str(icon_path) if icon_path.exists() else "NONE",
        
        # Adicionar dados necessários
        "--add-data", f"{parent_dir}/images;images",
        "--add-data", f"{parent_dir}/settings;settings",
        "--add-data", f"{parent_dir}/brandlogo;brandlogo",
        
        # Adicionar módulos hidden
        "--hidden-import", "pyRfactor2SharedMemory",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtMultimedia",
        
        # Excluir módulos desnecessários
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",
        "--exclude-module", "PIL",
        
        # Arquivo principal
        str(parent_dir / "run.py"),
    ]
    
    print("\nIniciando build...")
    print(f"Comando: {' '.join(cmd)}\n")
    
    # Executar PyInstaller
    import subprocess
    result = subprocess.run(cmd, cwd=str(parent_dir))
    
    if result.returncode == 0:
        # Mover executável para a raiz
        exe_dist = dist_dir / "SectorFlow.exe"
        exe_root = parent_dir / "SectorFlow.exe"
        
        if exe_dist.exists():
            if exe_root.exists():
                exe_root.unlink()  # Remover executável antigo
            shutil.move(str(exe_dist), str(exe_root))
            print("\nMovendo executavel para a raiz...")
        
        print("\n" + "=" * 60)
        print("OK Executavel criado com sucesso!")
        print("=" * 60)
        print(f"\nLocalizacao: {exe_root}")
        print("\nPara executar:")
        print("   .\\SectorFlow.exe")
    else:
        print("\nERRO ao criar executavel!")
        sys.exit(1)

if __name__ == "__main__":
    # Configurar encoding UTF-8 para o console Windows
    import sys
    if sys.platform == "win32":
        import os
        os.system("chcp 65001 >nul 2>&1")
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print(f"OK PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("ERRO PyInstaller nao esta instalado!")
        print("\nInstale com: pip install pyinstaller")
        sys.exit(1)
    
    build_executable()
