
import sys

# Mocking the logic from standings_hybrid.py to test it in isolation
class StandingsLogicTester:
    def __init__(self, vehicles_data):
        self.vehicles_data = vehicles_data

    def get_filtered_order(self):
        """
        Logic copied from StandingsHybrid.get_filtered_order
        Adapted to read from self.vehicles_data instead of api/minfo
        """
        veh_total = len(self.vehicles_data)
        if veh_total < 1:
            return []

        # Group vehicles by class
        classes = {} # name -> list of (place, veh_idx, is_player)
        player_class = None
        
        for i, v in enumerate(self.vehicles_data):
            cls = v['class']
            place = v['place']
            is_player = v['is_player']
            
            if cls not in classes:
                classes[cls] = []
            classes[cls].append((place, i, is_player))
            
            if is_player:
                player_class = cls

        # Sort classes by leader position (overall place)
        sorted_classes = sorted(classes.items(), key=lambda x: min(v[0] for v in x[1]))
        
        # Reorder: Move player class to the BOTTOM (End of list)
        if player_class:
            # Remove player class tuple
            p_cls_tuple = next((item for item in sorted_classes if item[0] == player_class), None)
            if p_cls_tuple:
                sorted_classes.remove(p_cls_tuple)
                sorted_classes.append(p_cls_tuple)

        # Determine limits based on class count
        num_classes = len(sorted_classes)
        limit_player = 9
        limit_others = 2
        
        if num_classes == 1:
            limit_player = 11
        elif num_classes == 2:
            limit_others = 5
            limit_player = 9
        else: # 3 or more
            limit_others = 2
            limit_player = 9

        display_items = []
        
        for cls_name, vehicles in sorted_classes:
            # Add Class Header
            display_items.append(f"--- {cls_name} ---")
            
            # Sort vehicles in class by place
            vehicles.sort(key=lambda x: x[0])
            
            if cls_name == player_class:
                # Player class logic
                limit = limit_player
                
                # Find player index in this list
                p_idx = -1
                for idx, v in enumerate(vehicles):
                    if v[2]: # is_player
                        p_idx = idx
                        break
                
                if p_idx != -1:
                    # Always include leader (index 0)
                    indices = [0]
                    slots_remaining = limit - 1
                    
                    if slots_remaining > 0:
                        # Calculate window around player
                        # We want to center the player in the remaining slots
                        half_window = slots_remaining // 2
                        
                        start = p_idx - half_window
                        end = p_idx + half_window + (slots_remaining % 2) # Add remainder to end
                        
                        # Adjust bounds
                        if start <= 0: # Avoid index 0 (Leader)
                            diff = 1 - start
                            start = 1
                            end += diff
                        
                        if end >= len(vehicles):
                            diff = end - len(vehicles)
                            end = len(vehicles)
                            start = max(1, start - diff) # Pull back start if end hits wall
                        
                        # Add window indices
                        for i in range(start, end):
                            if i not in indices and i < len(vehicles):
                                indices.append(i)
                            
                    # Add to display list
                    # Sort indices to keep order
                    indices.sort()
                    for i in indices:
                        display_items.append(vehicles[i][1])
                else:
                    # Fallback if player not found
                    for v in vehicles[:limit]:
                        display_items.append(v[1])
            else:
                # Other class logic: Top N
                for v in vehicles[:limit_others]:
                    display_items.append(v[1])
        
        return display_items

def create_vehicle(idx, cls, place, is_player=False):
    return {'id': idx, 'class': cls, 'place': place, 'is_player': is_player}

def run_tests():
    print("=== TESTE DE LÓGICA DE EXIBIÇÃO ===")

    # --- TESTE 1: Apenas 1 Categoria (GT3) ---
    print("\n[CENÁRIO 1] Apenas 1 Categoria (GT3)")
    print("Esperado: 11 Carros da classe do jogador")
    
    vehs = []
    # Create 20 GT3 cars
    for i in range(20):
        is_p = (i == 10) # Player is P11 (index 10)
        vehs.append(create_vehicle(i, "GT3", i+1, is_p))
    
    tester = StandingsLogicTester(vehs)
    result = tester.get_filtered_order()
    
    count_gt3 = 0
    for item in result:
        if isinstance(item, str):
            print(f"HEADER: {item}")
        else:
            v = vehs[item]
            marker = " [PLAYER]" if v['is_player'] else ""
            print(f"  P{v['place']:02d} - {v['class']}{marker}")
            if v['class'] == "GT3": count_gt3 += 1
            
    print(f"Total GT3 mostrados: {count_gt3}")
    if count_gt3 == 11: print("✅ SUCESSO: Mostrou 11 carros.")
    else: print(f"❌ FALHA: Mostrou {count_gt3} carros.")


    # --- TESTE 2: 2 Categorias (Hypercar + GT3) ---
    print("\n[CENÁRIO 2] 2 Categorias (Hypercar + GT3)")
    print("Esperado: 5 Hypercars (Outra) + 9 GT3 (Player)")
    
    vehs = []
    # 10 Hypercars (P1-P10)
    for i in range(10):
        vehs.append(create_vehicle(i, "Hypercar", i+1, False))
    # 15 GT3s (P11-P25), Player is P18
    for i in range(15):
        is_p = (i == 7) # 7th GT3, P18 overall
        vehs.append(create_vehicle(10+i, "GT3", 11+i, is_p))
        
    tester = StandingsLogicTester(vehs)
    result = tester.get_filtered_order()
    
    count_hyper = 0
    count_gt3 = 0
    for item in result:
        if isinstance(item, str):
            print(f"HEADER: {item}")
        else:
            # Find vehicle in list by index (item is index in original list)
            # Since we constructed list sequentially, item is index
            v = vehs[item]
            marker = " [PLAYER]" if v['is_player'] else ""
            print(f"  P{v['place']:02d} - {v['class']}{marker}")
            if v['class'] == "Hypercar": count_hyper += 1
            if v['class'] == "GT3": count_gt3 += 1

    print(f"Total Hypercar: {count_hyper} (Esperado: 5)")
    print(f"Total GT3: {count_gt3} (Esperado: 9)")
    
    if count_hyper == 5 and count_gt3 == 9: print("✅ SUCESSO.")
    else: print("❌ FALHA.")


    # --- TESTE 3: 3 Categorias (Hypercar + LMP2 + GT3) ---
    print("\n[CENÁRIO 3] 3 Categorias (Hypercar + LMP2 + GT3)")
    print("Esperado: 2 Hypercar + 2 LMP2 + 9 GT3 (Player)")
    
    vehs = []
    # 5 Hypercars
    for i in range(5):
        vehs.append(create_vehicle(len(vehs), "Hypercar", len(vehs)+1, False))
    # 5 LMP2s
    for i in range(5):
        vehs.append(create_vehicle(len(vehs), "LMP2", len(vehs)+1, False))
    # 15 GT3s, Player in middle
    for i in range(15):
        is_p = (i == 7)
        vehs.append(create_vehicle(len(vehs), "GT3", len(vehs)+1, is_p))
        
    tester = StandingsLogicTester(vehs)
    result = tester.get_filtered_order()
    
    counts = {"Hypercar": 0, "LMP2": 0, "GT3": 0}
    
    for item in result:
        if isinstance(item, str):
            print(f"HEADER: {item}")
        else:
            v = vehs[item]
            marker = " [PLAYER]" if v['is_player'] else ""
            print(f"  P{v['place']:02d} - {v['class']}{marker}")
            counts[v['class']] += 1
            
    print(f"Hypercar: {counts['Hypercar']} (Esperado: 2)")
    print(f"LMP2: {counts['LMP2']} (Esperado: 2)")
    print(f"GT3: {counts['GT3']} (Esperado: 9)")
    
    if counts['Hypercar'] == 2 and counts['LMP2'] == 2 and counts['GT3'] == 9:
        print("✅ SUCESSO.")
    else:
        print("❌ FALHA.")

if __name__ == "__main__":
    run_tests()
