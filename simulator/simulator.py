import time
import simpy
import logging
from typing import List, Optional
from dataclasses import dataclass, field

from blockchain.core.nodes import Node
from blockchain.core.miner import Miner
from blockchain.core.wallet import Wallet
from blockchain.core.block import Block
from blockchain.core.transaction_pool import TransactionPool
from blockchain.simulation.metrics import SimulationMetrics
from blockchain.network.network_simulator import NetworkSimulator
from blockchain.processes.wallet_process import WalletProcessManager
from blockchain.processes.mining_process import MiningProcessManager
from blockchain.processes.trace_process import TraceProcessManager

@dataclass
class BlockchainSimulation:
    config: object
    
    # Core components
    env: simpy.Environment = field(init=False)
    nodes: List[Node] = field(default_factory=list)
    miners: List[Miner] = field(default_factory=list)
    wallets: List[Wallet] = field(default_factory=list)
    transaction_pool: TransactionPool = field(default_factory=TransactionPool)
    blocks: List[Block] = field(default_factory=list)
    
    # Simulation subsystems
    metrics: SimulationMetrics = field(default_factory=SimulationMetrics)
    network_simulator: NetworkSimulator = field(init=False)
    
    # Process managers
    wallet_manager: WalletProcessManager = field(init=False)
    mining_manager: MiningProcessManager = field(init=False)
    trace_manager: TraceProcessManager = field(init=False)
    
    def __post_init__(self):
        """Initialize simulation components"""
        self.env = simpy.Environment()
        self.logger = logging.getLogger(f"BlockchainSimulation")
        
        # Initialize subsystems
        self.network_simulator = NetworkSimulator(self.config)
        self.wallet_manager = WalletProcessManager(self.env, self.config)
        self.mining_manager = MiningProcessManager(self.env, self.config)
        self.trace_manager = TraceProcessManager(self.env, self.config)
        
        self.logger.info("Initialized blockchain simulation")

    def setup(self) -> None:
        """Setup all simulation components"""
        self._setup_network()
        self._setup_wallets()
        self._setup_miners()
        self._setup_trace_loading()
        
        self.logger.info(
            f"Setup complete: {len(self.nodes)} nodes, "
            f"{len(self.miners)} miners, {len(self.wallets)} wallets"
        )

    def _setup_network(self) -> None:
        """Initialize network topology"""
        from blockchain.network.topology import NetworkTopology
        topology = NetworkTopology()
        topology.create_network(self.nodes, self.config.nodes, self.config.neighbors)

    def _setup_wallets(self) -> None:
        """Initialize wallet instances"""
        self.wallets = self.wallet_manager.create_wallets(self.config.wallets)

    def _setup_miners(self) -> None:
        """Initialize miner instances"""
        self.miners = self.mining_manager.create_miners(self.config.miners, self.config)

    def _setup_trace_loading(self) -> None:
        """Setup trace event loading"""
        self.trace_manager.setup_trace_loading()

    def run(self) -> None:
        """Execute the complete blockchain simulation"""
        start_time = time.time()
        
        try:
            self.setup()
            
            # Start all processes
            self._start_wallet_processes()
            self._start_mining_processes()
            self._start_trace_processes()
            
            # Run simulation
            self.logger.info("Starting blockchain simulation...")
            self.env.run()
            
        except Exception as e:
            self.logger.error(f"Simulation failed: {e}")
            raise
        finally:
            self._print_final_summary(start_time)

    def _start_wallet_processes(self) -> None:
        """Start all wallet processes"""
        for wallet in self.wallets:
            self.env.process(
                self.wallet_manager.wallet_process(wallet, self.transaction_pool, self.metrics)
            )

    def _start_mining_processes(self) -> None:
        """Start all mining processes"""
        for miner in self.miners:
            self.env.process(
                self.mining_manager.mining_process(
                    miner, self.wallets, self.transaction_pool, 
                    self.blocks, self.metrics, self.network_simulator
                )
            )

    def _start_trace_processes(self) -> None:
        """Start trace event processing"""
        if self.trace_manager.has_trace_data():
            self.env.process(self.trace_manager.process_trace_events())

    def _print_final_summary(self, start_time: float) -> None:
        """Print final simulation results"""
        from blockchain.utils.formatters import format_final_summary
        summary = format_final_summary(self.metrics, self.env.now, time.time() - start_time)
        print(summary)