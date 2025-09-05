#!/usr/bin/env python3

"""
Main entry point for the Fractal Explorer application.
Launches the Kivy application.
"""

import os
import kivy
from kivy.resources import resource_add_path
from mandelbrot_app import FractalExplorerApp

if __name__ == '__main__':
    # Make sure current directory is in path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resource_add_path(current_dir)
    
    # Start the Kivy application
    FractalExplorerApp().run()
