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
        else:
            i += 1
            continue

        if (i + 1) < len(argv) and not argv[i + 1].startswith('-'):
            value = argv[i + 1]
            i += 1
        else:
            value = "True"
            
        args[key] = value
        i += 1
    return args


def build_config(args):
    config_kwargs = {}
    for field in Config.__dataclass_fields__:
        value = args.get(field, getattr(Config, field))
        field_type = Config.__dataclass_fields__[field].type
        if field_type == int:
            value = int(value)
        elif field_type == bool:
            value = str(value).lower() in ['true', '1', 'yes']
        config_kwargs[field] = value
    return Config(**config_kwargs)
