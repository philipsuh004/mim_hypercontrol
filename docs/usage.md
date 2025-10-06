# User Manual

## Getting Started

### Launching the Application

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run: `python src/main.py`

### Main Interface Overview

The MIM HyperControl application provides a unified interface with multiple control panels:

- **Main Control Panel**: Central hub for all operations
- **MIM Control**: Position control and scanning
- **Temperature Control**: Cryogenic temperature management
- **Magnet Control**: Magnetic field control
- **Helium Monitor**: Cryogen level monitoring
- **Experiment Control**: Automated measurement sequences

## Control Modules

### MIM Control

**Purpose**: Core instrument control and positioning

**Key Features**:
- Attocube controller integration
- Precise positioning control
- Scanning capabilities
- Real-time position monitoring

**Usage**:
1. Connect to Attocube controllers
2. Set position parameters
3. Execute positioning commands
4. Monitor position feedback

### Temperature Control

**Purpose**: Cryogenic temperature management

**Key Features**:
- Multi-channel temperature monitoring
- PID control loops
- Ramp rate control
- Temperature logging

**Usage**:
1. Configure temperature sensors
2. Set target temperatures
3. Configure ramp rates
4. Monitor temperature stability

### Magnet Control

**Purpose**: Magnetic field control and monitoring

**Key Features**:
- Field strength control
- Ramp rate settings
- Field monitoring
- Safety interlocks

**Usage**:
1. Connect to magnet power supply
2. Set field parameters
3. Configure ramp rates
4. Monitor field stability

### Helium Monitor

**Purpose**: Cryogen level monitoring and alerts

**Key Features**:
- Real-time level monitoring
- Alert thresholds
- Level logging
- Safety notifications

**Usage**:
1. Configure level sensors
2. Set alert thresholds
3. Monitor levels continuously
4. Respond to alerts

### Experiment Control

**Purpose**: Automated measurement procedures

**Key Features**:
- Programmable sequences
- Data acquisition
- Real-time plotting
- Data export

**Usage**:
1. Design measurement sequences
2. Set acquisition parameters
3. Run automated experiments
4. Export results

## Data Management

### Data Storage

- All data is automatically logged
- Data files are timestamped
- Export formats: CSV, HDF5, JSON

### Plotting and Visualization

- Real-time data plotting
- Interactive zoom and pan
- Export plots as images
- Customizable plot parameters

## Safety Features

### Interlocks

- Temperature interlocks
- Helium level warnings
- Field safety limits
- Emergency stop functionality

### Monitoring

- Continuous system monitoring
- Alert notifications
- Log file generation
- Error reporting

## Best Practices

### Before Starting Experiments

1. Verify all instrument connections
2. Check temperature stability
3. Confirm magnetic field settings
4. Monitor helium levels

### During Experiments

1. Monitor system status continuously
2. Respond to alerts promptly
3. Save data regularly
4. Document experimental conditions

### After Experiments

1. Save all data files
2. Document experimental results
3. Shut down systems safely
4. Update log files
