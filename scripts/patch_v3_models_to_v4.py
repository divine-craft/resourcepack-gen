import csv
import json
import os

import click


# see: https://github.com/HypixelDev/ResourcePackConverter/tree/master/src/main/resources
# see: https://minecraft.gamepedia.com/Java_Edition_1.13/Flattening
# see: https://blockbench.net/2018/07/18/changes-to-resource-packs-in-minecraft-1-13/

def load_mappings(csv_mappings_file: str) -> dict:
    with open(csv_mappings_file) as csv_mappings_file:
        csv_mappings_file = csv.reader(csv_mappings_file)
        next(csv_mappings_file, None)

        mappings = {}
        for mapping in csv_mappings_file:
            mappings[mapping[0]] = mapping[1]

        return mappings


def patch_v3_models_to_v4(models_directory: str, block_texture_mappings: dict, item_mapping_textures: dict) -> None:
    for parent, directories, files in os.walk(models_directory):
        for file in files:
            if not file.endswith('.json'):
                continue

            file = os.path.join(parent, file)
            with open(file, 'r+') as model_file:
                model = json.load(model_file)
                model_file.seek(0)

                # Patches start
                textures = model['textures']

                dirty = False
                if textures is not None:
                    for (key, value) in list(textures.items()):
                        texture_dirty = False  # Flag indicating if changes happened

                        # 1) remove explicit `minecraft:` namespace
                        if value.startswith('minecraft:'):
                            value = value[10:]
                            texture_dirty = True

                        # 2) replace `blocks/` and `items/` with `block/` and `item/` respectively
                        # 3) fix changed texture names
                        if value.startswith('blocks/'):
                            texture_name = value[7:]
                            value = f'block/{block_texture_mappings.get(texture_name, texture_name)}'

                            texture_dirty = True
                        elif value.startswith('items/'):
                            texture_name = value[6:]
                            value = f'item/{item_mapping_textures.get(texture_name, texture_name)}'

                            texture_dirty = True

                        if texture_dirty:
                            textures[key] = value

                            dirty = True  # At least one change happened
                # Patches end

                if dirty:
                    json.dump(model, model_file, separators=(',', ':'))
                    model_file.truncate()


@click.command()
@click.option(
    '-m', '--models', 'models_path',
    help='Path to the folder in which all json-models should be updated from V3 to V4',
    type=click.Path(file_okay=False, writable=True)
)
@click.option(
    '-b', '--blocks', 'block_textures_mappings_file',
    default=os.path.join(os.path.dirname(__file__), 'mappings/v3_v4/block_textures.csv'),
    help='Path to the CSV-file containing block mappings',
    type=click.Path(dir_okay=False, writable=True)
)
@click.option(
    '-i', '--items', 'item_texture_mappings_file',
    default=os.path.join(os.path.dirname(__file__), 'mappings/v3_v4/item_textures.csv'),
    help='Path to the CSV-file containing item mappings',
    type=click.Path(dir_okay=False, writable=True)
)
def main(models_path: str, block_textures_mappings_file: str, item_texture_mappings_file: str) -> None:
    patch_v3_models_to_v4(
        models_path, load_mappings(block_textures_mappings_file), load_mappings(item_texture_mappings_file)
    )


if __name__ == '__main__':
    main()
