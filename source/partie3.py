from sys import argv
from os.path import isfile

from amazons import Amazons


def check_file():
    if len(argv) < 2:
        print('Usage: python3 partie3.py <path>')
        return False
    if not isfile(argv[1]):
        print(f'{argv[1]} n\'est pas un chemin valide vers un fichier')
        return False
    return True


def main():
    if not check_file():
        return
    game = Amazons(argv[1])
    game.play()


if __name__ == '__main__':
    import random
    random.seed(0xCAFE)
    main()
