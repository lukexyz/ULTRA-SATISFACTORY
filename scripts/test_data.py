"""
Test script for ultra_satisfactory.data module.
Mirrors the test cell in nbs/00_data.ipynb.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ultra_satisfactory.data import load_data, get_item_recipe

DATA_PATH = Path('data/data.json')
data = load_data(DATA_PATH)

targets = [
    'Versatile Framework',
    'Modular Engine',
    'Adaptive Control Unit',
    'Heavy Modular Frame',
    'Automated Wiring',
    'Cable',
]

all_ok = True
for name in targets:
    result = get_item_recipe(name, data)
    if result is None:
        print(f'FAIL: {name} -- not found')
        all_ok = False
    else:
        ing_str = ', '.join(f"{i['name']} x{i['amount']}" for i in result['ingredients'])
        prod = result['products'][0]
        print(f"OK: {result['name']}")
        print(f"    Recipe:      {result['recipe_name']}")
        print(f"    Machine:     {result['machine']} ({result['machine_power']} MW)")
        print(f"    Cycle:       {result['cycle_time']}s")
        print(f"    Output:      {prod['amount']} @ {prod['rate_per_min']}/min")
        print(f"    Ingredients: {ing_str}")
        print(f"    Image URL:   {result['image_url']}")
        print()

if all_ok:
    print('All 6 items OK.')
else:
    print('Some items FAILED.')
    sys.exit(1)
