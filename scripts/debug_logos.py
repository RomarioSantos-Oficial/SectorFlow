
import os
import sys
from PySide6.QtGui import QPixmap, QGuiApplication
from PySide6.QtCore import Qt

# Initialize QGuiApplication (needed for QPixmap)
app = QGuiApplication(sys.argv)

def test_logo_loading():
    print("--- Starting Logo Debug ---")
    
    # 1. Check Paths
    cwd = os.getcwd()
    print(f"Current Working Directory: {cwd}")
    
    possible_paths = [
        "images/logo marca/",
        os.path.join(cwd, "images", "logo marca"),
        "brandlogo/"
    ]
    
    valid_path = None
    available_logos = {}

    for path in possible_paths:
        exists = os.path.isdir(path)
        print(f"Checking path: '{path}' -> Exists: {exists}")
        if exists:
            # Check for files
            has_images = False
            temp_logos = {}
            for entry in os.scandir(path):
                if entry.is_file():
                    name, ext = os.path.splitext(entry.name)
                    if ext.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                        temp_logos[name.lower()] = (name, ext)
                        has_images = True
            
            if has_images:
                valid_path = path
                available_logos = temp_logos
                print(f"  -> Found {len(temp_logos)} images in this path. Selected.")
                break
            else:
                print("  -> Path exists but has no images. Skipping.")
            
    if not valid_path:
        print("CRITICAL: No valid logo directory found!")
        return

    print(f"Using path: {valid_path}")
    print(f"Available logos: {list(available_logos.keys())}")
    
    # 3. Test Matching Logic
    test_vehicles = ["Ferrari 488 GT3", "Porsche 911 RSR", "Toyota GR010", "Unknown Car"]
    
    print("\n--- Testing Matching Logic ---")
    for veh_name in test_vehicles:
        print(f"Vehicle: '{veh_name}'")
        
        logo_name = veh_name
        logo_ext = ".png"
        found = False
        
        # Logic from standings_hybrid.py
        if veh_name.lower() in available_logos:
            logo_name, logo_ext = available_logos[veh_name.lower()]
            found = True
            print(f"  -> Exact match found: {logo_name}{logo_ext}")
        else:
            # Sort by length desc
            for key in sorted(available_logos.keys(), key=len, reverse=True):
                if key in veh_name.lower():
                    logo_name, logo_ext = available_logos[key]
                    found = True
                    print(f"  -> Substring match found: '{key}' in '{veh_name.lower()}' -> {logo_name}{logo_ext}")
                    break
        
        if not found:
            print("  -> No match found.")
            continue

        # 4. Test Loading
        full_path = os.path.join(valid_path, f"{logo_name}{logo_ext}")
        pixmap = QPixmap(full_path)
        if pixmap.isNull():
            print(f"  -> FAILED to load QPixmap from: {full_path}")
        else:
            print(f"  -> SUCCESS loading QPixmap: {pixmap.width()}x{pixmap.height()}")

if __name__ == "__main__":
    test_logo_loading()
