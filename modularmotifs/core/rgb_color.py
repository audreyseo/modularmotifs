from typing import Self

class RGBColor:
    """Simple RGB [0, 255] triple"""

    def __init__(self, red: int, green: int, blue: int):
        if max(red, green, blue) > 255:
            raise ValueError("RGB coordinates must be less than 255!")
        if min(red, green, blue) < 0:
            raise ValueError("RGB coordinates must be greater than 0!")
        self.__red = red
        self.__blue = blue
        self.__green = green

    def hex(self) -> str:
        """Returns the hex representation
        (e.g., "#3300f2") of the color

        Returns:
            String: hex representation
        """
        return "#" + "".join(
            [
                hex(p).lstrip("0x").zfill(2)
                for p in [self.__red, self.__blue, self.__green]
            ]
        )

    @classmethod
    def from_hex(cls, hexstr) -> Self:
        """Given a hex string, returns a new RGBColor instance representing that color.
        """
        assert len(hexstr) == 7 and re.match(r"#[0-9a-f]{6}", hexstr, re.I), f"RGBColor.from_hex: hex string {hexstr} has the wrong format"
        red = int(hexstr[1:3], 16)
        green = int(hexstr[3:5], 16)
        blue = int(hexstr[5:7], 16)
        return RGBColor(red, green, blue)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.hex()})"

    def tuple(self) -> tuple[int, int, int]:
        """ Returns a tuple of the red, green, and blue parts
        """
        return (self.__red, self.__green, self.__blue)