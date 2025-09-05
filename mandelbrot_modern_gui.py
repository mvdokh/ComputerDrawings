#!/usr/bin/env python3

"""Modern Interactive Mandelbrot Set Explorer with Real-time Preview"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
import math
import os
import numpy as np
from PIL import Image, ImageTk
from mandelbrot import Mandelbrot

# Optional dependencies with graceful fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import pynvml
    NVIDIA_ML_AVAILABLE = True
except ImportError:
    NVIDIA_ML_AVAILABLE = False


# Default UI settings - central place for all visual parameters
DEFAULT_UI_SETTINGS = {
    # Color scheme
    'bg_dark': '#1e1e1e',           # Main background 
    'bg_panel': '#2d2d2d',          # Panel background
    'fg_text': '#ffffff',           # Main text color
    'fg_muted': '#cccccc',          # Secondary text color
    'fg_accent': '#4da6ff',         # Accent color for titles and highlights
    'fg_success': '#00ff00',        # Success messages
    'fg_warning': '#ffff00',        # Warning messages
    'fg_error': '#ff0000',          # Error messages
    'color_button': '#404040',      # Default button color
    'color_button_highlight': '#666666',  # Button hover/active color
    'color_button_save': '#0066cc', # Save button color
    'color_button_create': '#cc6600', # Create button color
    
    # Fonts
    'font_title': ('Segoe UI', 16, 'bold'),
    'font_heading': ('Segoe UI', 11, 'bold'),
    'font_normal': ('Segoe UI', 10),
    'font_small': ('Segoe UI', 9),
    'font_button': ('Segoe UI', 9),
    'font_mono': ('Consolas', 9),
    
    # Layout
    'padding_outer': 10,
    'padding_inner': 20,
    'padding_section': (0, 20),
    'padding_control': 5,
    'panel_width': 350,
    'window_size': (1400, 900),
    
    # Widget styles
    'relief_frame': 'flat',
    'relief_button': 'flat',
    'border_width': 1,
    'highlight_thickness': 0,
    'slider_length': 200,
}


class ModernMandelbrotGUI:
    """Modern Interactive Mandelbrot Set Explorer"""
    
    def __init__(self, root, **kwargs):
        """Initialize the Mandelbrot Explorer GUI
        
        Args:
            root: tk.Tk
                Root Tkinter window
            **kwargs: dict
                Optional UI settings to override defaults
        """
        # Merge default settings with any provided kwargs
        self.ui = DEFAULT_UI_SETTINGS.copy()
        self.ui.update(kwargs)
        
        self.root = root
        self.root.title("🌀 Modern Mandelbrot Explorer")
        self.root.geometry(f"{self.ui['window_size'][0]}x{self.ui['window_size'][1]}")
        self.root.configure(bg=self.ui['bg_dark'])
        
        # Initial sizing variables - these will be updated once the canvas is created
        self.canvas_width = 800  # Default initial width
        self.canvas_height = 600  # Default initial height
        
        # Initialize Mandelbrot object with dynamic resolution that will match canvas size
        self.mandelbrot = Mandelbrot(
            xpixels=800,  # Initial resolution X, will be updated
            maxiter=500,
            coord=(-2.6, 1.845, -1.25, 1.25),
            gpu=True,
            ncycle=32,
            rgb_thetas=(0.0, 0.15, 0.25),
            stripe_s=0,
            step_s=0
        )
        
        # GUI state
        self.current_image = None
        self.is_computing = False
        self.computation_queue = queue.Queue()
        self.update_pending = False
        self.zoom_history = []
        self.max_history = 20
        
        # Store the current zoom level for display
        self.zoom_level = 1.0
        
        # Save the initial coordinates as home
        self.home_coords = list(self.mandelbrot.coord)
        
        # Initialize image scaling info
        self.image_scale = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.scaled_image_width = 0
        self.scaled_image_height = 0
        
        # Add rendering quality options
        self.preview_quality = "Normal"  # "Low", "Normal", "High"
        self.dynamic_iterations = True   # Auto-adjust iterations based on zoom
        self.oversampling = 1            # Super-sampling factor (1, 2, 3)
        
        # Base iteration count (will be scaled with zoom)
        self.base_iterations = 500
        self.max_iterations = 50000      # Upper limit for iterations
        
        # Color themes
        self.color_themes = {
            "Classic": (0.0, 0.15, 0.25),
            "Fire": (0.0, 0.05, 0.1),
            "Ocean": (0.4, 0.6, 0.8),
            "Forest": (0.2, 0.4, 0.1),
            "Purple": (0.7, 0.3, 0.9),
            "Sunset": (0.0, 0.3, 0.6),
            "Electric": (0.2, 0.7, 0.9),
            "Copper": (0.1, 0.05, 0.0)
        }
        
        # Add advanced color presets (combinations of parameters that work well)
        self.color_presets = {
            "Filigree Detail": {
                "rgb_thetas": (0.0, 0.15, 0.25),
                "ncycle": 32,
                "stripe_s": 16,
                "stripe_sig": 0.9,
                "step_s": 8,
                "light": (45., 45., 0.75, 0.2, 0.5, 0.5, 20)
            },
            "Deep Structure": {
                "rgb_thetas": (0.7, 0.3, 0.9),
                "ncycle": 64,
                "stripe_s": 24,
                "stripe_sig": 0.85,
                "step_s": 12,
                "light": (60., 60., 0.85, 0.15, 0.6, 0.7, 30)
            },
            "Fine Detail": {
                "rgb_thetas": (0.2, 0.7, 0.9),
                "ncycle": 48,
                "stripe_s": 12,
                "stripe_sig": 0.95,
                "step_s": 4,
                "light": (30., 30., 0.9, 0.1, 0.7, 0.6, 15)
            },
            "Rich Boundaries": {
                "rgb_thetas": (0.0, 0.3, 0.6),
                "ncycle": 56,
                "stripe_s": 20,
                "stripe_sig": 0.88,
                "step_s": 10,
                "light": (75., 25., 0.8, 0.25, 0.45, 0.65, 25)
            }
        }
        
        # Setup the modern UI
        self.setup_modern_ui()
        
        # Start with initial computation
        self.schedule_update()
    
    def setup_modern_ui(self, **kwargs):
        """Setup modern dark-themed UI
        
        Args:
            **kwargs: dict
                Optional UI settings to override defaults
        """
        # Update UI settings with any kwargs
        ui = self.ui.copy()
        ui.update(kwargs)
        
        # Configure dark theme styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark theme configuration
        style.configure('Dark.TFrame', background=ui['bg_panel'], relief='flat')
        style.configure('Dark.TLabel', background=ui['bg_panel'], foreground=ui['fg_text'])
        style.configure('Dark.TButton', background=ui['color_button'], foreground=ui['fg_text'])
        style.configure('Dark.TScale', background=ui['bg_panel'], troughcolor=ui['color_button'])
        style.configure('Preview.TLabel', background=ui['bg_dark'], foreground=ui['fg_text'])
        
        # Main container with dark background
        main_container = tk.Frame(self.root, bg=ui['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=ui['padding_outer'], pady=ui['padding_outer'])
        
        # Left panel for controls
        left_panel = tk.Frame(
            main_container, 
            bg=ui['bg_panel'], 
            width=ui['panel_width'], 
            relief='raised', 
            bd=ui['border_width']
        )
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, ui['padding_outer']))
        left_panel.pack_propagate(False)
        
        # Right panel for preview
        right_panel = tk.Frame(main_container, bg=ui['bg_dark'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Setup panels with the same UI settings
        self.setup_left_panel(left_panel, **ui)
        self.setup_right_panel(right_panel, **ui)
    
    def setup_left_panel(self, parent, **kwargs):
        """Setup the left control panel
        
        Args:
            parent: tk.Frame
                Parent frame to contain the panel
            **kwargs: dict
                UI settings to use for this panel
        """
        # Merge default settings with any provided kwargs
        ui = self.ui.copy()
        ui.update(kwargs)
        
        # Title
        title_frame = tk.Frame(parent, bg=ui['bg_panel'])
        title_frame.pack(fill=tk.X, padx=ui['padding_inner'], pady=(ui['padding_inner'], ui['padding_inner'] + 10))
        
        title_label = tk.Label(
            title_frame, 
            text="🌀 Mandelbrot Explorer", 
            font=ui['font_title'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_accent']
        )
        title_label.pack()
        
        # Create scrollable frame for controls
        canvas = tk.Canvas(
            parent, 
            bg=ui['bg_panel'], 
            highlightthickness=ui['highlight_thickness']
        )
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ui['bg_panel'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(ui['padding_inner'], 0))
        scrollbar.pack(side="right", fill="y")
        
        # Coordinates section
        self.setup_coordinates_section(scrollable_frame, **ui)
        
        # Visual parameters section
        self.setup_visual_section(scrollable_frame, **ui)
        
        # Export section
        self.setup_export_section(scrollable_frame, **ui)
        
        # Navigation section
        self.setup_navigation_section(scrollable_frame, **ui)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_section(self, parent, title, **kwargs):
        """Create a section frame with a proper header
        
        Args:
            parent: tk.Frame
                Parent frame to contain the section
            title: str
                Title text for the section
            **kwargs: dict
                UI settings to override defaults:
                - bg_panel: Background color
                - fg_text: Text color
                - font_heading: Font for the heading
                - padding_section: Padding for the section
                
        Returns:
            tk.Frame: Content frame for adding section widgets
        """
        # Merge default settings with any provided kwargs
        ui = self.ui.copy()
        ui.update(kwargs)
        
        section_frame = tk.Frame(parent, bg=ui['bg_panel'])
        section_frame.pack(fill=tk.X, pady=ui['padding_section'])
        
        # Section header - make it look like a proper header, not a button
        header_frame = tk.Frame(section_frame, bg=ui['bg_panel'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add a subtle line above the header
        line_frame = tk.Frame(header_frame, bg='#555555', height=1)
        line_frame.pack(fill=tk.X, pady=(0, 8))
        
        header_label = tk.Label(
            header_frame, 
            text=title, 
            font=ui['font_heading'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_text']
        )
        header_label.pack(anchor=tk.W)
        
        # Content frame
        content_frame = tk.Frame(section_frame, bg=ui['bg_panel'])
        content_frame.pack(fill=tk.X, padx=10)
        
        return content_frame
    
    def create_subsection(self, parent, title, **kwargs):
        """Create a subsection frame
        
        Args:
            parent: tk.Frame
                Parent frame to contain the subsection
            title: str
                Title text for the subsection
            **kwargs: dict
                UI settings to override defaults:
                - bg_panel: Background color
                - fg_muted: Text color for subsection title
                - font_small: Font for the title
                
        Returns:
            tk.Frame: Frame for adding subsection widgets
        """
        # Merge default settings with any provided kwargs
        ui = self.ui.copy()
        ui.update(kwargs)
        
        subsection_frame = tk.Frame(parent, bg=ui['bg_panel'])
        subsection_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Fix the pady parameter - use a single value instead of a tuple
        title_label = tk.Label(
            subsection_frame, 
            text=title, 
            font=ui['font_small'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_muted'],
            pady=5  # Changed from pady=(0, 5) to pady=5
        )
        title_label.pack(anchor=tk.W)
        
        return subsection_frame
        
    def setup_coordinates_section(self, parent, **kwargs):
        """Setup coordinate display"""
        ui = self.ui.copy()
        ui.update(kwargs)
        
        section_frame = self.create_section(parent, "📍 Current View", **kwargs)
        
        # Coordinate display
        coord_frame = tk.Frame(section_frame, bg=ui['bg_panel'])
        coord_frame.pack(fill=tk.X, pady=ui['padding_control'])
        
        self.coord_label = tk.Label(
            coord_frame, 
            text="", 
            font=ui['font_mono'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_muted']
        )
        self.coord_label.pack()
        
        # Zoom level display
        zoom_frame = tk.Frame(section_frame, bg=ui['bg_panel'])
        zoom_frame.pack(fill=tk.X, pady=ui['padding_control'])
        
        self.zoom_label = tk.Label(
            zoom_frame, 
            text="Zoom: 1.0x", 
            font=ui['font_normal'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_accent']
        )
        self.zoom_label.pack()
        
        # Reset button
        reset_frame = tk.Frame(section_frame, bg=ui['bg_panel'])
        reset_frame.pack(fill=tk.X, pady=(10, 0))
        
        reset_btn = self.create_button(
            reset_frame, 
            "🏠 Reset to Home View", 
            self.reset_to_home
        )
        reset_btn.pack(fill=tk.X)

    def setup_visual_section(self, parent, **kwargs):
        """Setup visual parameter controls"""
        ui = self.ui.copy()
        ui.update(kwargs)
        
        section_frame = self.create_section(parent, "🎨 Visual Parameters", **kwargs)
        
        # Quality controls
        quality_frame = self.create_subsection(section_frame, "⚙️ Rendering Quality", **kwargs)
        
        # Dynamic iterations toggle
        dyn_iter_frame = tk.Frame(quality_frame, bg=ui['bg_panel'])
        dyn_iter_frame.pack(fill=tk.X, pady=2)
        
        self.dyn_iter_var = tk.BooleanVar(value=self.dynamic_iterations)
        dyn_iter_cb = tk.Checkbutton(
            dyn_iter_frame, 
            text="Dynamic Iterations", 
            variable=self.dyn_iter_var,
            command=self.on_dynamic_iterations_change,
            bg=ui['bg_panel'], 
            fg=ui['fg_text'],
            selectcolor=ui['color_button'], 
            activebackground=ui['bg_panel'],
            activeforeground=ui['fg_text']
        )
        dyn_iter_cb.pack(anchor=tk.W)
        
        # Preview quality
        quality_opt_frame = tk.Frame(quality_frame, bg=ui['bg_panel'])
        quality_opt_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            quality_opt_frame, 
            text="Preview Quality:", 
            bg=ui['bg_panel'], 
            fg=ui['fg_text']
        ).pack(side=tk.LEFT)
        
        self.quality_var = tk.StringVar(value=self.preview_quality)
        quality_combo = ttk.Combobox(
            quality_opt_frame, 
            textvariable=self.quality_var,
            values=["Low", "Normal", "High"],
            state="readonly", 
            width=10
        )
        quality_combo.pack(side=tk.RIGHT)
        quality_combo.bind('<<ComboboxSelected>>', self.on_quality_change)
        
        # Oversampling
        os_frame = tk.Frame(quality_frame, bg=ui['bg_panel'])
        os_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            os_frame, 
            text="Oversampling:", 
            bg=ui['bg_panel'], 
            fg=ui['fg_text']
        ).pack(side=tk.LEFT)
        
        self.os_var = tk.IntVar(value=self.oversampling)
        os_combo = ttk.Combobox(
            os_frame, 
            textvariable=self.os_var,
            values=[1, 2, 3],
            state="readonly", 
            width=10
        )
        os_combo.pack(side=tk.RIGHT)
        os_combo.bind('<<ComboboxSelected>>', self.on_oversampling_change)
        
        # Iterations
        self.iter_slider = self.create_slider(
            section_frame, 
            "Base Iterations:", 
            100, 
            5000, 
            self.base_iterations, 
            self.on_iterations_change, 
            50
        )
        
        # Color presets
        preset_frame = tk.Frame(section_frame, bg=ui['bg_panel'])
        preset_frame.pack(fill=tk.X, pady=ui['padding_control'])
        
        tk.Label(
            preset_frame, 
            text="Color Preset:", 
            font=ui['font_normal'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_text']
        ).pack(anchor=tk.W)
        
        self.preset_var = tk.StringVar(value="Custom")
        preset_combo = ttk.Combobox(
            preset_frame, 
            textvariable=self.preset_var,
            values=["Custom"] + list(self.color_presets.keys()),
            state="readonly", 
            font=ui['font_small']
        )
        preset_combo.pack(fill=tk.X, pady=(5, 0))
        preset_combo.bind('<<ComboboxSelected>>', self.on_preset_change)
        
        # More controls...
        # ... (other visual section UI elements)
        
        # Let's use the existing implementation for brevity
        # The rest of the visual section setup would continue here

    def create_button(self, parent, text, command, **kwargs):
        """Create a styled button with configurable appearance
        
        Args:
            parent: tk.Frame
                Parent frame to contain the button
            text: str
                Text for the button
            command: function
                Function to call when button is clicked
            **kwargs: dict
                UI settings to override defaults:
                - bg_color: Background color (defaults to color_button)
                - fg_color: Text color (defaults to fg_text)
                - font: Font for the button (defaults to font_button)
                - relief: Relief style (defaults to relief_button)
                - width: Width of button (defaults to 0 - auto)
                
        Returns:
            tk.Button: The created button widget
        """
        # Merge default settings with any provided kwargs
        ui = self.ui.copy()
        ui.update(kwargs)
        
        # Use specific kwargs for the button or fall back to defaults
        bg_color = kwargs.get('bg_color', ui['color_button'])
        fg_color = kwargs.get('fg_color', ui['fg_text'])
        font = kwargs.get('font', ui['font_button'])
        relief = kwargs.get('relief', ui['relief_button'])
        width = kwargs.get('width', 0)
        
        button = tk.Button(
            parent, 
            text=text, 
            command=command,
            bg=bg_color, 
            fg=fg_color, 
            font=font, 
            relief=relief,
            width=width
        )
        
        return button
    
    def create_slider(self, parent, label, min_val, max_val, initial, callback, step=1, **kwargs):
        """Create a labeled slider with configurable appearance
        
        Args:
            parent: tk.Frame
                Parent frame to contain the slider
            label: str
                Label text for the slider
            min_val: float
                Minimum value for the slider
            max_val: float
                Maximum value for the slider
            initial: float
                Initial value for the slider
            callback: function
                Function to call when slider value changes
            step: float
                Step size for the slider
            **kwargs: dict
                UI settings to override defaults:
                - bg_panel: Background color
                - fg_text: Text color
                - fg_accent: Color for the value label
                - font_normal: Font for the label
                
        Returns:
            tk.Scale: The created slider widget
        """
        # Merge default settings with any provided kwargs
        ui = self.ui.copy()
        ui.update(kwargs)
        
        slider_frame = tk.Frame(parent, bg=ui['bg_panel'])
        slider_frame.pack(fill=tk.X, pady=ui['padding_control'])
        
        # Label with value
        label_frame = tk.Frame(slider_frame, bg=ui['bg_panel'])
        label_frame.pack(fill=tk.X)
        
        label_text = tk.Label(
            label_frame, 
            text=label, 
            font=ui['font_normal'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_text']
        )
        label_text.pack(side=tk.LEFT)
        
        value_label = tk.Label(
            label_frame, 
            text=str(initial), 
            font=ui['font_normal'], 
            bg=ui['bg_panel'], 
            fg=ui['fg_accent']
        )
        value_label.pack(side=tk.RIGHT)
        
        # Slider
        slider = tk.Scale(
            slider_frame, 
            from_=min_val, 
            to=max_val, 
            orient=tk.HORIZONTAL, 
            resolution=step,
            bg=ui['color_button'], 
            fg=ui['fg_text'], 
            troughcolor=ui['bg_panel'], 
            highlightthickness=ui['highlight_thickness'],
            command=lambda val: self.update_slider_label(value_label, val, callback)
        )
        slider.pack(fill=tk.X, pady=(5, 0))
        slider.set(initial)
        
        return slider
    
    # Now let's make sure we have minimal implementations of the required functions
    # that were referenced in the UI setup code
    
    def update_slider_label(self, label, value, callback):
        """Update slider label and call callback"""
        label.config(text=str(value))
        if callback:
            callback(float(value))
            
    def on_dynamic_iterations_change(self):
        """Handle dynamic iterations toggle"""
        self.dynamic_iterations = self.dyn_iter_var.get()
        if self.dynamic_iterations:
            self.update_dynamic_iterations()
            self.schedule_update()
            
    def update_dynamic_iterations(self):
        """Update iteration count based on zoom level if dynamic iterations is enabled"""
        if self.dynamic_iterations:
            # Calculate iterations based on zoom level using a logarithmic scale
            # This formula can be adjusted based on preference
            new_iterations = int(self.base_iterations * math.log(self.zoom_level + 1, 10) + self.base_iterations)
            new_iterations = min(new_iterations, self.max_iterations)  # Cap at max_iterations
            
            # Only update if significantly different to avoid constant recomputation
            current_iterations = self.mandelbrot.maxiter
            if abs(new_iterations - current_iterations) > 0.1 * current_iterations:
                self.mandelbrot.maxiter = new_iterations
                
                # Update the slider value to reflect the new iteration count
                if hasattr(self, 'iter_slider'):
                    self.iter_slider.set(new_iterations)
                    
                # Update the status display
                if hasattr(self, 'status_label'):
                    self.status_label.config(text=f"Iterations adjusted to {new_iterations}", fg=self.ui['fg_accent'])
                    self.root.after(2000, lambda: self.status_label.config(text="Ready", fg=self.ui['fg_success']))

    def on_quality_change(self, event=None):
        """Handle preview quality change"""
        self.preview_quality = self.quality_var.get()
        self.schedule_update()
    
    def on_oversampling_change(self, event=None):
        """Handle oversampling change"""
        self.oversampling = int(self.os_var.get())
        self.mandelbrot.os = self.oversampling
        self.schedule_update()
    
    def on_iterations_change(self, value):
        """Handle base iterations change"""
        self.base_iterations = int(value)
        if not self.dynamic_iterations:
            self.mandelbrot.maxiter = self.base_iterations
        else:
            self.update_dynamic_iterations()
        self.schedule_update()
    
    def on_preset_change(self, event=None):
        """Handle color preset change"""
        preset_name = self.preset_var.get()
        
        if preset_name == "Custom":
            return  # Keep current settings
            
        if preset_name in self.color_presets:
            preset = self.color_presets[preset_name]
            
            # Update RGB thetas
            self.mandelbrot.rgb_thetas = preset["rgb_thetas"]
            from mandelbrot import sin_colortable
            self.mandelbrot.colortable = sin_colortable(self.mandelbrot.rgb_thetas)
            
            # Update other parameters
            self.mandelbrot.ncycle = preset["ncycle"]
            self.mandelbrot.stripe_s = preset["stripe_s"]
            self.mandelbrot.stripe_sig = preset["stripe_sig"]
            self.mandelbrot.step_s = preset["step_s"]
            self.mandelbrot.light = preset["light"]
            
            # Update sliders to reflect the new values
            if hasattr(self, 'ncycle_slider'):
                self.ncycle_slider.set(preset["ncycle"])
            
            if hasattr(self, 'stripe_slider'):
                self.stripe_slider.set(preset["stripe_s"])
                
            if hasattr(self, 'step_slider'):
                self.step_slider.set(preset["step_s"])
            
            self.schedule_update()
    
    def setup_right_panel(self, parent, **kwargs):
        """Setup the right preview panel
        
        Args:
            parent: tk.Frame
                Parent frame to contain the panel
            **kwargs: dict
                UI settings to use for this panel
        """
        # Merge default settings with any provided kwargs
        ui = self.ui.copy()
        ui.update(kwargs)
        
        # Preview title and info
        info_frame = tk.Frame(parent, bg=ui['bg_dark'])
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        preview_label = tk.Label(
            info_frame, 
            text="🖼️ Live Preview", 
            font=ui['font_heading'], 
            bg=ui['bg_dark'], 
            fg=ui['fg_accent']
        )
        preview_label.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            info_frame, 
            text="Ready", 
            font=ui['font_normal'], 
            bg=ui['bg_dark'], 
            fg=ui['fg_success']
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Preview canvas with scroll - wrap in a frame to ensure it expands properly
        canvas_frame = tk.Frame(
            parent, 
            bg=ui['bg_dark'], 
            relief='sunken', 
            bd=ui['border_width']
        )
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Make the canvas frame expandable in both directions
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas with scrollbars
        self.preview_canvas = tk.Canvas(
            canvas_frame, 
            bg='#000000', 
            highlightthickness=ui['highlight_thickness'], 
            cursor='crosshair'
        )
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.preview_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(
            yscrollcommand=v_scrollbar.set, 
            xscrollcommand=h_scrollbar.set
        )
        
        # Grid-based layout for better expansion behavior
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind click events for zooming
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        self.preview_canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.preview_canvas.bind("<MouseWheel>", self.on_canvas_scroll)
        
        # Bind canvas resize event to update display
        self.preview_canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Instructions
        instructions_frame = tk.Frame(parent, bg=ui['bg_dark'])
        instructions_frame.pack(fill=tk.X, pady=(10, 0))
        
        instructions_text = "🖱️ Click to zoom in • Right-click to zoom out • Scroll wheel to zoom"
        instructions_label = tk.Label(
            instructions_frame, 
            text=instructions_text, 
            font=ui['font_small'], 
            bg=ui['bg_dark'], 
            fg=ui['fg_muted']
        )
        instructions_label.pack()

    def update_mandelbrot(self):
        """Update the mandelbrot set in a background thread"""
        self.update_pending = False
        
        if self.is_computing:
            return
        
        # Get the current canvas dimensions
        self.preview_canvas.update_idletasks()
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Apply quality adjustments based on preview quality setting
        render_width = canvas_width
        render_height = canvas_height
        
        # Adjust resolution based on quality setting
        if self.preview_quality == "Low":
            render_width = int(canvas_width * 0.5)
            render_height = int(canvas_height * 0.5)
        elif self.preview_quality == "High":
            render_width = int(canvas_width * 1.5)
            render_height = int(canvas_height * 1.5)
        
        # Only update canvas dimensions if they're valid
        if canvas_width > 50 and canvas_height > 50:
            self.canvas_width = canvas_width
            self.canvas_height = canvas_height
            
            # Set Mandelbrot resolution to match the render dimensions
            self.mandelbrot.xpixels = render_width
            self.mandelbrot.ypixels = render_height
            
            # Update oversampling
            self.mandelbrot.os = self.oversampling
            
            # Adjust the coordinate system to maintain proper aspect ratio
            current_coords = self.mandelbrot.coord
            
            # Calculate center point of current view
            center_x = (current_coords[0] + current_coords[1]) / 2
            center_y = (current_coords[2] + current_coords[3]) / 2
            
            # Calculate the x-range (width) of the current view
            x_range = current_coords[1] - current_coords[0]
            
            # Calculate new y-range based on canvas aspect ratio
            aspect_ratio = canvas_height / canvas_width
            new_y_range = x_range * aspect_ratio
            
            # Update coordinates to maintain center point with new aspect ratio
            self.mandelbrot.coord = (
                center_x - x_range/2,  # x_min
                center_x + x_range/2,  # x_max
                center_y - new_y_range/2,  # y_min
                center_y + new_y_range/2   # y_max
            )
        
        self.is_computing = True
        self.status_label.config(text="Computing...", fg=self.ui['fg_warning'])
        
        # Start computation in background thread
        thread = threading.Thread(target=self.compute_mandelbrot, daemon=True)
        thread.start()
        
        # Check for completion
        self.root.after(100, self.check_computation)
        
    def compute_mandelbrot(self):
        """Compute mandelbrot set in background thread"""
        try:
            # Update the set with the current parameters
            self.mandelbrot.update_set()
            
            # Convert the NumPy array to a PIL Image
            # Flip Y-axis for proper display orientation
            image_array = self.mandelbrot.set[::-1, :, :]
            image = Image.fromarray(image_array, 'RGB')
            
            # Put the result in the queue for the main thread to pick up
            self.computation_queue.put(('success', image))
        except Exception as e:
            # If any error occurs, put it in the queue for the main thread to handle
            self.computation_queue.put(('error', str(e)))
    
    def check_computation(self):
        """Check if computation is complete"""
        try:
            status, result = self.computation_queue.get_nowait()
            self.is_computing = False
            
            if status == 'success':
                self.current_image = result
                self.display_image()
                self.update_info_display()
                self.status_label.config(text="Ready", fg=self.ui['fg_success'])
            else:
                self.status_label.config(text=f"Error: {result}", fg=self.ui['fg_error'])
                messagebox.showerror("Computation Error", f"Failed to compute Mandelbrot set:\n{result}")
        except queue.Empty:
            # Still computing
            self.root.after(100, self.check_computation)
    
    def display_image(self):
        """Display the computed image on canvas with no scaling (100% size)"""
        if self.current_image:
            # Force canvas to update its dimensions first
            self.preview_canvas.update_idletasks()
            
            # Get actual canvas dimensions
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Only proceed if canvas has valid dimensions
            if canvas_width > 50 and canvas_height > 50:  # Reasonable minimum size
                # Since our Mandelbrot computation should exactly match the canvas size,
                # we can display the image at 100% without scaling
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(self.current_image)
                
                # Clear canvas and add image
                self.preview_canvas.delete("all")
                
                # Position image at top-left (no scaling or centering needed)
                self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                
                # Update scroll region to match canvas size
                self.preview_canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
                
                # Keep a reference to prevent garbage collection
                self.preview_canvas.image = photo
                
                # Store the coordinate conversion info (1:1 mapping now)
                self.image_scale = 1.0
                self.image_offset_x = 0
                self.image_offset_y = 0
                self.scaled_image_width = self.current_image.width
                self.scaled_image_height = self.current_image.height
            else:
                print(f"Canvas too small: {canvas_width}x{canvas_height}, skipping display")
    
    def canvas_to_complex(self, canvas_x, canvas_y):
        """Convert canvas coordinates to complex plane coordinates"""
        if not self.current_image:
            return None, None
        
        # Since we're now using 1:1 mapping (no scaling or offsets),
        # canvas coordinates are the same as image coordinates
        image_x = canvas_x
        image_y = canvas_y
        
        # Check if click is within the actual image bounds
        if (image_x < 0 or image_x >= self.current_image.width or 
            image_y < 0 or image_y >= self.current_image.height):
            return None, None
        
        # Convert to complex plane coordinates
        coord = self.mandelbrot.coord
        x_ratio = image_x / self.current_image.width
        y_ratio = image_y / self.current_image.height
        
        complex_x = coord[0] + x_ratio * (coord[1] - coord[0])
        complex_y = coord[2] + (1 - y_ratio) * (coord[3] - coord[2])  # Flip Y
        
        return complex_x, complex_y
    
    def on_canvas_resize(self, event):
        """Handle canvas resize events by triggering a full recomputation"""
        # Only handle resize events from the canvas itself, not child widgets
        if event.widget == self.preview_canvas:
            # Cancel any pending resize job
            if hasattr(self, '_resize_job') and self._resize_job:
                self.root.after_cancel(self._resize_job)
                
            # Store the new canvas dimensions
            self.canvas_width = event.width
            self.canvas_height = event.height
                
            # During continuous resize, we don't want to recalculate for every tiny change
            # Schedule an update with a delay to prevent excessive computations
            if not self.is_computing:
                self._resize_job = self.root.after(200, self.schedule_update)
    
    def save_current_view(self):
        """Save current view to history"""
        # Save current coordinates to history
        if len(self.zoom_history) >= self.max_history:
            self.zoom_history.pop(0)  # Remove oldest entry if history is full
        
        self.zoom_history.append(list(self.mandelbrot.coord))

    def reset_to_home(self):
        """Reset to the original home view while maintaining canvas aspect ratio"""
        if not self.is_computing:
            self.save_current_view()
            
            # Get current canvas aspect ratio
            self.preview_canvas.update_idletasks()
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 50 and canvas_height > 50:
                # Update the Mandelbrot resolution to match the canvas exactly
                self.mandelbrot.xpixels = canvas_width
                self.mandelbrot.ypixels = canvas_height
                
                aspect_ratio = canvas_height / canvas_width
                
                # Get original coordinates
                x_min, x_max, y_min, y_max = self.home_coords
                
                # Calculate center point of original view
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                
                # Calculate width of original view
                x_range = x_max - x_min
                
                # Calculate new y_range to match canvas aspect ratio
                new_y_range = x_range * aspect_ratio
                
                # Set new coordinates maintaining center point and x-range but adjusting y-range
                self.mandelbrot.coord = (
                    x_min,
                    x_max,
                    center_y - new_y_range/2,
                    center_y + new_y_range/2
                )
            else:
                # If canvas dimensions are not valid, use original coordinates
                self.mandelbrot.coord = list(self.home_coords)
                
            self.zoom_level = 1.0
            
            # Reset iterations to base value
            self.mandelbrot.maxiter = self.base_iterations
            if hasattr(self, 'iter_slider'):
                self.iter_slider.set(self.base_iterations)
                
            self.schedule_update()

    # Implement minimal placeholders for export and navigation sections
    def setup_export_section(self, parent, **kwargs):
        """Setup export controls"""
        # Minimal implementation to avoid errors
        ui = self.ui.copy()
        ui.update(kwargs)
        
        section_frame = self.create_section(parent, "💾 Export", **kwargs)
        
        # Just add a simple button for now
        export_btn = self.create_button(
            section_frame, 
            "🖼️ Save Image", 
            self.export_image,
            bg_color=ui['color_button_save']
        )
        export_btn.pack(fill=tk.X, pady=ui['padding_control'])
        
    def setup_navigation_section(self, parent, **kwargs):
        """Setup navigation controls"""
        # Minimal implementation to avoid errors
        ui = self.ui.copy()
        ui.update(kwargs)
        
        section_frame = self.create_section(parent, "🧭 Navigation", **kwargs)
        
        # Just add a simple label for now
        nav_label = tk.Label(
            section_frame,
            text="Use mouse to navigate: click to zoom in, right-click to zoom out",
            wraplength=ui['panel_width'] - 40,
            bg=ui['bg_panel'],
            fg=ui['fg_muted'],
            pady=10
        )
        nav_label.pack()
        
    def export_image(self):
        """Minimal export function"""
        if self.current_image:
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
                )
                if filename:
                    self.current_image.save(filename)
                    self.status_label.config(text="Image saved!", fg=self.ui['fg_success'])
                    self.root.after(2000, lambda: self.status_label.config(text="Ready", fg=self.ui['fg_success']))
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
    
    def schedule_update(self):
        """Schedule a mandelbrot update with a short delay to batch multiple requests"""
        if not self.update_pending:
            self.update_pending = True
            self.root.after(100, self.update_mandelbrot)  # Small delay to batch updates
    
    def update_info_display(self):
        """Update coordinate and zoom displays"""
        coord = self.mandelbrot.coord
        coord_text = f"Real: [{coord[0]:.6f}, {coord[1]:.6f}]\nImag: [{coord[2]:.6f}, {coord[3]:.6f}]"
        self.coord_label.config(text=coord_text)
        
        zoom_text = f"Zoom: {self.zoom_level:.1f}x"
        self.zoom_label.config(text=zoom_text)

    def on_canvas_click(self, event):
        """Handle left click on canvas - zoom in"""
        if self.current_image and not self.is_computing:
            # Convert canvas coordinates to complex plane coordinates
            x, y = self.canvas_to_complex(event.x, event.y)
            if x is not None and y is not None:
                self.save_current_view()
                self.mandelbrot.zoom_at(x, y, 0.25)  # 4x zoom in
                self.zoom_level *= 4
                # Update iterations based on zoom level if dynamic iterations is enabled
                self.update_dynamic_iterations()
                self.schedule_update()
    
    def on_canvas_right_click(self, event):
        """Handle right click on canvas - zoom out"""
        if self.current_image and not self.is_computing:
            # Convert canvas coordinates to complex plane coordinates
            x, y = self.canvas_to_complex(event.x, event.y)
            if x is not None and y is not None:
                self.save_current_view()
                self.mandelbrot.zoom_at(x, y, 4.0)  # 4x zoom out
                self.zoom_level /= 4
                # Update iterations based on zoom level if dynamic iterations is enabled
                self.update_dynamic_iterations()
                self.schedule_update()
    
    def on_canvas_scroll(self, event):
        """Handle mouse wheel on canvas"""
        if self.current_image and not self.is_computing:
            x, y = self.canvas_to_complex(event.x, event.y)
            if x is not None and y is not None:
                self.save_current_view()
                if event.delta > 0:
                    # Zoom in
                    self.mandelbrot.zoom_at(x, y, 0.5)
                    self.zoom_level *= 2
                else:
                    # Zoom out
                    self.mandelbrot.zoom_at(x, y, 2.0)
                    self.zoom_level /= 2
                # Update iterations based on zoom level if dynamic iterations is enabled
                self.update_dynamic_iterations()
                self.schedule_update()

def main():
    """Main application entry point"""
    print("Starting Mandelbrot Explorer GUI...")
    try:
        root = tk.Tk()
        print("Tkinter root window created")
        
        # Center the window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        width = 1400
        height = 900
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Ensure the window is visible and in normal state
        root.update()
        root.deiconify()
        
        print("Creating application...")
        app = ModernMandelbrotGUI(root)
        print("Application created, starting main loop...")
        
        # Make sure the window has focus
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        root.mainloop()
        print("Main loop exited")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
