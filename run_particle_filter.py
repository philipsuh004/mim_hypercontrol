#!/usr/bin/env python3
"""
Launcher script for MIM HyperControl Particle Filter.

This script provides an easy way to run the particle filter from the project root.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from particle_filter.particle_filter import main
    main()
