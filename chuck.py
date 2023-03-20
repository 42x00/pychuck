import argparse

from pychuck.core import _Chuck

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--srate', type=int, default=44100)
    parser.add_argument('--bufsize', type=int, default=256)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to execute')
    args = parser.parse_args()

    app = _Chuck(sample_rate=args.srate, buffer_size=args.bufsize, verbose=args.verbose)

    for file in args.files:
        app.add_shred(open(file).read())

    app.start()
