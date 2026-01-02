import os

# Mock class to simulate the widget
class MockWidget:
    def __init__(self):
        self.available_logos = {}
        self.logo_search_path = ""
        self.scan_logos()

    def scan_logos(self):
        # Simulate the scanning logic from the widget
        search_paths = [
            os.path.join(os.getcwd(), "images", "logo marca"),
            os.path.join(os.getcwd(), "brandlogo"),
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                print(f"Scanning: {path}")
                temp_logos = {}
                has_images = False
                with os.scandir(path) as entries:
                    for entry in entries:
                        if entry.is_file():
                            name, ext = os.path.splitext(entry.name)
                            if ext.lower() in ['.png', '.jpg', '.jpeg', '.svg']:
                                temp_logos[name.lower()] = (name, ext)
                                has_images = True
                
                if has_images:
                    self.logo_search_path = path
                    self.available_logos = temp_logos
                    print(f"Found {len(temp_logos)} logos.")
                    break

    def resolve_logo(self, veh_name, veh_class, team_name=""):
        """
        Standalone version of update_brand_logo logic
        Returns: (Logo Filename, Status)
        """
        # Smart Mapping Logic
        mapped_brand = None
        v_name_lower = veh_name.lower()
        v_class_lower = veh_class.lower()
        t_name_lower = team_name.lower() if team_name else ""
        
        # Combine name and team for searching
        search_text = f"{v_name_lower} {t_name_lower}"

        # 1. LMP2 - Almost always Oreca in LMU
        if "lmp2" in v_class_lower:
            mapped_brand = "Oreca"

        # 1.1 LMP3 Mappings
        elif "lmp3" in v_class_lower or "p3" in v_class_lower:
            # Check Ginetta and Duqueine FIRST to avoid false positives with "P325" in Ligier check
            if any(x in search_text for x in ["ginetta", "g61", "lt-p3", "lt-p325", "dkr engineering"]):
                mapped_brand = "Ginetta"
            elif any(x in search_text for x in ["duqueine", "d08", "wtm", "rinaldi"]):
                mapped_brand = "Duqueine"
            elif any(x in search_text for x in ["ligier", "js p3", "jsp3", "js p325", "cool racing", "rlr", "virage", "inter europol", "nielsen", "united", "cd sport", "graff", "24-7", "racing spirit", "mv2s", "ultimate", "eurointernational", "clx", "m racing"]):
                mapped_brand = "Ligier"
            
            # Fallback if name doesn't contain manufacturer
            if not mapped_brand:
                # Common LMP3 teams/models
                if "js p3" in search_text: mapped_brand = "Ligier"
        
        # 2. GT3 / LMGT3 Mappings
        elif "gt3" in v_class_lower:
            # Check explicit manufacturer names first
            if "ferrari" in v_name_lower: mapped_brand = "Ferrari"
            elif "porsche" in v_name_lower: mapped_brand = "Porsche"
            elif "lamborghini" in v_name_lower: mapped_brand = "Lamborghini"
            elif "bmw" in v_name_lower: mapped_brand = "BMW"
            elif "aston" in v_name_lower: mapped_brand = "Aston Martin"
            elif "corvette" in v_name_lower: mapped_brand = "Corvette"
            elif "ford" in v_name_lower or "mustang" in v_name_lower: mapped_brand = "Ford"
            elif "lexus" in v_name_lower: mapped_brand = "Lexus"
            elif "mclaren" in v_name_lower: mapped_brand = "mclaren"
            elif "mercedes" in v_name_lower or "amg" in v_name_lower: mapped_brand = "mercedes"
            
            # Team Name Mappings (if manufacturer not found)
            if not mapped_brand:
                # Specific Year/Team Logic
                if "iron lynx" in search_text:
                    if "2025" in search_text or "mercedes" in search_text or "amg" in search_text:
                        mapped_brand = "mercedes"
                    else:
                        mapped_brand = "Lamborghini"
                elif "iron dames" in search_text:
                    if "2025" in search_text or "porsche" in search_text:
                        mapped_brand = "Porsche"
                    else:
                        mapped_brand = "Lamborghini"
                elif "proton" in search_text:
                    # Proton: Porsche (Hypercar/ELMS) vs Ford (WEC GT3)
                    if "mustang" in search_text or "ford" in search_text:
                        mapped_brand = "Ford"
                    elif "porsche" in search_text or "911" in search_text:
                        mapped_brand = "Porsche"
                    else:
                        # Default fallback based on user request: "Proton Competition 2025" -> Porsche
                        # But also "Ford: Proton Competition 2025"
                        # If ambiguous, check for "competition" vs "racing" if that helps? No.
                        # Let's assume Ford for WEC GT3 context if not specified
                        mapped_brand = "Ford" 
                elif "gr racing" in search_text:
                    if "2025" in search_text or "ferrari" in search_text or "296" in search_text:
                        mapped_brand = "Ferrari"
                    elif "2024" in search_text: # User listed GR Racing 2024 under Ferrari too
                        mapped_brand = "Ferrari"
                    else:
                        mapped_brand = "Porsche" # Old GTE default
                
                # General Team Mappings
                elif any(x in search_text for x in ["vista", "af corse", "spirit of race", "kessel", "jmw", "richard mille", "ziggo"]):
                    mapped_brand = "Ferrari"
                elif any(x in search_text for x in ["wrt", "the bend", "walkenhorst", "rowe"]):
                    mapped_brand = "BMW"
                elif any(x in search_text for x in ["tf sport", "awa"]):
                    mapped_brand = "Corvette"
                elif any(x in search_text for x in ["heart of racing", "d'station", "racing spirit", "beechdean"]):
                    mapped_brand = "Aston Martin"
                elif any(x in search_text for x in ["united autosports", "inception", "optimum"]):
                    mapped_brand = "mclaren"
                elif any(x in search_text for x in ["grt", "fff"]):
                    mapped_brand = "Lamborghini"
                elif any(x in search_text for x in ["manthey", "pure rxcing", "pfaff", "dinamic", "1st phorm"]):
                    mapped_brand = "Porsche"
                elif any(x in search_text for x in ["multimatic"]):
                    mapped_brand = "Ford"
                elif any(x in search_text for x in ["akkodis", "asp", "vasser sullivan"]):
                    mapped_brand = "Lexus"
                elif any(x in search_text for x in ["winward", "gruppe m", "craft-bamboo"]):
                    mapped_brand = "mercedes"

        # 3. GTE (2023 Season)
        elif "gte" in v_class_lower:
             if "ferrari" in v_name_lower: mapped_brand = "Ferrari"
             elif "porsche" in v_name_lower: mapped_brand = "Porsche"
             elif "aston" in v_name_lower: mapped_brand = "Aston Martin"
             elif "corvette" in v_name_lower: mapped_brand = "Corvette"
             
             if not mapped_brand:
                 if any(x in v_name_lower for x in ["af corse", "kessel", "richard mille", "iron lynx"]):
                     mapped_brand = "Ferrari"
                 elif any(x in v_name_lower for x in ["proton", "project 1", "iron dames", "gr racing", "gulf"]):
                     mapped_brand = "Porsche"
                 elif any(x in v_name_lower for x in ["ort by tf", "d'station", "northwest"]):
                     mapped_brand = "Aston Martin"

        # 4. Hypercar Mappings
        elif any(x in v_class_lower for x in ["hyper", "lmh", "lmdh"]):
            if "alpine" in v_name_lower: mapped_brand = "Alpine"
            elif "isotta" in v_name_lower: mapped_brand = "Isotta"
            elif "valkyrie" in v_name_lower: mapped_brand = "Aston Martin"
            elif "bmw" in v_name_lower: mapped_brand = "BMW"
            elif "lamborghini" in v_name_lower: mapped_brand = "Lamborghini"
            elif "vanwall" in v_name_lower: mapped_brand = "Vanwall"
            elif "glickenhaus" in v_name_lower: mapped_brand = "Glickenhaus"
            elif "peugeot" in v_name_lower: mapped_brand = "Peugeot"
            elif "cadillac" in v_name_lower: mapped_brand = "Cadillac"
            elif "toyota" in v_name_lower: mapped_brand = "toyota"
            elif "ferrari" in v_name_lower: mapped_brand = "Ferrari"
            elif "porsche" in v_name_lower: mapped_brand = "Porsche"
            
            if not mapped_brand:
                if any(x in v_name_lower for x in ["jota", "penske", "proton"]):
                    mapped_brand = "Porsche"
                elif any(x in v_name_lower for x in ["af corse"]):
                    mapped_brand = "Ferrari"
                elif any(x in v_name_lower for x in ["wrt"]):
                    mapped_brand = "BMW"
                elif any(x in v_name_lower for x in ["action express", "whelen"]):
                    mapped_brand = "Cadillac"

        # Search for logo
        logo_name = None
        logo_ext = ".png"
        
        # Try to find the mapped brand first
        if mapped_brand:
            # Check exact match
            if mapped_brand.lower() in self.available_logos:
                logo_name, logo_ext = self.available_logos[mapped_brand.lower()]
            else:
                # Check substring match for mapped brand
                for key in sorted(self.available_logos.keys(), key=len, reverse=True):
                    if key in mapped_brand.lower():
                        logo_name, logo_ext = self.available_logos[key]
                        break
        
        # If no mapping or mapping failed to find file, try original vehicle name
        if not logo_name:
            if veh_name.lower() in self.available_logos:
                logo_name, logo_ext = self.available_logos[veh_name.lower()]
            else:
                for key in sorted(self.available_logos.keys(), key=len, reverse=True):
                    if key in veh_name.lower():
                        logo_name, logo_ext = self.available_logos[key]
                        break
            
        if logo_name:
            return f"{logo_name}{logo_ext}", "OK"
        else:
            return "?", f"MISSING (Mapped to: {mapped_brand if mapped_brand else 'None'})"

# Test Cases
test_cases = [
    # LMGT3
    ("Heart of Racing Team 2025 #27", "GT3"),
    ("D'station Racing 2025 #777", "GT3"),
    ("Team WRT 2025 #46", "GT3"),
    ("TF Sport 2025 #33", "GT3"),
    ("Vista AF Corse 2025 #54", "GT3"),
    ("Iron Dames 2025 #85", "GT3"),
    ("Proton Competition 2025 #88", "GT3"), # Ford
    ("Iron Lynx 2025 #60", "GT3"), # Lambo
    ("Akkodis ASP Team 2025 #78", "GT3"), # Lexus
    ("United Autosports 2025 #59", "GT3"), # McLaren
    ("Manthey EMA 2025 #91", "GT3"), # Porsche
    ("Pure Rxcing 2025 #92", "GT3"), # Porsche
    
    # Hypercar
    ("Toyota Gazoo Racing 2025 #7", "Hypercar"),
    ("Ferrari AF Corse 2025 #50", "Hypercar"),
    ("Porsche Penske Motorsport 2025 #6", "Hypercar"),
    ("Cadillac Racing 2025 #2", "Hypercar"),
    ("Peugeot TotalEnergies 2025 #93", "Hypercar"),
    ("Glickenhaus Racing 2025 #708", "Hypercar"),
    ("Floyd Vanwall Racing 2025 #4", "Hypercar"),
    ("BMW M Team WRT 2025 #15", "Hypercar"),
    ("Lamborghini Iron Lynx 2025 #63", "Hypercar"),
    ("Alpine Endurance Team 2025 #35", "Hypercar"),
    ("Isotta Fraschini 2025 #11", "Hypercar"),
    ("Hertz Team JOTA 2025 #38", "Hypercar"), # Porsche
    ("Proton Competition 2025 #99", "Hypercar"), # Porsche
    
    # LMP2
    ("United Autosports 2025 #22", "LMP2"),
    ("Algarve Pro Racing 2025 #25", "LMP2"),

    # GT3 User Specific Cases
    # Porsche
    ("Proton Competition 2025", "GT3", "Proton Competition"), # Ambiguous, might need model
    ("Iron Dames 2025", "GT3", "Iron Dames"),
    ("Manthey EMA 2025", "GT3", "Manthey EMA"),
    ("Manthey 1st Phorm 2025", "GT3", "Manthey 1st Phorm"),
    ("Manthey PureRxcing 2024", "GT3", "Manthey PureRxcing"),
    
    # Mercedes
    ("Iron Lynx 2025", "GT3", "Iron Lynx"),
    
    # McLaren
    ("United Autosports 2025", "GT3", "United Autosports"),
    ("United Autosports 2024", "GT3", "United Autosports"),
    ("Inception Racing 2024", "GT3", "Inception Racing"),
    
    # Lexus
    ("Akkodis ASP Team 2025", "GT3", "Akkodis ASP Team"),
    ("Akkodis ASP Team 2024", "GT3", "Akkodis ASP Team"),
    
    # Lamborghini
    ("Iron Lynx 2024", "GT3", "Iron Lynx"),
    
    # Ford
    ("Proton Competition 2025 Mustang", "GT3", "Proton Competition"), # Explicit model
    ("Proton Racing 2024", "GT3", "Proton Racing"),
    
    # Ferrari
    ("Vista AF Corse 2025", "GT3", "Vista AF Corse"),
    ("Richard Mille AF Corse 2025", "GT3", "Richard Mille AF Corse"),
    ("AF Corse 2025", "GT3", "AF Corse"),
    ("Spirit of Race 2025", "GT3", "Spirit of Race"),
    ("Kessel Racing 2025", "GT3", "Kessel Racing"),
    ("JMW Motorsport 2025", "GT3", "JMW Motorsport"),
    ("GR Racing 2025", "GT3", "GR Racing"),
    ("Ziggo Sport Tempesta 2025", "GT3", "Ziggo Sport Tempesta"),
    ("Vista AF Corse 2024", "GT3", "Vista AF Corse"),
    ("JMW Motorsport 2024", "GT3", "JMW Motorsport"),
    ("GR Racing 2024", "GT3", "GR Racing"),
    ("Spirit of Race 2024", "GT3", "Spirit of Race"),
    
    # Corvette
    ("AWA Racing 2025", "GT3", "AWA Racing"),
    ("TF Sport 2025", "GT3", "TF Sport"),
    ("TF Sport", "GT3", "TF Sport"),
    
    # BMW
    ("The Bend Team WRT 2025", "GT3", "The Bend Team WRT"),
    ("Team WRT 2025", "GT3", "Team WRT"),
    ("Team WRT 2024", "GT3", "Team WRT"),
    
    # Aston Martin
    ("Racing Spirit of Leman 2025", "GT3", "Racing Spirit of Leman"),
    ("Heart of Racing Team 2025", "GT3", "Heart of Racing Team"),
    ("Heart of Racing Team 2024", "GT3", "Heart of Racing Team"),
    ("D'station Racing 2024", "GT3", "D'station Racing"),
]

def run_test():
    widget = MockWidget()
    
    print(f"\n{'Vehicle Name':<35} | {'Class':<10} | {'Team':<20} | {'Result':<20} | {'Status'}")
    print("-" * 110)
    
    for item in test_cases:
        v_name = item[0]
        v_class = item[1]
        team_name = item[2] if len(item) > 2 else ""
        
        result, status = widget.resolve_logo(v_name, v_class, team_name)
        print(f"{v_name:<35} | {v_class:<10} | {team_name:<20} | {result:<20} | {status}")

if __name__ == "__main__":
    run_test()
