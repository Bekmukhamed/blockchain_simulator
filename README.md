Command line Options:<br> 
```
--nodes, -n          Number of network nodes (default: 10)  <br> 
--neighbors, -m      Connections per node (default: 5)    <br> 
--miners, -k         Number of miners (default: 2)  <br> 
--hashrate, -h       Hashrate per miner (default: 1M)<br> 
--wallets, -w        Number of wallets (default: 5)<br> 
--transactions, -x   Transactions per wallet (default: 100)<br> 
--blocks, -l         Total blocks to mine (default: 10)<br> 
--print, -p          Print summary every N blocks (default: 144)<br> 
```
Blockchain selection:<br> 
```
--chain CHAIN        Blockchain: btc, bch, ltc, doge, memo<br> 
--workload WORKLOAD  Workload: small, medium, large<br> 
--years YEARS        Simulation of Years<br> 
--halving BLOCKS     Halving interval (blocks)<br> 
```
Simple simulation with default values<br> 
```python sim-blockchain.py<br>```

