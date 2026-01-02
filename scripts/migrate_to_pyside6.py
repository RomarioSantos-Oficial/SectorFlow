"""
Script para migrar de PySide2 para PySide6 no SectorFlow
"""

import os
import re

def migrate_file(filepath):
    """Migrate a single file from PySide6 to PySide6"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file contains PySide2
        if 'PySide2' not in content:
            return False
        
        # Replace PySide2 with PySide6
        new_content = content.replace('from PySide6', 'from PySide6')
        new_content = new_content.replace('import PySide6', 'import PySide6')
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Migrated: {filepath}")
        return True
        
    except Exception as e:
        print(f"✗ Error in {filepath}: {e}")
        return False

def migrate_directory(directory):
    """Migrate all Python files in directory"""
    migrated_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if migrate_file(filepath):
                    migrated_count += 1
    
    return migrated_count

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("SectorFlow - PySide2 to PySide6 Migration")
    print("=" * 60)
    
    count = migrate_directory(base_dir)
    
    print("=" * 60)
    print(f"Migration complete! {count} files migrated.")
    print("=" * 60)
