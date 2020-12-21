import json
import os

import click


def generate_pack_mcmeta(path: str, version: int, description: str) -> None:
    with open(os.path.join(path, 'pack.mcmeta'), 'w') as file:
        json.dump({
            'pack': {
                'pack_format': version,
                'description': description
            }
        }, file, separators=(',', ':'))


@click.command()
@click.option(
    '-p', '--path', 'path',
    type=click.Path(file_okay=False, writable=True),
    help='Path to resourcepack folder'
)
@click.option(
    '-v', '--version', 'version',
    type=int,
    help='Resourcepack version'
)
@click.option(
    '-d', '--description', 'description',
    help='Resourcepack description'
)
def main(path: str, version: int, description: str) -> None:
    generate_pack_mcmeta(path, version, description)


if __name__ == '__main__':
    main()
