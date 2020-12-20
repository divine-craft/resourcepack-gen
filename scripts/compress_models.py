import json
import os

import click

# see: https://minecraft.gamepedia.com/Model
ALLOWED_MODEL_ROOT_TAGS = {
    'parent', 'ambientocclusion', 'display', 'textures', 'elements', 'gui_light', 'overrides'
}


def compress_model_files(models_directory: str) -> None:
    for parent, directories, files in os.walk(models_directory):
        for file in files:
            if not file.endswith('.json'):
                continue

            file = os.path.join(parent, file)
            with open(file, 'r+') as model_file:
                model = json.load(model_file)
                model_file.seek(0)

                # Patches start

                # Remove unused root rags
                for key in list(model.keys()):
                    if key not in ALLOWED_MODEL_ROOT_TAGS:
                        del model[key]

                # Patches end

                json.dump(model, model_file, separators=(',', ':'))
                model_file.truncate()


@click.command()
@click.option(
    '-m', '--models', 'models_path',
    help='Path to the folder in which all json-models should be compressed',
    type=click.Path(file_okay=False, writable=True)
)
def main(models_path: str) -> None:
    compress_model_files(models_path)


if __name__ == '__main__':
    main()
