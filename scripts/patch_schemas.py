import re

path = "app/models/schemas.py"

print(f"Scanning {path} for broken regex patterns...")

with open(path, "r") as f:
    content = f.read()

lines = content.splitlines()
new_lines = []
count = 0

for line in lines:
    # Use raw string for search, looking for double backslash + 1
    if "pattern=r'" in line and r"\\1" in line:
        
        # Regex to remove `pattern=r'.*?',` 
        # Match pattern=r' then minimal chars then ' then optional comma
        new_line = re.sub(r"pattern=r'.*?',?", "", line)
        
        # Cleanup trailing spaces if any
        new_line = new_line.rstrip()
        
        new_lines.append(new_line)
        count += 1
    else:
        new_lines.append(line)

new_content = "\n".join(new_lines)

if count > 0:
    with open(path, "w") as f:
        f.write(new_content)
    print(f"✅ Success! Patched {count} lines.")
else:
    print("⚠️ No patterns found to patch.")
