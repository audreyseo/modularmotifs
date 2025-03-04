import abc
from typing import Optional, Self
from modularmotifs.core.rgb_color import RGBColor


class PixelGrid(abc.ABC):
    _name: Optional[str] = None
    
    def set_name(self, name: str) -> Self:
        self._name = name
        pass
    
    def get_name(self) -> Optional[str]:
        return self._name
    
    def has_name(self) -> bool:
        return self.get_name() is not None
    
    @abc.abstractmethod
    def width(self) -> int:
        pass
    
    @abc.abstractmethod
    def height(self) -> int:
        pass
    
    def in_range(self, x: int, y: int) -> bool:
        return 0 <= x < self.width() and 0 <= y < self.height()
    
    @abc.abstractmethod
    def get_rgb(self, x: int, y: int) -> RGBColor:
        pass
    pass

# class EditablePixelGrid(PixelGrid):
    # def set_pixel(self, )