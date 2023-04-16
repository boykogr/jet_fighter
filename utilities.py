from pygame.image import load
from pathlib import Path
from pygame.mixer import Sound


def load_sprite(name, alpha=True):
    filename = Path(__file__).parent / Path('assets/sprites/' + name + '.png')
    sprite = load(filename.resolve())

    if alpha:
        return sprite.convert_alpha()

    return sprite.convert()


def load_sound(name):
    filename = Path(__file__).parent / Path('assets/sounds/' + name + '.ogg')
    return Sound(filename)
