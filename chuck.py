import time
import argparse
from pychuck.core import _Chuck, spork

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--srate', type=int, default=22050)
    parser.add_argument('--bufsize', type=int, default=64)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to execute')
    args = parser.parse_args()

    app = _Chuck(sample_rate=args.srate, buffer_size=args.bufsize, verbose=args.verbose)

    for file in args.files:
        spork(file)

    app.start()
