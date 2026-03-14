import json

with open('data/data.json') as f:
    data = json.load(f)

print('Top-level keys:', list(data.keys()))
print('Total top-level keys:', len(data.keys()))

# Check for the 6 target items
target_items = [
    'Versatile_Framework',
    'Modular_Engine',
    'Adaptive_Control_Unit',
    'Heavy_Modular_Frame',
    'Automated_Wiring',
    'Cable',
]

# Explore one section to understand structure
for key in list(data.keys()):
    section = data[key]
    if isinstance(section, dict):
        print(f'\n[{key}] -- {len(section)} entries, sample keys: {list(section.keys())[:5]}')
    elif isinstance(section, list):
        print(f'\n[{key}] -- list of {len(section)} items')
    else:
        print(f'\n[{key}] -- {type(section).__name__}: {str(section)[:80]}')
