#!/usr/bin/env python3

"""
Main Kivy application for the Fractal Explorer.
Handles screens and navigation between different fractal explorers.
"""

import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder

# Import screens first so classes are registered before loading KV files
from main_menu import MainMenuScreen
from fractal_explorer import MandelbrotExplorerScreen

# Make sure kv directory exists
kv_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kv')
if not os.path.exists(kv_directory):
    os.makedirs(kv_directory)

# Assets directory for images
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)
    
    # Create a simple placeholder image if it doesn't exist
    placeholder_path = os.path.join(assets_dir, 'placeholder.png')
    if not os.path.exists(placeholder_path):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (300, 200), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 280, 180], outline=(100, 100, 100), width=2)
        draw.line([20, 20, 280, 180], fill=(100, 100, 100), width=2)
        draw.line([20, 180, 280, 20], fill=(100, 100, 100), width=2)
        img.save(placeholder_path)

# Load KV files in specific order (main.kv must be first)
Builder.load_file(os.path.join(kv_directory, 'main.kv'))
Builder.load_file(os.path.join(kv_directory, 'menu.kv'))
Builder.load_file(os.path.join(kv_directory, 'explorer.kv'))

class FractalExplorerApp(App):
    """Main application class for the Fractal Explorer"""
    
    # Define app properties
    title = 'Fractal Explorer'
    
    def build(self):
        """Build the application and return the root widget"""
        # Set window size
        Window.size = (1400, 900)
        
        # Create screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # Add screens
        self.screen_manager.add_widget(MainMenuScreen(name='main_menu'))
        self.screen_manager.add_widget(MandelbrotExplorerScreen(name='mandelbrot_explorer'))
        
        # Start with main menu
        self.screen_manager.current = 'main_menu'
        
        return self.screen_manager
    
    def on_start(self):
        """Called when the application starts"""
        pass
    
    def on_stop(self):
        """Called when the application stops"""
        pass
