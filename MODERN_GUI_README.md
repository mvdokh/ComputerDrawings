# Modern Mandelbrot Explorer

A modern, interactive GUI for exploring the Mandelbrot set with real-time preview and click-to-zoom functionality.

### Interactive Navigation
- **Click to Zoom In**: Left-click anywhere on the preview to zoom into that point
- **Right-click to Zoom Out**: Right-click to zoom out from that point  
- **Mouse Wheel**: Scroll to zoom in/out smoothly
- **Reset to Home**: Instantly return to the original full Mandelbrot view
- **Perfect Fit Display**: Preview always fits completely within the window

###  Real-time Visual Controls
- **Live Preview**: See changes instantly as you adjust parameters
- **Responsive Scaling**: Preview automatically scales to fit window size perfectly
- **Color Themes**: Choose from 8 beautiful preset color schemes
- **Iterations Control**: Adjust detail level (100-5000 iterations)
- **Advanced Coloring**: Stripe patterns, step shading, and color cycles
- **Lighting Effects**: Adjustable 3D-style lighting with azimuth, elevation, and intensity

###  Preset Locations
Quick navigation to interesting areas:
- **Seahorse Valley**: Classic seahorse tail formations
- **Lightning**: Electric fractal patterns  
- **Spiral**: Beautiful spiral structures
- **Mini Mandelbrot**: Self-similar mini copies
- **Elephant Valley**: Elephant-like formations
- **Fractal Coastline**: Intricate coastal boundaries

###  Export Features
- **Custom Export Path**: Set your preferred directory for all exports
- **High-Resolution Images**: Export at 720p, 1080p, 1440p, or 4K
- **Zoom Animations**: Create smooth zoom-in GIF animations
- **Multiple Formats**: Save as PNG, JPEG, or GIF

### Mordern Interface
- **Dark Theme**: Easy on the eyes for long exploration sessions
- **Clean Section Headers**: Professional, non-button-like section organization
- **Organized Controls**: Clean sections for different parameter groups
- **Real-time Status**: See computation progress and current coordinates
- **Perfect Fit Preview**: Image always scales to fit window completely

## Guide:

### Launch the Application
```bash
# Using the batch file
start_gui.bat

# Or directly with Python
python mandelbrot_modern_gui.py
```

### Basic Navigation
1. **Explore**: Click anywhere on the preview to zoom into interesting areas
2. **Adjust Parameters**: Use the sliders in the left panel to change visual appearance
3. **Try Presets**: Click preset location buttons for quick navigation to interesting spots
4. **Set Export Path**: Choose your preferred directory for saving images and animations

### Export High-Quality Images
1. Set your export path in the Export section
2. Set your desired export resolution (up to 4K)
3. Navigate to your favorite view
4. Click "Save Image" and choose your filename
5. The app will render a high-resolution version in the background

### Create Animations
1. Set your export path in the Export section
2. Navigate to an interesting starting point
3. Click "Create Animation"
4. Choose the number of frames (10-200)
5. The app will create a smooth zoom animation as a GIF

##  Color Themes

- **Classic**: Traditional blue/black Mandelbrot colors
- **Fire**: Red and orange flames
- **Ocean**: Deep blues and teals
- **Forest**: Greens and earth tones
- **Purple**: Rich purples and magentas
- **Sunset**: Orange to blue gradient
- **Electric**: Bright cyan and blue
- **Copper**: Warm metallic tones

##  Technical Features

- **GPU Acceleration**: Uses CUDA when available for fast computation
- **Background Processing**: UI stays responsive during computation
- **Memory Efficient**: Optimized for smooth performance
- **High Precision**: Support for deep zoom levels with numerical stability

## Tips for Exploration

1. **Start with presets** to see interesting areas, then explore nearby
2. **Adjust iterations** based on zoom level - deeper zooms need more iterations
3. **Try different color themes** to reveal different structural details
4. **Use the stripe and step controls** to add texture and depth
5. **Right-click to zoom out** when you've gone too deep
6. **Save interesting views** before continuing exploration

##  Requirements

- Python 3.7+
- NumPy
- Pillow (PIL)
- Numba (for GPU acceleration)
- Tkinter (usually included with Python)

##  Performance Tips

- **GPU Acceleration**: Ensure CUDA-capable GPU for best performance
- **Resolution**: Use lower preview resolution for faster real-time updates
- **Iterations**: Start with lower iterations, increase for final export
- **Background Computation**: Let computations finish before making new changes

