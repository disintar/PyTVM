# Example of usage PyTVM

Tvm-python is binding to TON VM.

tvm-python branch in [disintar/ton](https://github.com/disintar/ton/tree/tvm-python)

## Compile

Pass `-DTON_USE_PYTHON=1 -DPYTHON_EXECUTABLE=PATH_TO_YOUR_PYTHON` to `cmake build .`
And use `--target tvm-python`

You will get importable `.so` file 
