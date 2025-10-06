# Installation Guide

## Prerequisites

- Python 3.7 or higher
- Windows 10/11 (recommended for instrument compatibility)
- VISA drivers for your instruments (NI-VISA recommended)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mim_hypercontrol.git
cd mim_hypercontrol
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install VISA Drivers

Download and install National Instruments VISA drivers from:
https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html

### 5. Verify Installation

```bash
python src/main.py
```

## Troubleshooting

### Common Issues

**ImportError: No module named 'pylablib'**
```bash
pip install pylablib
```

**VISA Resource Manager Error**
- Ensure VISA drivers are properly installed
- Check instrument connections
- Verify VISA resource names

**PyQt5 Import Error**
```bash
pip install PyQt5
```

### Hardware Requirements

- Attocube controllers (for positioning)
- Temperature controllers (Lake Shore, Oxford, etc.)
- Magnet power supplies
- Helium level sensors
- VISA-compatible instruments

## Development Setup

For development work:

```bash
pip install -r requirements.txt
pip install pytest black flake8
```

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black src/
```
