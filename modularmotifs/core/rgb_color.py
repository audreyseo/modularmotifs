from typing import Self
import re

def rgba_bounded(f: float):
    return min(max(0, round(f)), 255)

class RGBAColor:
    """Simple RGB [0, 255] 4-tuple"""

    def __init__(self, red: int, green: int, blue: int, alpha: int):
        if max(red, green, blue, alpha) > 255:
            raise ValueError("RGBA coordinates must be less than 255!")
        if min(red, green, blue, alpha) < 0:
            raise ValueError("RGBA coordinates must be greater than 0!")
        self.__red = red
        self.__green = green
        self.__blue = blue
        self.__alpha = alpha

    def hex(self) -> str:
        """Returns the hex representation
        (e.g., "#3300f2") of the color's RGB

        Returns:
            String: hex representation
        """
        return "#" + "".join(
            [
                hex(p).lstrip("0x").zfill(2)
                for p in [self.__red, self.__green, self.__blue]
            ]
        )

    @classmethod
    def Back(cls) -> Self:
        return RGBAColor.from_hex("#ffffff")
    
    @classmethod
    def Fore(cls) -> Self:
        return RGBAColor.from_hex("#000000")
    
    @classmethod
    def Invis(cls) -> Self:
        return RGBAColor(128, 128, 128, 0)
    

    @classmethod
    def from_hex(cls, hexstr) -> Self:
        """Given a hex string, returns a new RGBAColor instance representing that color. Assumes full opacity (alpha=255)
        """
        assert len(hexstr) == 7 and re.match(r"#[0-9a-f]{6}", hexstr, re.I), f"RGBAColor.from_hex: hex string {hexstr} has the wrong format"
        red = int(hexstr[1:3], 16)
        green = int(hexstr[3:5], 16)
        blue = int(hexstr[5:7], 16)
        return RGBAColor(red, green, blue, 255)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.hex()})"

    def rgb_tuple(self) -> tuple[int, int, int]:
        """ Returns a tuple of the red, green, and blue parts
        """
        return (self.__red, self.__green, self.__blue)

    def rgba_tuple(self, opacity: int=255) -> tuple[int, int, int, int]:
        """ Returns a tuple of the red, green, blue, and alpha parts
        """
        return (self.__red, self.__green, self.__blue, self.__alpha if opacity == 255 else opacity)
    
    def filtered(self, r: float=1.0, g: float=1.0, b: float=1.0, a: float=1.0) -> tuple[int, int, int, int]:
        return (rgba_bounded(self.__red * r), rgba_bounded(self.__green * g), rgba_bounded(self.__blue * b), rgba_bounded(self.__alpha * a))