import sys
from blockchain import config

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
    for field in config.Config.__dataclass_fields__:
        value = args.get(field, getattr(config.Config, field))
        field_type = config.Config.__dataclass_fields__[field].type
        if field_type == int:
            value = int(value)
        elif field_type == bool:
            value = str(value).lower() in ['true', '1', 'yes']
        config_kwargs[field] = value

    if 'difficulty' not in args or args['difficulty'] == 0:
        config_kwargs['difficulty'] = int(config_kwargs['blocktime']) * (int(config_kwargs['miners']) * int(config_kwargs['hashrate']))
    return config.Config(**config_kwargs)


def get_config_from_cli():
    argv = sys.argv[1:]
    args = parse_args(argv)
    config = build_config(args)
    return config