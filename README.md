## Blockchain Simulator

Blockchain network simulation framework built in Python using SimPy for discrete event simulation. Supports multiple blockchain protocols—including Bitcoin (btc), Bitcoin Cash (bch), Litecoin (ltc), Dogecoin (doge), and Memo

## Installation
```bash
git clone https://github.com/Bekmukhamed/blockchain_simulator.git
cd blockchain_simulator
```
```bash
pip install -r requirements.txt
```
## Examples
Simple simulation with default values<br> 
```
python sim-blockchain.py
```
Simulation with custom parameters
```
python sim-blockchain.py --nodes 20 --miners 5 --blocks 100
```

## Command line Options
```
--nodes, -n          Number of network nodes (default: 10) 
--neighbors, -m      Connections per node (default: 5)
--miners, -k         Number of miners (default: 2)
--hashrate, -h       Hashrate per miner (default: 1M)
--wallets, -w        Number of wallets (default: 5) 
--transactions, -x   Transactions per wallet (default: 100)
--blocks, -l         Total blocks to mine (default: 10)
--print, -p          Print summary every N blocks (default: 144)
```
Blockchain selection:<br> 
```
--chain CHAIN        Blockchain: btc, bch, ltc, doge, memo
--workload WORKLOAD  Workload: small, medium, large
--years YEARS        Simulation of Years 
--halving BLOCKS     Halving interval (blocks) 
```

