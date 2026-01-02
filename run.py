#!/usr/bin/env python3
"""
SectorFlow - Telemetry Overlay Application

This is the main entry point for the application.
Run this file to start the telemetry overlay.

Based on TinyPedal project.
"""

import sys
import logging
from pathlib import Path

# Configurar logging antes de tudo
# Criar diretório logs se não existir
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "sectorflow.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("SectorFlow - Starting application")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        logger.info("=" * 60)
        
        from validadorers.ui.app import main
        exit_code = main()
        
        logger.info("=" * 60)
        logger.info(f"SectorFlow exited with code: {exit_code or 0}")
        logger.info("=" * 60)
        sys.exit(exit_code or 0)
        
    except ImportError as e:
        logger.error(f"Import error: {e}", exc_info=True)
        print("\n" + "=" * 60)
        print("❌ ERRO: Dependências não instaladas")
        print("=" * 60)
        print("Execute o seguinte comando para instalar:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        input("Pressione ENTER para sair...")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print("\n" + "=" * 60)
        print(f"❌ ERRO CRÍTICO: {e}")
        print("=" * 60)
        print(f"Verifique o arquivo '{log_file}' para mais detalhes")
        print("=" * 60)
        input("Pressione ENTER para sair...")
        sys.exit(1)

