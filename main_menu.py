#!/usr/bin/env python3

"""
Main menu screen for the Fractal Explorer app.
Shows available fractal visualizers that the user can explore.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.factory import Factory
from kivy.app import App
from kivy.properties import StringProperty

# Register the card class BEFORE it's used in any KV files
class FractalCard(BoxLayout):
    """Card showing a fractal option"""
    fractal_type = StringProperty('')
    fractal_name = StringProperty('')
    enabled = ListProperty([1, 1, 1, 1])  # RGBA: fully visible
    
    def on_touch_down(self, touch):
        """Handle touch on card - navigate to appropriate fractal"""
        if self.collide_point(*touch.pos) and self.enabled[3] > 0.5:
            if self.fractal_type == 'mandelbrot':
                self.parent.parent.parent.manager.current = 'mandelbrot_explorer'
                return True
        return super(FractalCard, self).on_touch_down(touch)

class FractalButton(Image):
    """Clickable image used in the menu to enter explorers"""
    fractal_type = StringProperty('')

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super(FractalButton, self).on_touch_down(touch)

        # Navigate based on fractal type
        app = App.get_running_app()
        if not app:
            return True

        target = None
        if self.fractal_type == 'mandelbrot':
            target = 'mandelbrot_explorer'

        if target:
            # app.root is the ScreenManager
            app.root.current = target
            return True

        return super(FractalButton, self).on_touch_down(touch)

# Register BEFORE loading KV files
Factory.register('FractalCard', cls=FractalCard)
Factory.register('FractalButton', cls=FractalButton)

class MainMenuScreen(Screen):
    """Main menu screen showing available fractal visualizers"""
    pass  # UI is defined in kv/menu.kv
