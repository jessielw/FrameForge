import math


class FontScaler:
    def __init__(self, original_font_size=100, original_scale=3.5):
        self.original_font_size = original_font_size
        self.original_scale = original_scale

    def calculate_scale_factor(self, desired_font_size):
        """Calculate the scale factor based on the desired font size."""
        return math.log(desired_font_size) / math.log(self.original_font_size)

    def adjust_scale_factor(self, scale_factor, multiplier):
        """Adjust the scale factor with a multiplier."""
        return scale_factor * multiplier

    def scale_font(self, scale_factor):
        """Scale the font size based on the original scale and scale factor."""
        return self.original_scale * scale_factor

    def get_adjusted_scale(self, desired_font_size, multiplier=1.0):
        """Get the adjusted font scale based on the desired font size and multiplier."""
        scale_factor = self.calculate_scale_factor(desired_font_size)
        adjusted_scale_factor = self.adjust_scale_factor(scale_factor, multiplier)
        return self.scale_font(adjusted_scale_factor)
