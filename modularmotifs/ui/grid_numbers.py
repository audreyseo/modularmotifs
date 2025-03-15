import tkinter as tk
import tkinter.font as tkfont

class GridNumbers:
    def __init__(self, frame: tk.Frame, horizontal_numbers: int, vertical_numbers: int, w: int, h: int, small_w: int, small_h: int):
        self.__frame = frame
        self.__top_numbers = tk.Canvas(self.__frame)
        self.__bottom_numbers = tk.Canvas(self.__frame)
        self.__left_numbers = tk.Canvas(self.__frame)
        self.__right_numbers = tk.Canvas(self.__frame)
        self.__top = []
        self.__bottom = []
        self.__left = []
        self.__right = []
        self.__font = tkfont.Font(font=("Courier New", 8))
        print(tkfont.families())
        
        self.__top_numbers.configure(width=w, height=small_h)
        self.__bottom_numbers.configure(width=w, height=small_h)
        self.__left_numbers.configure(width=small_w, height=h)
        self.__right_numbers.configure(width=small_w, height=h)
        
        for i in range(horizontal_numbers):
            self.add_top(i, small_w * 0.5 + i * small_w, small_h * 0.5)
            self.add_bottom(i, small_w * 0.5 + i * small_w, small_h * 0.5)
            pass
        for i in range(vertical_numbers):
            self.add_left(i, small_w * 0.9, small_h * 0.5 + i * small_h)
            self.add_right(i, small_w * 0.1, small_h * 0.5 + i * small_h)
        
        pass
    
    def add_left(self, num: int, x: int, y: int):
        self.__left.append(self.__left_numbers.create_text(x, y, text=str(num), anchor="e", font=self.__font))
        pass
    
    def add_right(self, num: int, x: int, y: int):
        self.__right.append(self.__right_numbers.create_text(x, y, text=str(num), anchor="w", font=self.__font))
        pass
    
    def add_bottom(self, num: int, x: int, y: int):
        self.__bottom.append(self.__bottom_numbers.create_text(x, y, text=str(num), font=self.__font))
        pass
    
    def add_top(self, num: int, x: int, y: int):
        self.__top.append(self.__top_numbers.create_text(x, y, text=str(num), font=self.__font))
        pass
    
    
    def get_top(self) -> tk.Canvas:
        return self.__top_numbers
    
    def get_bottom(self) -> tk.Canvas:
        return self.__bottom_numbers
    
    def get_left(self) -> tk.Canvas:
        return self.__left_numbers
    
    def get_right(self) -> tk.Canvas:
        return self.__right_numbers