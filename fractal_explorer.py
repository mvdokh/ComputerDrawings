#!/usr/bin/env python3

"""
Mandelbrot Explorer Screen using Kivy.
Provides interactive exploration of the Mandelbrot set.
"""

import threading
import math
import numpy as np
from io import BytesIO
from PIL import Image

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from mandelbrot import Mandelbrot
from deep_zoom_utils import estimate_required_iterations, adjust_color_parameters

class MandelbrotExplorerScreen(Screen):
    """Mandelbrot Explorer Screen using Kivy"""
    
    # Properties
    fractal_image = ObjectProperty(None)
    status_label = ObjectProperty(None)
    iterations_slider = ObjectProperty(None)
    zoom_level = NumericProperty(1.0)
    max_iterations = NumericProperty(500)
    base_iterations = NumericProperty(500)  # Add base_iterations property
    is_computing = BooleanProperty(False)
    preview_quality = StringProperty('Normal')
    dynamic_iterations = BooleanProperty(True)
    oversampling = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super(MandelbrotExplorerScreen, self).__init__(**kwargs)
        
        # Initialize Mandelbrot object
        self.mandelbrot = Mandelbrot(
            xpixels=800,
            maxiter=500,
            coord=(-2.6, 1.845, -1.25, 1.25),
            gpu=True,
            ncycle=32,
            rgb_thetas=(0.0, 0.15, 0.25),
            stripe_s=0,
            step_s=0
        )
        
        # Store initial view for home button
        self.home_coords = list(self.mandelbrot.coord)
        
        # Setup for tracking computation
        self._computing_lock = threading.Lock()
        self._update_scheduled = False
        
    def on_pre_enter(self):
        """Called before the screen is entered"""
        # Schedule initial rendering
        Clock.schedule_once(lambda dt: self.update_mandelbrot(), 0.1)
    
    def on_leave(self):
        """Called when leaving the screen"""
        pass
    
    def update_mandelbrot(self, *args):
        """Update the Mandelbrot set rendering"""
        if self.is_computing:
            return
            
        if self.ids.fractal_image:
            # Get current size of the image widget
            width = int(self.ids.fractal_image.width)
            height = int(self.ids.fractal_image.height)
            
            if width > 50 and height > 50:
                # Update Mandelbrot resolution
                self.mandelbrot.xpixels = width
                self.mandelbrot.ypixels = height
                
                # Adjust aspect ratio
                current_coords = self.mandelbrot.coord
                center_x = (current_coords[0] + current_coords[1]) / 2
                center_y = (current_coords[2] + current_coords[3]) / 2
                x_range = current_coords[1] - current_coords[0]
                aspect_ratio = height / width
                new_y_range = x_range * aspect_ratio
                
                # Update coordinates with proper aspect ratio
                self.mandelbrot.coord = (
                    center_x - x_range/2,
                    center_x + x_range/2,
                    center_y - new_y_range/2,
                    center_y + new_y_range/2
                )
        
        self.is_computing = True
        
        # Start computation in background thread
        threading.Thread(target=self.compute_mandelbrot, daemon=True).start()
    
    def compute_mandelbrot(self):
        """Compute the Mandelbrot set in a background thread"""
        try:
            with self._computing_lock:
                # Update the set
                self.mandelbrot.update_set()
                
                # Get the resulting image
                image_array = self.mandelbrot.set[::-1, :, :]
                
                # Schedule UI update on the main thread
                Clock.schedule_once(lambda dt: self.display_result(image_array), 0)
        except Exception as e:
            print(f"Error computing Mandelbrot set: {e}")
    
    def display_result(self, image_array):
        """Display the computed image"""
        # Create texture from numpy array
        texture = Texture.create(
            size=(image_array.shape[1], image_array.shape[0]), 
            colorfmt='rgb'
        )
        texture.blit_buffer(
            image_array.tobytes(), 
            colorfmt='rgb', 
            bufferfmt='ubyte'
        )
        
        # Update the image
        if self.ids.fractal_image:
            self.ids.fractal_image.texture = texture
        
        # Update status
        self.is_computing = False
        
        # Update any UI elements that depend on the current state
        if self.ids.status_label:
            self.ids.status_label.text = "Ready"
    
    def go_back_to_menu(self):
        """Return to the main menu"""
        self.manager.current = 'main_menu'
    
    def on_touch_down(self, touch):
        """Handle touch down event for zooming"""
        # Handle zooming and other interactions
        return super(MandelbrotExplorerScreen, self).on_touch_down(touch)
    
    def compute_mandelbrot(self):
        """Compute the Mandelbrot set in a background thread"""
        try:
            with self._computing_lock:
                # Update the set
                self.mandelbrot.update_set()
                
                # Get the resulting image
                image_array = self.mandelbrot.set[::-1, :, :]
                
                # Schedule UI update on the main thread
                Clock.schedule_once(lambda dt: self.display_result(image_array), 0)
        except Exception as e:
            print(f"Error computing Mandelbrot set: {e}")
            Clock.schedule_once(lambda dt: self.on_computation_error(str(e)), 0)
    
    def display_result(self, image_array):
        """Display the computed image on the UI thread"""
        if not self.fractal_image:
            return
            
        # Create texture from numpy array
        texture = Texture.create(
            size=(image_array.shape[1], image_array.shape[0]), 
            colorfmt='rgb'
        )
        texture.blit_buffer(
            image_array.tobytes(), 
            colorfmt='rgb', 
            bufferfmt='ubyte'
        )
        texture.flip_vertical()
        
        # Update the image widget
        self.fractal_image.texture = texture
        
        # Update UI
        self.is_computing = False
        if self.status_label:
            self.status_label.text = "Ready"
    
    def on_computation_error(self, error_msg):
        """Handle computation errors"""
        self.is_computing = False
        if self.status_label:
            self.status_label.text = f"Error: {error_msg}"
    
    def update_dynamic_iterations(self):
        """Update iteration count based on zoom level"""
        if not self.dynamic_iterations:
            return
            
        # Calculate appropriate iterations based on zoom - now using base_iterations
        new_iterations = estimate_required_iterations(self.zoom_level, self.base_iterations)
        
        # Apply if significantly different
        current_iterations = self.mandelbrot.maxiter
        if abs(new_iterations - current_iterations) > 0.1 * current_iterations:
            self.mandelbrot.maxiter = new_iterations
            if self.iterations_slider:
                self.iterations_slider.value = new_iterations
                
            # Update UI to show new iteration count
            if self.ids.status_label:
                self.ids.status_label.text = f"Iterations: {new_iterations}"
    
    def on_touch_down(self, touch):
        """Handle touch down event for zooming"""
        if self.collide_point(*touch.pos) and not self.is_computing:
            # Store touch position for possible dragging
            self._touch_drag_start = touch.pos
            
            # Right click (zoom out) is simulated with touch.button == 'right'
            if hasattr(touch, 'button') and touch.button == 'right':
                self.zoom_at_point(touch.pos, zoom_out=True)
                return True
                
        return super(MandelbrotExplorerScreen, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up event for zooming"""
        if self.collide_point(*touch.pos) and self._touch_drag_start:
            # If minimal movement, treat as a click (zoom in)
            if (abs(touch.pos[0] - self._touch_drag_start[0]) < 5 and
                abs(touch.pos[1] - self._touch_drag_start[1]) < 5):
                self.zoom_at_point(touch.pos)
                
            self._touch_drag_start = None
            return True
            
        return super(MandelbrotExplorerScreen, self).on_touch_up(touch)
    
    def zoom_at_point(self, pos, zoom_out=False):
        """Zoom in or out at the specified point"""
        if self.is_computing or not self.ids.fractal_image:  # Use self.ids.fractal_image
            return
            
        # Convert screen coordinates to fractal coordinates
        fx, fy = self.screen_to_fractal_coords(pos)
        
        if fx is None or fy is None:
            return
            
        # Apply zoom
        zoom_factor = 4.0 if zoom_out else 0.25
        self.mandelbrot.zoom_at(fx, fy, zoom_factor)
        
        # Update zoom level
        self.zoom_level = self.zoom_level / 4.0 if zoom_out else self.zoom_level * 4.0
        
        # Update color parameters based on zoom level
        color_params = adjust_color_parameters(self.zoom_level)
        self.mandelbrot.stripe_s = color_params["stripe_s"]
        self.mandelbrot.ncycle = color_params["ncycle"]
        
        # Update iterations based on zoom level
        self.update_dynamic_iterations()
        
        # Schedule update
        self.update_mandelbrot()
    
    def screen_to_fractal_coords(self, pos):
        """Convert screen coordinates to fractal coordinates"""
        if not self.ids.fractal_image or not self.ids.fractal_image.texture:  # Use self.ids.fractal_image
            return None, None
            
        # Get relative position within the image
        local_x = pos[0] - self.fractal_image.x
        local_y = pos[1] - self.fractal_image.y
        
        # Convert to normalized coordinates [0-1]
        norm_x = local_x / self.fractal_image.width
        norm_y = 1.0 - (local_y / self.fractal_image.height)  # Flip Y
        
        # Map to fractal coordinates
        coord = self.mandelbrot.coord
        fx = coord[0] + norm_x * (coord[1] - coord[0])
        fy = coord[2] + norm_y * (coord[3] - coord[2])
        
        return fx, fy
    
    def reset_to_home(self):
        """Reset to the initial view"""
        if self.is_computing:
            return
            
        self.mandelbrot.coord = list(self.home_coords)
        self.zoom_level = 1.0
        self.update_mandelbrot()
    
    def go_back_to_menu(self):
        """Return to the main menu"""
        self.manager.current = 'main_menu'
