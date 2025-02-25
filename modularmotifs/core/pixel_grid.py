import abc
from modularmotifs.core.rgb_color import RGBColor


class PixelGrid(abc.ABC):
    @abc.abstractmethod
    def width(self) -> int:
        pass
    
    @abc.abstractmethod
    def height(self) -> int:
        pass
    
    def in_range(self, x: int, y: int) -> bool:
        return 0 <= x < self.width() and 0 <= y < self.height()
    
    # @abc.abstractmethod
    # def get_color(self, x: int, y: int) -> int:
    #     pass
    
    @abc.abstractmethod
    def get_rgb(self, x: int, y: int) -> RGBColor:
        pass