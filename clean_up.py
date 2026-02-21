import os

files_to_remove = [
    'dataroma_funds.json', 'dataroma_manager_names.json', 'dataroma_matched.json',
    'dataroma_unmatched.json', 'dataroma_final_ciks.json', 'dataroma_output.html', 
    'dataroma_brk.html', 'extract_names.py', 'fetch_brk.py', 'fetch_html.py', 
    'match_ciks_v2.py', 'match_sec_db.py', 'search_sec.py', 'new_ciks_to_add.txt', 
    'search_hillhouse.py', 'format_output.py', 'dataroma_spider.py'
]

for f in files_to_remove:
    try:
        if os.path.exists(f):
            os.remove(f)
            print(f"Removed: {f}")
    except OSError as e:
        print(f"Error removing {f}: {e}")
