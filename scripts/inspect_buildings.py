import json

with open('data/data.json') as f:
    data = json.load(f)

# Show one building entry
key = 'Desc_AssemblerMk1_C'
print('Building sample:', json.dumps(data['buildings'].get(key, {}), indent=2)[:500])

# Also show Constructor
key2 = 'Desc_ConstructorMk1_C'
print('\nConstructor sample:', json.dumps(data['buildings'].get(key2, {}), indent=2)[:500])
