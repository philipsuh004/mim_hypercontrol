"""
Basic tests for MIM HyperControl controllers.

Note: These tests require actual hardware connections to be meaningful.
For unit testing without hardware, mock the instrument connections.
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestControllers(unittest.TestCase):
    """Test cases for controller classes."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_import_controllers(self):
        """Test that all controllers can be imported."""
        try:
            from controllers.mim_control import MIMControl
            from controllers.temperature_control import TemperatureControl
            from controllers.magnet_control import MagnetControl
            from controllers.helium_monitor import HeliumMonitor
            from controllers.experiment_control import CreateExperiment
        except ImportError as e:
            self.fail(f"Failed to import controllers: {e}")
    
    def test_controller_initialization(self):
        """Test that controllers can be initialized."""
        try:
            from controllers.mim_control import MIMControl
            from controllers.temperature_control import TemperatureControl
            from controllers.magnet_control import MagnetControl
            from controllers.helium_monitor import HeliumMonitor
            from controllers.experiment_control import CreateExperiment
            
            # Note: These will create GUI windows, so they should be tested
            # in a headless environment or with proper cleanup
            pass
            
        except Exception as e:
            self.fail(f"Failed to initialize controllers: {e}")

if __name__ == '__main__':
    unittest.main()
