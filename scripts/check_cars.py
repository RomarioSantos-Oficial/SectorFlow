import sys
import os
import time
import mmap
import ctypes

# Add the current directory to sys.path to find pyRfactor2SharedMemory
sys.path.append(os.getcwd())

try:
    from pyRfactor2SharedMemory.rF2data import SimInfo
except ImportError as e:
    print(f"Could not import pyRfactor2SharedMemory: {e}")
    print(f"Current path: {sys.path}")
    sys.exit(1)

def main():
    print("Connecting to Shared Memory...")
    
    try:
        info = SimInfo()
        
        # Wait for connection
        print("Waiting for game data (Ctrl+C to stop)...")
        
        while True:
            # Check if we have vehicles
            num_vehicles = info.Rf2Scor.mScoringInfo.mNumVehicles
            
            if num_vehicles == 0:
                print("Connected, but no vehicles found. (In main menu?)")
                time.sleep(2)
                continue

            print(f"\nFound {num_vehicles} vehicles:")
            print(f"{'ID':<5} | {'Driver':<20} | {'Class':<15} | {'Vehicle Name'}")
            print("-" * 80)

            for i in range(num_vehicles):
                veh = info.Rf2Scor.mVehicles[i]
                # Decode bytes to string, handling potential encoding issues
                try:
                    driver = bytes(veh.mDriverName).decode('utf-8', errors='replace').strip().strip('\x00')
                    v_class = bytes(veh.mVehicleClass).decode('utf-8', errors='replace').strip().strip('\x00')
                    v_name = bytes(veh.mVehicleName).decode('utf-8', errors='replace').strip().strip('\x00')
                    
                    print(f"{i:<5} | {driver:<20} | {v_class:<15} | {v_name}")
                except Exception as e:
                    print(f"Error decoding vehicle {i}: {e}")

            print("\nCheck the 'Vehicle Name' column. These are the strings we are matching against your logo filenames.")
            print("Your logo files must match a substring of 'Vehicle Name'.")
            print("-" * 80)
            break

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
