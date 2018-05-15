# GenesisZ
Zcash (forks) genesis block mining script. Runs an external miner for finding valid Equihash solutions.
Inspired by [GenesisH0](https://github.com/lhartikk/GenesisH0), but written from scratch.

## Features
- Modify every parameter that influences the block header hash (see _Usage_)
- Sensible defaults
- Placeholders of the form `{BTC}`, `{ETH}` or `{ZEC}` in the `TIMESTAMP` input string get translated to the currencie's latest block number and hash.
- Uses the [`python-zcashlib`](https://github.com/sebastianst/python-zcashlib), which is a (still very much unfinished) extension of the well-known [`python-bitcoinlib`](https://github.com/petertodd/python-bitcoinlib).

## Getting started
Clone this repo, create a **python 3** virtualenv and install dependencies with pip:
```bash
git clone --recursive https://github.com/sebastianst/GenesisZ
python3 -m venv GenesisZ
cd GenesisZ
source bin/activate
pip install -r requirements.txt
```

Make sure you have a working and supported equihash solver. Currently, the
[silent army](https://github.com/mbevand/silentarmy) GPU solver (only for
mainnet and testnet parameters `N,k=200,9`) and [tromp equihash](https://github.com/tromp/equihash) CPU solver are supported.

#### python-zcashlib submodule
Note that the zcashlib is used as a submodule, since I haven't uploaded it to PyPI yet (and because it's easier for the current interdependent development). That's why you must use the `--recursive` flag during cloning. When you update this repo, don't forget to update the submodule as well, i.e., run `git pull && git submodule update` to update.

## Examples
#### Zcash mainnet
Mine the zcash mainnet gensis block by calling
```bash
./genesis.py -s "/path/to/sa-solver" -r 5000 -t 1477641360
```
or cheat, because you already know the right nonce:
```bash
./genesis.py -s "/path/to/sa-solver" -n 1257 -t 1477641360
```

## Usage
```
usage: genesis.py [-h] [-c {mainnet,testnet,regtest}] [-t TIME] [-C COINNAME]
                  [-z TIMESTAMP] [-Z PSZTIMESTAMP] [-n NONCE] [-r ROUNDS]
                  [-p PUBKEY] [-b BITS] [-E EXTRANONCE] [-V VALUE] [-s SOLVER]
                  [-S {tromp,silentarmy}] [-v]

This script uses any Equihash solver to find a solution for the specified
genesis block

optional arguments:
  -h, --help            show this help message and exit
  -c {mainnet,testnet,regtest}, --chainparams {mainnet,testnet,regtest}
                        Select the core chain parameters for PoW limit and
                        parameters N and K.
  -t TIME, --time TIME  unix time to set in block header (defaults to current
                        time)
  -C COINNAME, --coinname COINNAME
                        the coin name prepends the blake2s hash of timestamp
                        in pszTimestamp
  -z TIMESTAMP, --timestamp TIMESTAMP
                        the pszTimestamp found in the input coinbase
                        transaction script. Will be blake2s'd and then
                        prefixed by coin name. Default is Zcash's mainnet
                        pszTimestamp. You may use tokens of the form {XYZ},
                        which will be replaced by the current block index and
                        hash of coin XZY (BTC, ETH or ZEC). Always the latest
                        block is retrieved, regardless of time argument.
  -Z PSZTIMESTAMP, --pszTimestamp PSZTIMESTAMP
                        Specify the pszTimestamp directly. Will ignore options
                        -C and -z
  -n NONCE, --nonce NONCE
                        nonce to start with when searching for a valid
                        equihash solution; parsed as hex, leading zeros may be
                        omitted.
  -r ROUNDS, --rounds ROUNDS
                        how many nonces to check at most
  -p PUBKEY, --pubkey PUBKEY
                        the pubkey found in the output transaction script
  -b BITS, --bits BITS  the target in compact representation, defining a
                        difficulty of 1
  -E EXTRANONCE, --extra-nonce EXTRANONCE
                        Usually, the coinbase script contains the nBits as
                        fixed first data, which in bitcoin is also referred to
                        as extra nonce. This conventional behaviour can be
                        changed by specifying this parameter (not recommended
                        for mainnet, useful for testnet).
  -V VALUE, --value VALUE
                        output transaction value in zatoshi (1 ZEC = 100000000
                        zatoshi)
  -s SOLVER, --solver SOLVER
                        path to solver binary. Currently supported are
                        silentarmy (sa-solver) and Tromp (equi/equi485).
                        Command line arguments may be passed, although that
                        should be unnecessary.
  -S {tromp,silentarmy}, --solver-type {tromp,silentarmy}
                        Set the type of solver explicitly. Otherwise GenesisZ
                        tries to infer the type from the binary name (equi* ->
                        tromp, sa-solver -> silentarmy)
  -v, --verbose         verbose output
```

### Tromp solver
Make sure to select the right binary with `-s` when using Tromp's equihash solver:

\#threads | main/testnet (`N,K=200,9`) | regtest (`N,K=48,5`)
----------|----------------------------|--------------------
1         | `equi1`                    | `eq4851`
>1        | `equi`                     | `eq485`

Note that `make` only builds `equi{,1}`, so you have to run `make eq485{,1}` in Tromp's source directory if you need the solver for regtest.

## TODO

- [ ] Complete this TODO list
- [X] Regtest genesis block mining. silentarmy only supports the main/testnet parameters `N, K = 200, 9`. See also this [zcash forum thread](https://forum.z.cash/t/equihash-solver-for-n-k-48-5-other-than-default-200-9).
- [ ] More structured and complete output of intermediate information and
  results. Currently, you need to specify verbose output to see all necessary information.
- [ ] Use solvers' native APIs instead of reading `stdout`
- [ ] more examples (zcash testnet, zclassic)
- [ ] Make block number selectable for the `TIMESTAMP` placeholders. Like `{BTC:1234}` for block #1234.

## License
Released under the GPLv3, see `LICENSE` file.
