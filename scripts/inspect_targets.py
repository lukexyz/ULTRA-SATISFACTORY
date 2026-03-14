import json

with open('data/data.json') as f:
    data = json.load(f)

# Search items for the 6 targets by name
targets = [
    'Versatile Framework',
    'Modular Engine',
    'Adaptive Control Unit',
    'Heavy Modular Frame',
    'Automated Wiring',
    'Cable',
]

print('=== ITEM MATCHES ===')
for key, item in data['items'].items():
    name = item.get('name', '')
    if name in targets:
        print(f'\nKey: {key}')
        print(f'  name: {name}')
        print(f'  All fields: {list(item.keys())}')
        print(f'  Full: {json.dumps(item, indent=2)[:400]}')

print('\n\n=== RECIPE MATCHES ===')
for key, recipe in data['recipes'].items():
    name = recipe.get('name', '')
    # Check if product is one of targets
    products = recipe.get('products', [])
    for p in products:
        item_key = p.get('item', '')
        item_name = data['items'].get(item_key, {}).get('name', '')
        if item_name in targets:
            print(f'\nRecipe Key: {key}')
            print(f'  name: {name}')
            print(f'  Full: {json.dumps(recipe, indent=2)[:600]}')
            break
