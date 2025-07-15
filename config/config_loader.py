import json
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ChainConfig:
    name: str
    symbol: str
    initial_reward: float
    halving_interval: Optional[int]
    target_block_time: int
    max_size_bytes: int
    max_transactions: int
    max_supply: Optional[int]
    difficulty_adjustment_blocks: int = 2016
    header_size_bytes: int = 1024
    transaction_size_bytes: int = 256
    
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]):
        return cls(
            name=json_data["name"],
            symbol=json_data["symbol"],
            initial_reward=json_data["mining"]["initial_reward"],
            halving_interval=json_data["mining"]["halving_interval"],
            target_block_time=json_data["mining"]["target_block_time"],
            max_size_bytes=json_data["blocks"]["max_size_bytes"],
            max_transactions=json_data["blocks"]["max_transactions"],
            max_supply=json_data["economics"]["max_supply"],
            difficulty_adjustment_blocks=json_data["consensus"]["difficulty_adjustment_blocks"],
            header_size_bytes=json_data["blocks"]["header_size_bytes"],
            transaction_size_bytes=json_data["blocks"]["transaction_size_bytes"]
        )

@dataclass
class WorkloadConfig:
    name: str
    description: str
    wallets: int
    transactions_per_wallet: int
    transaction_interval: float
    
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]):
        return cls(
            name=json_data["name"],
            description=json_data["description"],
            wallets=json_data["wallets"],
            transactions_per_wallet=json_data["transactions_per_wallet"],
            transaction_interval=json_data["transaction_interval"]
        )

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
    
    def load_defaults(self) -> Dict[str, Any]:
        """Load default configuration values"""
        defaults_file = os.path.join(self.config_dir, "defaults.json")
        if not os.path.exists(defaults_file):
            # Return fallback defaults
            return {
                "default_nodes": 7,
                "default_neighbors": 4,
                "default_miners": 2,
                "default_hashrate": 1000,
                "default_blocktime": 10,
                "default_difficulty": 0,
                "default_reward": 50,
                "default_wallets": 5,
                "default_transactions": 100,
                "default_interval": 1,
                "default_blocksize": 1000,
                "default_blocks": 10,
                "default_print": 144,
                "default_debug": False,
                "default_halving": 210000
            }
        with open(defaults_file, 'r') as f:
            return json.load(f)["simulation"]
    
    def load_cli_mapping(self) -> Dict[str, Any]:
        """Load CLI mapping configuration"""
        cli_file = os.path.join(self.config_dir, "cli_mapping.json")
        if not os.path.exists(cli_file):
            # Return fallback mapping
            return {
                "short_options": {"n": "nodes", "m": "neighbors", "k": "miners", "h": "hashrate",
                                "t": "blocktime", "d": "difficulty", "r": "reward", "w": "wallets",
                                "x": "transactions", "i": "interval", "s": "blocksize", "l": "blocks",
                                "p": "print", "g": "debug"},
                "long_options": {"nodes": "nodes", "neighbors": "neighbors", "miners": "miners",
                               "hashrate": "hashrate", "blocktime": "blocktime", "difficulty": "difficulty",
                               "reward": "reward", "wallets": "wallets", "transactions": "transactions",
                               "interval": "interval", "blocksize": "blocksize", "blocks": "blocks",
                               "print": "print", "debug": "debug", "chain": "chain", "workload": "workload",
                               "years": "years"},
                "data_types": {"nodes": "int", "neighbors": "int", "miners": "int", "hashrate": "int",
                             "blocktime": "int", "difficulty": "int", "reward": "float", "wallets": "int",
                             "transactions": "int", "interval": "float", "blocksize": "int", "blocks": "int",
                             "print": "int", "debug": "bool", "years": "float"},
                "boolean_true_values": ["true", "1", "yes", "on"],
                "boolean_false_values": ["false", "0", "no", "off"]
            }
        with open(cli_file, 'r') as f:
            return json.load(f)
    
    def load_chain_config(self, chain: str) -> ChainConfig:
        """Load blockchain configuration from JSON files"""
        chain_file = os.path.join(self.config_dir, "chains", f"{chain.lower()}.json")
        if not os.path.exists(chain_file):
            raise FileNotFoundError(f"Chain config not found: {chain_file}")
        
        with open(chain_file, 'r') as f:
            data = json.load(f)
        return ChainConfig.from_json(data)
    
    def load_workload_config(self, workload: str) -> WorkloadConfig:
        """Load workload configuration from JSON files"""
        workload_file = os.path.join(self.config_dir, "workloads", f"{workload.lower()}.json")
        if not os.path.exists(workload_file):
            raise FileNotFoundError(f"Workload config not found: {workload_file}")
        
        with open(workload_file, 'r') as f:
            data = json.load(f)
        return WorkloadConfig.from_json(data)