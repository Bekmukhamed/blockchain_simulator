import sys
from config import Config

options = {
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
        if argv[i].startswith('--'):
            key = argv[i][2:]
    

    argv = sys.argv[1:]
    parse_args(argv)