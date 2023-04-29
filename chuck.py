import argparse
from pychuck.core import _Chuck

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--srate', type=int, default=44100)
    parser.add_argument('--bufsize', type=int, default=256)
    parser.add_argument('--in', type=int, default=1)
    parser.add_argument('--out', type=int, default=2)
    parser.add_argument('-c', '--compile', action='store_true')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to execute')
    args = parser.parse_args()

    app = _Chuck(sample_rate=args.srate, buffer_size=args.bufsize,
                 in_channels=args['in'], out_channels=args.out,
                 compile=args.compile)
    for file in args.files:
        app._add_shred(code=open(file).read())
    app._loop()
