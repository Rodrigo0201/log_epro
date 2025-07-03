#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Limpar Diretório Temporário
======================================
"""

import os
import shutil

def clean_temp_directory():
    """Limpa o diretório temporário."""
    temp_dir = "temp_unzipped_logs"
    
    if os.path.exists(temp_dir):
        print(f"🧹 Limpando diretório: {temp_dir}")
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        print(f"✅ Diretório {temp_dir} limpo e recriado")
    else:
        print(f"📁 Diretório {temp_dir} não existe, criando...")
        os.makedirs(temp_dir)
        print(f"✅ Diretório {temp_dir} criado")

if __name__ == "__main__":
    clean_temp_directory() 