Command line Options:<br> 
--nodes, -n          Number of network nodes (default: 10)  
--neighbors, -m      Connections per node (default: 5)    
--miners, -k         Number of miners (default: 2)  
--hashrate, -h       Hashrate per miner (default: 1M)
--wallets, -w        Number of wallets (default: 5)
--transactions, -x   Transactions per wallet (default: 100)
--blocks, -l         Total blocks to mine (default: 10)
--print, -p          Print summary every N blocks (default: 144)

Blockchain selection:
--chain CHAIN        Blockchain: btc, bch, ltc, doge, memo
--workload WORKLOAD  Workload: small, medium, large
--years YEARS        Simulation of Years
--halving BLOCKS     Halving interval (blocks)

# Simple simulation with default values
python sim-blockchain.py

