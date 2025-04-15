# Type Enforced
[![PyPI version](https://badge.fury.io/py/fizgrid.svg)](https://badge.fury.io/py/fizgrid)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simulate grid based environments.

# Setup

Make sure you have Python 3.10.x (or higher) installed on your system. You can download it [here](https://www.python.org/downloads/).

### Installation

```
pip install fizgrid
```

## Basic Usage
```py
import fizgrid
```

# Getting Started


# Development
## Running Tests, Prettifying Code, and Updating Docs

Make sure Docker is installed and running.

- Create a docker container and drop into a shell
    - `./run.sh`
- Run all tests (see ./utils/test.sh)
    - `./run.sh test`
- Prettify the code (see ./utils/prettify.sh)
    - `./run.sh prettify`
- Update the docs (see ./utils/docs.sh)
    - `./run.sh docs`

- Note: You can and should modify the `Dockerfile` to test different python versions.
