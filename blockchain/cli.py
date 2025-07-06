import sys
from config import Config

option_map = {
    'n': 'nodes',
    'm': 'neighbors',
    'k': 'miners',
    'h': 'hashrate',
    't': 'blocktime',
    'd': 'difficulty',
    'r': 'reward',
    'w': 'wallets',
    'x': 'transactions',
    'i': 'interval',
    's': 'blocksize',
    'l': 'blocks',
    'p': 'print',
    'g': 'debug'
}

def parse_args(argv):
    args = {}
    i = 0
    while (i < len(argv)):
        arg = argv[i]
        if arg.startswith('--'):
            key = argv[i][2:]
        elif arg.startswith('-') and len(arg) == 2:
            key = option_map.get(arg[1], None)
            if key is None:
                print(f"Unknown option: {arg}")
                i += 1
                continue

    argv = sys.argv[1:]
    parse_args(argv)