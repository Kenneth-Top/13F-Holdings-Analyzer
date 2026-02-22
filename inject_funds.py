import os

def insert_missing():
    # Read missing dicts
    with open('dataroma_missing.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract only the dict lines
    dict_lines = [line for line in lines if line.strip().startswith('{')]
    
    # Read config.py
    config_path = os.path.join('backend', 'config.py')
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
        
    # Find the end of FUNDS array
    # Looking for:
    #     # 注: Hillman Value Fund / FPA Queens Road / Meridian Contrarian 无独立 SEC CIK
    # ]
    target_idx = config_content.find(']')
    
    if target_idx != -1:
        # We need to find the specific ] that closes FUNDS
        # A safer way: search for "\n]" after FUNDS
        start_funds = config_content.find('FUNDS = [')
        end_funds = config_content.find('\n]', start_funds)
        
        if start_funds != -1 and end_funds != -1:
            insertion = "\n    # --- Dataroma Missing Funds (Fallback Scraper) ---\n" + "".join(dict_lines)
            new_config = config_content[:end_funds] + insertion + config_content[end_funds:]
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_config)
            print("Successfully injected missing funds into config.py")
        else:
            print("Could not find FUNDS array bounds")

insert_missing()
