# Getting Started

I have set up data collection, visualization and training 
as cli programs, that is installed as part of the package.

## Installation

```shell
pip install -e .
```

## Where the scripts are

the scripts are located in the `scripts` module in any of the
installed packages. For instance, `lucidxr` contains the `launch.py`
script, which you can call via `lucidxr-launch -h` from the command
line after installation. (Updated on 2025-02-07)

**`lucidxr-launch`**: This one launches on the cluster. You can call via
```shell
lucidxr-launch --sweep some_exp.jsonl 
```

**`collect-demo`**: this one fires up a vuer server, that allows you to 
collect demonstrations. You can call via
```shell
collect-demo --name pick_block
```
  
**`visualize-demo`**: this one visualizes the demonstrations you have 
collected. You can call via
```shell
visualize-demo --name pick_block
```

for details of each of then, 
- [ ] setup doc page for each of the cli.
