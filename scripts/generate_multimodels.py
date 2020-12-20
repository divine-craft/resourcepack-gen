import csv
import json
import os

# see: https://minecraft.gamepedia.com/Item_durability#Tool_durability

import click

# note: on `pack_format: 4` durabilities should be decreased by 1
TOOL_DURABILITIES_V3 = {
    # Wooden
    'wooden_shovel': 59,
    'wooden_pickaxe': 59,
    'wooden_axe': 59,
    'wooden_hoe': 59,
    # Stone
    'stone_shovel': 131,
    'stone_pickaxe': 131,
    'stone_axe': 131,
    'stone_hoe': 131,
    # Iron
    'iron_shovel': 250,
    'iron_pickaxe': 250,
    'iron_axe': 250,
    'iron_hoe': 250,
    # Golden
    'golden_shovel': 32,
    'golden_pickaxe': 32,
    'golden_axe': 32,
    'golden_hoe': 32,
    # Diamond
    'diamond_shovel': 1561,
    'diamond_pickaxe': 1561,
    'diamond_axe': 1561,
    'diamond_hoe': 1561,
    # Netherite
    'netherite_shovel': 2031,
    'netherite_pickaxe': 2031,
    'netherite_axe': 2031,
    'netherite_hoe': 2031,
    # Other
    'fishing_rod': 64,
    'flint_and_steel': 64,
    'carrot_on_a_stick': 25,
    'shears': 238,
    'shield': 336,
    'bow': 384,
    'trident': 250,
    'elytra': 432,
    'crossbow': 326,
    'warped_fungus_on_a_stick': 100,
}


# TODO fix corner-cases
TOOL_DURABILITIES_V4 = dict(map(lambda pair: (pair[0], pair[1]), TOOL_DURABILITIES_V3.items()))


def generate_multimodel(csv_mappings_file: str, model_name: str, durability: int, model=None) -> dict:
    """
    Generates

    :param csv_mappings_file: name of the CSV-file containing required mapping
    :param model_name: name of the original model
    :param durability: durability of the item used for specific model generation
    :param model: basic model data, by default it will be filled with standard parent and textures
    :return created model
    """

    if model is None:
        model = {
            'parent': 'item/handheld',
            'textures': {'layer0': f'items/{model_name}'}
        }

    with open(csv_mappings_file) as csv_mappings_file:
        mappings = csv.reader(csv_mappings_file)
        next(mappings, None)

        original_model = f'item/{model_name}'
        overrides = [{'predicate': {'damage': 0}, 'model': original_model}]
        for mapping in mappings:
            overrides.append({
                'predicate': {'damaged': 0, 'damage': int(mapping[0]) / durability},
                'model': mapping[1]
            })
        overrides.append({'predicate': {'damaged': 1}, 'model': original_model})
        model['overrides'] = overrides

    return model


def generate_multimodel_files(mappings_directory: str, target_directory: str, pack_format: int) -> None:
    """
    Generates multimodel files according to the given mappings

    :param mappings_directory: directory containing mapping-files names `<tool_name>.csv`
    :param target_directory: directory to store generated multimodel files names as `<tool_name>.json`
    :param pack_format: format of the resourcepack for which the model is generated
    """

    # Start by creating a directory so that the permissions are fail-safely checked
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    durabilities = TOOL_DURABILITIES_V4 if pack_format >= 4 else TOOL_DURABILITIES_V3

    for mappings_file in os.listdir(mappings_directory):
        if mappings_file.endswith('.csv'):
            model_name = mappings_file[:-4]

            durability = durabilities[model_name]
            if durability is None:
                raise ValueError(f'Unknown tool to generate model for: {model_name}')

            with open(f'{target_directory}/{model_name}.json', 'w') as target_file:
                json.dump(generate_multimodel(
                    f'{mappings_directory}/{mappings_file}', model_name, durability), target_file, separators=(',', ':')
                )


@click.command()
@click.option(
    '-m', '--mappings', 'mappings_path',
    help='Path to mappings\' folder containing `<tool_name>.csv` files',
    type=click.Path(file_okay=False)
)
@click.option(
    '-t', '--target', 'target_path',
    help='Path to models\' folder to contain `<tool_name>.json` files',
    type=click.Path(file_okay=False, writable=True)
)
@click.option(
    '-f', '--format', 'pack_format',
    help='Pack format of the pack for which the model is generated',
    type=int
)
def main(mappings_path: str, target_path: str, pack_format: int) -> None:
    generate_multimodel_files(mappings_path, target_path, pack_format)


if __name__ == '__main__':
    main()
