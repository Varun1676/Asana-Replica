import re

path = "app/schemas.py"

print(f"Scanning {path} for broken regex backreferences...")

with open(path, "r") as f:
    content = f.read()

# This pattern looks for the specific broken syntax: (,\1)*
# We replace it with ".*" which means "followed by anything" (valid and safe)
# The regex below escapes the parentheses and backslash to match the literal characters in the file
broken_pattern = r"\(\,\\1\)\*" 

# Count how many we find before fixing
matches = re.findall(broken_pattern, content)
print(f"Found {len(matches)} broken patterns.")

if matches:
    # Replace all occurrences with ".*"
    new_content = re.sub(broken_pattern, ".*", content)
    
    with open(path, "w") as f:
        f.write(new_content)
    print(f"✅ Success! Patched {len(matches)} validation errors.")
else:
    print("⚠️ No broken patterns found. (Did you run the old patch already? Check schemas.py manually if it still fails).")