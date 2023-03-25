from pygame.image import load
from pathlib import Path


def load_sprite(name, alpha=True):
    filename = Path(__file__).parent / Path('assets/sprites/' + name + '.png')
    sprite = load(filename.resolve())

    if alpha:
        return sprite.convert_alpha()

    return sprite.convert()
