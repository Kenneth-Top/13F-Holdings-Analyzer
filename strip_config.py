import re

with open("ciks_to_remove.txt", "r") as f:
    ciks = set(line.strip() for line in f if line.strip())

with open("backend/config.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

out_lines = []
i = 0
dropped_count = 0
while i < len(lines):
    line = lines[i]
    # format in config.py is usually:
    #     {
    #         "cik": "1234567890",
    # ...
    if '"cik":' in line or "'cik':" in line:
        # Check if the cik is in the set
        match = re.search(r'''["']cik["']\s*:\s*["'](\d+)["']''', line)
        if match and match.group(1) in ciks:
            # Start finding the boundaries. The dictionary usually starts a few lines up or on this line.
            # But here `{"cik"` is usually the start, or it's preceded by `{`.
            # If `{` was on the line before:
            if i > 0 and out_lines[-1].strip() == "{":
                out_lines.pop()
            
            # Skip lines until `}` or `},`
            while i < len(lines):
                if lines[i].strip() in ("}", "},"):
                    i += 1
                    break
                i += 1
            dropped_count += 1
            continue
    out_lines.append(line)

with open("backend/config.py", "w", encoding="utf-8") as f:
    f.write("".join(out_lines))

print(f"Dropped {dropped_count} funds from config.py")
