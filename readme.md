# Mandelbrot Fractal Explorer

A modern, interactive Mandelbrot explorer with GPU acceleration, real-time preview, and click-to-zoom. Includes both a GUI and a Matplotlib interface.

## Project direction
- I intend to make this a cool math graphing tool focused on fractals.
- I will implement more functions that allow you to change equation parameters and explore related fractals.

## Features
- GPU and CPU acceleration via Numba (CUDA when available)
- Modern GUI with interactive navigation and real-time preview
- Original Matplotlib interface for scripted exploration
- Smooth iteration coloring, optional oversampling anti-aliasing
- Shading: Blinn-Phong and Lambert lighting, stripe average coloring, step shading
- Color themes and customizable palettes
- High precision (float64) for deep zooms
- Background processing and responsive UI
- System monitoring (processing, memory, and accelerator usage)

## Quick start

### Option A: Modern GUI (recommended)
- Windows: double-click `start_gui.bat`
- Or from terminal:
  - `python launch.py`
  - or: `python mandelbrot_modern_gui.py`
  - or (in some versions): `python mandelbrot_gui.py`

### Option B: Original Matplotlib interface

```python
from mandelbrot import Mandelbrot
mand = Mandelbrot()  # set gpu=False if no GPU is available

# Explore interactively
mand.explore()

# Draw a still image
mand.draw('mandelbrot.png')
```

## Modern GUI usage

### Interactive navigation
- Click to zoom in at a point
- Right-click to zoom out
- Mouse wheel to zoom smoothly
- Reset to return to the default view
- Preview fits completely within the window

### Visual controls
- Iterations: 100–5000
- Resolution presets for preview
- Stripe and step effects, color cycling
- Lighting effects: azimuth, elevation, intensity
- Color themes (8 presets) and palette controls

### Presets
- Seahorse Valley, Lightning, Spiral, Mini Mandelbrot, Elephant Valley, Fractal Coastline

### Export
- Set a custom export directory
- Save images at 720p, 1080p, 1440p, or 4K
- Create zoom animations (GIF) with 10–200 frames
- Formats: PNG, JPEG, GIF

### System monitoring (GUI)
- Processing usage
- Memory usage
- Accelerator usage (when available)

## Command line reference

Launch the modern GUI

```shell
python launch.py
```

Launch the original interface

```shell
python ./mandelbrot.py
```

## Example: simple animation (compact)

```python
mand = Mandelbrot(maxiter=5000, xpixels=426, stripe_s=5)
# Zoom target
x_real = -1.749705768080503
x_imag = -6.13369029080495e-05
mand.animate(x_real, x_imag, 'mandelbrot.gif')
```

## Color themes
- Classic, Fire, Ocean, Forest, Purple, Sunset, Electric, Copper

## Technical notes
- GPU acceleration via CUDA when available
- Memory-efficient background computation for a responsive GUI
- Float64 numerical stability for deep zooms

## Tips
- Start with presets, then fine-tune nearby
- Increase iterations for deeper zooms
- Experiment with color themes, stripe, and step settings
- Right-click to zoom out
- Save interesting views as you explore

## Runtime
- As a reference, generating about 100 frames at 1280×720 with 2000 iterations can complete in about a second on certain data center GPUs (e.g., Tesla K80), depending on configuration.

## Requirements

### Core dependencies
- numpy
- matplotlib
- numba
- pillow
- imageio

### Optional (GUI enhancements)
- psutil
- pynvml

### Hardware
- Optional: CUDA-capable GPU and CUDA Toolkit for faster rendering

### Installation
```bash
pip install -r requirements.txt
# or
pip install numpy matplotlib numba pillow imageio psutil pynvml
```

## Notes
- The preview is optimized for responsiveness; final exports render at target resolution and quality.
- If you do not have a CUDA GPU, set gpu=False or run CPU-only modes.
                           -1.8709580332005737e-06])
mand.draw('octogone.png')
```
![](img/octogone.png)

```python
mand = Mandelbrot(maxiter = 5000, rgb_thetas = [.87, .83, .77],
                  coord = [-1.9415524417847085,
                           -1.9415524394561112,
                           0.00013385928801614168,
                           0.00013386059768851223])
mand.draw('julia.png')
```
![](img/julia.png)

```python
mand = Mandelbrot(maxiter = 5000, rgb_thetas = [.54, .38, .35], stripe_s = 8,
                  coord = [-0.19569582393630502,
                           -0.19569331188751315,
                           1.1000276413181806,
                           1.10002905416902])
mand.draw('lightning.png')
```
![](img/lightning.png)

```python
mand = Mandelbrot(maxiter = 5000, rgb_thetas = [.47, .51, .63], step_s = 20,
                  coord = [-1.7497082019887222,
                           -1.749708201971718,
                           -1.3693697170765535e-07,
                           -1.369274301311596e-07])
mand.draw('web.png')
```
![](img/web.png)

```python
mand = Mandelbrot(maxiter = 5000, rgb_thetas = [.6, .57, .45], stripe_s = 12,
                  coord = [-1.8605721473418524,
                           -1.860572147340747,
                           -3.1800170324714687e-06,
                           -3.180016406837821e-06])
mand.draw('wave.png')
```
![](img/wave.png)

```python
mand = Mandelbrot(maxiter = 5000, rgb_thetas = [.63, .83, .98],
                  coord = [-0.7545217835886875,
                           -0.7544770820676441,
                           0.05716740181493137,
                           0.05719254327783547])
mand.draw('tiles.png')
```
![](img/tiles.png)

```python
mand = Mandelbrot(maxiter = 5000, rgb_thetas = [.29, .52, .59], stripe_s = 5,
                  coord = [-1.6241199193994318,
                           -1.624119919281773,
                           -0.00013088931048083944,
                           -0.0001308892443058033])
mand.draw('velvet.png')
```
![](img/velvet.png)

## Runtime 🚀

Computing a sequence of `100` frames of HD pictures (`1280*720` pixels), with `2000` iterations takes approximately **1 second** on a Tesla K80 GPU.

## Requirements

### Core Dependencies
- NumPy
- Matplotlib
- Numba
- Pillow (PIL)
- imageio

### Optional Dependencies (for enhanced GUI features)
- psutil (for system monitoring)
- pynvml (for detailed accelerator monitoring)

### Hardware Requirements
- (optional, for much faster rendering) A CUDA compatible GPU & CUDA Toolkit

### Installation

Install all dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install numpy matplotlib numba pillow imageio psutil pynvml
```
