# LlamaVerifier Examples

This directory contains example files for using LlamaVerifier.

## Simple Linear Model

The `simple_model.txt` file contains a simple linear model with the following parameters:
- `w1 = 0.5`
- `w2 = 0.3`
- `b = 0.1`

The model computes `y = w1*x1 + w2*x2 + b`.

### Input

The `input.json` file contains the input values:
- `x1 = 2.0`
- `x2 = 3.0`

### Expected Output

The `expected_output.json` file contains the expected output:
- `y = 0.5*2.0 + 0.3*3.0 + 0.1 = 1.9`

## Running the Example

You can run the example using the following command:

```bash
llamaverifier verify --model examples/simple_model.txt --input examples/input.json --expected-output examples/expected_output.json
```

This will verify that the model produces the expected output for the given input. 