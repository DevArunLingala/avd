# AVD - Always Running Android Emulator

Single command setup for macOS Android emulator.

## Quick Start

## Installation

### Option 1: Development (editable)
```bash
pip install -e .
```
### Option 2: Production (from requirements)
```bash
pip install -r requirements.txt
pip install -e .
```


---
## Installation (macOS - Fixed for PEP 668)

```bash
# 1. Ensure Python 3.12
brew install python@3.12

# 2. Clone repo
git clone <your-repo> avd
cd avd

# 3. Create virtual environment + install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 4. Setup & run
avd setup HomeMonitor
avd start
```