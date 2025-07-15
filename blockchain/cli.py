import sys
import os
import json
from blockchain import config
from config.config_loader import ConfigLoader

class JSONBasedCLI:
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.cli_mapping = self.config_loader.load_cli_mapping()
        self.defaults = self.config_loader.load_defaults()
    
    def parse_args(self, argv):
        args = {}
        i = 0
        while i < len(argv):
            arg = argv[i]
            if arg.startswith('--'):
                key = arg[2:]
                if key in self.cli_mapping["long_options"]:
                    key = self.cli_mapping["long_options"][key]
                else:
                    print(f"Unknown option: {arg}")
                    i += 1
                    continue
            elif arg.startswith('-') and len(arg) == 2:
                short_key = arg[1]
                if short_key in self.cli_mapping["short_options"]:
                    key = self.cli_mapping["short_options"][short_key]
                else:
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

    def convert_value(self, key, value):
        try:
            if key in self.cli_mapping["data_types"]:
                data_type = self.cli_mapping["data_types"][key]
                if data_type == "int":
                    # Handle scientific notation
                    return int(float(value))
                elif data_type == "float":
                    return float(value)
                elif data_type == "bool":
                    return value.lower() in self.cli_mapping["boolean_true_values"]
        except (ValueError, KeyError) as e:
            print(f"Error converting {key}={value}: {e}")
            return value
        return value

    def build_config(self, args):
        config_kwargs = {}
        
        # Start with defaults from JSON
        for field in config.Config.__dataclass_fields__:
            default_key = f"default_{field}"
            if default_key in self.defaults:
                config_kwargs[field] = self.defaults[default_key]
            else:
                # Fallback to hardcoded default from Config class
                field_info = config.Config.__dataclass_fields__[field]
                if field_info.default != field_info.default_factory:  # Has default value
                    config_kwargs[field] = field_info.default
                else:
                    # Use class defaults as fallback
                    config_kwargs[field] = getattr(config.Config(), field, 0)
        
        # Override with command line arguments
        for key, value in args.items():
            if key in config.Config.__dataclass_fields__:
                config_kwargs[key] = self.convert_value(key, value)
        
        # Handle chain-specific configuration including mining defaults
        if 'chain' in args:
            try:
                chain_config = self.config_loader.load_chain_config(args['chain'])
                config_kwargs['reward'] = chain_config.initial_reward
                config_kwargs['blocktime'] = chain_config.target_block_time
                config_kwargs['blocksize'] = chain_config.max_transactions
                config_kwargs['halving'] = chain_config.halving_interval or 0
                
                # Set mining defaults if not specified
                if 'miners' not in args and hasattr(chain_config, 'default_miners'):
                    config_kwargs['miners'] = getattr(chain_config, 'default_miners', 2)
                if 'hashrate' not in args and hasattr(chain_config, 'default_hashrate'):
                    config_kwargs['hashrate'] = getattr(chain_config, 'default_hashrate', 1000000)
                
            except FileNotFoundError as e:
                print(f"Warning: {e}")
        
        # Handle workload-specific configuration
        if 'workload' in args:
            try:
                workload_config = self.config_loader.load_workload_config(args['workload'])
                config_kwargs['wallets'] = workload_config.wallets
                config_kwargs['transactions'] = workload_config.transactions_per_wallet
                config_kwargs['interval'] = workload_config.transaction_interval
            except FileNotFoundError as e:
                print(f"Warning: {e}")
        
        # Handle years parameter
        if 'years' in args:
            years = float(args['years'])
            # Use the configured block time, not the default
            blocks_per_day = int(86400 / config_kwargs['blocktime'])
            config_kwargs['blocks'] = int(blocks_per_day * 365 * years)
        
        # Initialize difficulty if not provided
        if 'difficulty' not in args or args['difficulty'] == '0':
            config_kwargs['difficulty'] = int(config_kwargs['blocktime'] * 
                                           config_kwargs['miners'] * 
                                           config_kwargs['hashrate'])
        
        return config.Config(**config_kwargs)

# Create global instance
json_cli = JSONBasedCLI()

def parse_args(argv):
    return json_cli.parse_args(argv)

def build_config(args):
    return json_cli.build_config(args)

def get_config_from_cli():
    argv = sys.argv[1:]
    args = parse_args(argv)
    return build_config(args)