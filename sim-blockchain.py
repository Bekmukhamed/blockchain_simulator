#!/usr/bin/env python3

"""
This is the main entry point for the blockchain simulator.
"""

import sys
import logging
from simulator import cli
from simulator.core.simulation import BlockchainSimulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        config = cli.get_config_from_cli()
        simulator = BlockchainSimulation(config)
        simulator.run()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()