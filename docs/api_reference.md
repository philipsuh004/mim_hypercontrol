# API Reference

## Controller Classes

### MIMControl

Core MIM instrument control class.

```python
from controllers.mim_control import MIMControl

# Initialize controller
mim = MIMControl()
```

**Methods**:
- `connect_instruments()`: Connect to Attocube controllers
- `set_position(x, y, z)`: Set position coordinates
- `scan_area(x_range, y_range, steps)`: Perform area scan
- `get_position()`: Get current position

### TemperatureControl

Cryogenic temperature management.

```python
from controllers.temperature_control import TemperatureControl

# Initialize controller
temp = TemperatureControl()
```

**Methods**:
- `set_temperature(channel, temp)`: Set target temperature
- `get_temperature(channel)`: Get current temperature
- `set_ramp_rate(channel, rate)`: Set temperature ramp rate
- `start_ramp(channel)`: Start temperature ramp

### MagnetControl

Magnetic field control.

```python
from controllers.magnet_control import MagnetControl

# Initialize controller
magnet = MagnetControl()
```

**Methods**:
- `set_field(field_value)`: Set magnetic field
- `get_field()`: Get current field
- `set_ramp_rate(rate)`: Set field ramp rate
- `ramp_to_field(target)`: Ramp to target field

### HeliumMonitor

Cryogen level monitoring.

```python
from controllers.helium_monitor import HeliumMonitor

# Initialize monitor
helium = HeliumMonitor()
```

**Methods**:
- `get_level()`: Get current helium level
- `set_alert_threshold(threshold)`: Set alert threshold
- `is_level_low()`: Check if level is low

### ExperimentControl

Automated measurement procedures.

```python
from controllers.experiment_control import CreateExperiment

# Initialize experiment controller
experiment = CreateExperiment()
```

**Methods**:
- `add_measurement(procedure)`: Add measurement to sequence
- `run_sequence()`: Execute measurement sequence
- `save_data(filename)`: Save measurement data

## Main Application

### MainWindow

Main application window class.

```python
from src.main import MainWindow
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
```

## Configuration

### Instrument Configuration

All controllers support configuration through VISA resource names:

```python
# Example configuration
config = {
    'attocube': 'ASRL1::INSTR',
    'temperature': 'TCPIP0::192.168.1.100::INSTR',
    'magnet': 'TCPIP0::192.168.1.101::INSTR'
}
```

### Data Logging

Automatic data logging is enabled by default:

```python
# Log files are automatically created in:
# - logs/temperature_YYYYMMDD_HHMMSS.log
# - logs/magnet_YYYYMMDD_HHMMSS.log
# - logs/experiment_YYYYMMDD_HHMMSS.log
```

## Error Handling

All controllers include comprehensive error handling:

```python
try:
    controller.connect()
except ConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Threading

Controllers use Qt threading for non-blocking operations:

```python
# All long-running operations are threaded
controller.start_measurement()  # Non-blocking
controller.measurement_finished.connect(callback_function)
```
