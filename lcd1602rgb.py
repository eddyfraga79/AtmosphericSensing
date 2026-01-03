import board
import busio
from circuitpython_waveshare_lcd1602 import LCD1602

# LCD_I2C_ADDRS = 0x60;
MAX_LCD_COLUMN = 16
MAX_DISPLAY_ROW = 2

class LCD1602RGB:
    def __init__(self, i2c=None):
        """Initialize the Waveshare LCD1602 RGB display."""
        self.i2c = i2c or busio.I2C(board.SCL, board.SDA)
        self.lcd = LCD1602(self.i2c)
        self.clear()
        self.set_backlight_Red()
#     rgb_display.setCursor(0, 0);

    def clear(self):
        """Clear the LCD display."""
        self.lcd.clear()

    def set_cursor(column, row):
        if column < MAX_LCD_COLUMN and  row < MAX_LCD_ROW:
            self.lcd.set_cursor(column, row)
        else
            print(f"[ERROR] Column/Row size(s) are incorrect")

    def set_backlight(self, r: int, g: int, b: int):
        """
        Set backlight color (0–255 values).
        :param r: Red channel (0–255)
        :param g: Green channel (0–255)
        :param b: Blue channel (0–255)
        """
        self.lcd.set_rgb(r, g, b)

    def set_backlight_Red(self):
        self.set_backlight(255, 0, 0)

    def set_backlight_Green(self):
        self.set_backlight(0, 255, 0)

    def set_backlight_Blue(self):
        self.set_backlight(0, 0, 255)

    def set_backlight_Purple(self):
        self.set_backlight(128, 0, 128)

    def set_backlight_Orange(self):
        self.set_backlight(255, 165, 0)

    def print(self, text: str, row=0: int = 0):
        """
        Print text to a specific line (0 or 1).
        :param text: The string to display
        :param row: Row index (0 or 1)
        """
        set_cursor(0, line)
        self.lcd.printout(text)
