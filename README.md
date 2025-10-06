# MIM HyperControl

A PyQt5-based control system for Magnetic Imaging Microscopy (MIM) experiments developed at Stanford University's Department of Physics.

## Description

This software provides a unified interface for controlling MIM experimental setups, integrating multiple instrument control systems into a single application. The system handles positioning, temperature control, magnetic field management, and cryogen monitoring through a centralized GUI.

**Components:**
- **GUI Control System**: PyQt5-based interface for instrument control
- **Particle Filter**: Image processing and localization algorithms

**Control Modules:**
- MIM positioning and scanning
- Cryogenic temperature control
- Magnetic field control and monitoring  
- Helium level monitoring
- Automated measurement procedures
- Particle filter localization

## Installation

**Prerequisites:**
- Python 3.7 or higher
- VISA drivers (NI-VISA recommended)
- Compatible hardware (Attocube controllers, temperature controllers, magnet power supplies)

**Setup:**
```bash
git clone https://github.com/yourusername/mim_hypercontrol.git
cd mim_hypercontrol
pip install -r requirements.txt
python src/main.py
```

## Usage

The application launches with a main control panel providing access to all instrument modules. Each control panel can be opened independently and configured for your specific hardware setup.

**Typical workflow:**
1. Configure instrument connections in each control panel
2. Set measurement parameters and safety limits
3. Execute positioning, temperature ramps, or field changes
4. Monitor real-time data and system status
5. Run automated measurement sequences

## Documentation

Detailed documentation is available in the `docs/` directory:
- Installation and setup instructions
- User manual with control module descriptions  
- API reference for developers

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Authors

**Philip David Suh** and **Siyuan Qiu**  
Stanford University, Department of Physics

## Contact

For questions about instrument compatibility or technical support, please open an issue in this repository.
