import pychuck
import argparse

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--srate', type=int, default=22050)
    parser.add_argument('--bufsize', type=int, default=256)
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='files to execute')
    args = parser.parse_args()

    # start chuck
    pychuck._Chuck(
        sample_rate=args.srate,
        buffer_size=args.bufsize,
        verbose=args.verbose
    ).start()

    # execute files
    for file in args.files:
        pychuck.spork(exec, open(file).read())
