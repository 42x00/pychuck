import pygame
pygame.init()
import argparse
from pychuck.core import _Chuck

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--compile', action='store_true')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to execute')
    args = parser.parse_args()

    app = _Chuck(compile=args.compile)
    for file in args.files:
        app._add_shred(code=open(file).read())
    app._loop()
