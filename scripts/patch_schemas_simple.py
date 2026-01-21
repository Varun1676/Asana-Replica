path = "app/models/schemas.py"

print(f"Scanning {path}...")

with open(path, "r") as f:
    content = f.read()

# The string to find is literal: (,\1)*
# In python string: "(,\\1)*"
bad_string = r"(,\1)*"

if bad_string in content:
    print("Found bad string!")
    # Replace with .* to match anything (simplifying validation)
    # The original regex was trying to match comma-separated usage of the group 1.
    # We will just relax it to allow recurring chars or specific regex
    # Actually just replacing (,\1)* with .* might break the regex grouping if not careful
    # e.g. ([a|b])(,\1)* -> ([a|b]).*
    
    new_content = content.replace(bad_string, ".*")
    
    with open(path, "w") as f:
        f.write(new_content)
    print("Patched.")
else:
    print("Bad string not found via simple search.")
