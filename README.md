# coqprofiler

A simple profiler for Coq `.v` files. Uses the `-time` parameter of `coqc` to gather data and plots the results.
It can output the plots in `.pdf` format or show them on screen. 

## Requirements

```
pip3 install matplotlib seaborn pandas
```
## Usage
- Use as you would use `coqc`. You can pass `coqc` parameters to it.
- If necessary, tweak `config.py` file to change to change preferences
- Type `make example` and check the `example/` folder to test



![alt text](resources/preview.png "Title")