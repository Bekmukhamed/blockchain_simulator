import sys
import os
import json
from simulator import config
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
                    self.show_help()
                    sys.exit(1)
            elif arg.startswith('-') and len(arg) == 2:
                short_key = arg[1]
                if short_key in self.cli_mapping["short_options"]:
                    key = self.cli_mapping["short_options"][short_key]
                else:
                    print(f"Unknown option: {arg}")
                    self.show_help()
                    sys.exit(1)
            else:
                i += 1
                continue

            # Check if this is a help request
            if key == "help":
                args[key] = True
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

    def show_help(self):
        """Display comprehensive help information"""
        print("Blockchain Simulator - Help")
        print("=" * 50)
        print()
        
        # Basic usage
        print("USAGE:")
        print("  python sim-blockchain.py [OPTIONS]")
        print()
        
        # Options from configuration
        print("OPTIONS:")
        self._print_options()
        print()
        
        # Chain configurations
        print("BLOCKCHAIN TYPES:")
        self._print_available_chains()
        print()
        
        # Workload configurations  
        print("WORKLOAD PRESETS:")
        self._print_available_workloads()
        print()
        
        # Examples
        print("EXAMPLES:")
        self._print_examples()
        print()

    def _print_options(self):
        """Print all available CLI options with descriptions"""
        if "help_descriptions" not in self.cli_mapping:
            print("  No option descriptions available")
            return
            
        # Get reverse mappings for short options
        short_to_long = {v: k for k, v in self.cli_mapping["short_options"].items()}
        
        # Print each option with its description
        for long_opt, param_name in self.cli_mapping["long_options"].items():
            short_opt = short_to_long.get(param_name, "")
            description = self.cli_mapping["help_descriptions"].get(param_name, "No description available")
            
            # Format option display
            if short_opt:
                option_display = f"  --{long_opt}, -{short_opt}"
            else:
                option_display = f"  --{long_opt}"
                
            # Add data type information
            data_type = self.cli_mapping.get("data_types", {}).get(param_name, "string")
            if data_type != "bool":
                option_display += f" <{data_type}>"
                
            print(f"{option_display:<25} {description}")

    def _print_available_chains(self):
        """Print available blockchain configurations"""
        try:
            chains_dir = "config/chains"
            if os.path.exists(chains_dir):
                chain_files = [f[:-5] for f in os.listdir(chains_dir) if f.endswith('.json')]
                for chain in sorted(chain_files):
                    try:
                        chain_config = self.config_loader.load_chain_config(chain)
                        print(f"  {chain:<10} {chain_config.name} - {chain_config.symbol}")
                    except Exception:
                        print(f"  {chain:<10} {chain.upper()}")
            else:
                print("  No chain configurations found")
        except Exception as e:
            print(f"  Error loading chain information: {e}")

    def _print_available_workloads(self):
        """Print available workload configurations"""
        try:
            workloads_dir = "config/workloads"
            if os.path.exists(workloads_dir):
                workload_files = [f[:-5] for f in os.listdir(workloads_dir) if f.endswith('.json')]
                for workload in sorted(workload_files):
                    try:
                        workload_config = self.config_loader.load_workload_config(workload)
                        print(f"  {workload:<10} {workload_config.wallets} wallets, "
                              f"{workload_config.transactions_per_wallet} tx each, "
                              f"{workload_config.transaction_interval}s interval")
                    except Exception:
                        print(f"  {workload:<10} {workload.capitalize()} workload")
            else:
                print("  No workload configurations found")
        except Exception as e:
            print(f"  Error loading workload information: {e}")

    def _print_examples(self):
        """Print usage examples"""
        if "examples" in self.cli_mapping:
            for example_name, command in self.cli_mapping["examples"].items():
                print(f"  {example_name.capitalize()}:")
                print(f"    {command}")
                print()
        else:
            # Fallback examples
            print("  Basic simulation:")
            print("    python sim-blockchain.py --blocks 100")
            print()
            print("  Bitcoin 1-year simulation:")
            print("    python sim-blockchain.py --chain btc --years 1")
            print()

    def build_config(self, args):
        # Check for help first
        if 'help' in args:
            self.show_help()
            sys.exit(0)
            
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
        
        # Handle years parameter - fix the calculation
        if 'years' in args:
            years = float(args['years'])
            # Use seconds per year / block time to get blocks per year
            seconds_per_year = 365.25 * 24 * 60 * 60  # 31,557,600 seconds
            blocks_per_year = int(seconds_per_year / config_kwargs['blocktime'])
            config_kwargs['blocks'] = int(blocks_per_year * years)
            print(f"Simulating {years} years = {config_kwargs['blocks']} blocks at {config_kwargs['blocktime']}s per block")
        
        # Initialize difficulty if not provided
        if 'difficulty' not in args or args['difficulty'] == '0':
            config_kwargs['difficulty'] = int(config_kwargs['blocktime'] * 
                                           config_kwargs['miners'] * 
                                           config_kwargs['hashrate'])
        
        return config.Config(**config_kwargs)

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