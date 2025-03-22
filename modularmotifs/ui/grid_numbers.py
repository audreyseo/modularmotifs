import tkinter as tk
import tkinter.font as tkfont


class GridNumbers:
    def __init__(
        self,
        frame: tk.Frame,
        horizontal_numbers: int,
        vertical_numbers: int,
        w: int,
        h: int,
        small_w: int,
        small_h: int,
    ):
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

        self.__small_w = small_w
        self.__small_h = small_h

        for i in range(horizontal_numbers):
            self.add_top(i)
            self.add_bottom(i)
            pass
        for i in range(vertical_numbers):
            self.add_left(i)
            self.add_right(i)

        pass

    def add_left(self, num: int):
        self.__left.append(
            self.__left_numbers.create_text(
                self.__small_w * 0.9,
                (num + 0.5) * self.__small_h,
                text=str(num),
                anchor="e",
                font=self.__font,
            )
        )
        pass

    def add_right(self, num: int):
        self.__right.append(
            self.__right_numbers.create_text(
                self.__small_w * 0.1,
                (num + 0.5) * self.__small_h,
                text=str(num),
                anchor="w",
                font=self.__font,
            )
        )
        pass

    def add_bottom(self, num: int):
        self.__bottom.append(
            self.__bottom_numbers.create_text(
                (num + 0.5) * self.__small_w,
                self.__small_h * 0.5,
                text=str(num),
                font=self.__font,
            )
        )
        pass

    def add_top(self, num: int):
        self.__top.append(
            self.__top_numbers.create_text(
                (num + 0.5) * self.__small_w,
                self.__small_h * 0.5,
                text=str(num),
                font=self.__font,
            )
        )
        pass

    def add_horizontals(self):
        # the top and bottom number lists are the horizontal ones
        new_num = len(self.__top)
        self.change_top_size(self.__small_w)
        self.change_bottom_size(self.__small_w)
        # top_config = self.__top_numbers.configure()
        # print(top_config["width"])
        # self.__top_numbers.configure(width=int(top_config["width"][-1]) + self.__small_w)
        # bottom_config = self.__bottom_numbers.configure()
        # self.__bottom_numbers.configure(width=int(bottom_config["width"][-1]) + self.__small_w)
        self.add_top(new_num)
        self.add_bottom(new_num)
        pass

    def remove_horizontals(self):
        top = self.__top.pop(-1)
        bottom = self.__bottom.pop(-1)
        self.__top_numbers.delete(top)
        self.__bottom_numbers.delete(bottom)
        self.change_bottom_size(-self.__small_w)
        self.change_top_size(-self.__small_w)
        pass

    def remove_verticals(self):
        left = self.__left.pop(-1)
        right = self.__right.pop(-1)
        self.__left_numbers.delete(left)
        self.__right_numbers.delete(right)
        self.change_right_size(-self.__small_h)
        self.change_left_size(-self.__small_h)

    def change_top_size(self, amount: int):
        top = self.__top_numbers.configure()
        self.__top_numbers.configure(width=int(top["width"][-1]) + amount)
        pass

    def change_bottom_size(self, amount: int):
        bottom = self.__bottom_numbers.configure()
        self.__bottom_numbers.configure(width=int(bottom["width"][-1]) + amount)
        pass

    def change_left_size(self, amount: int):
        left_config = self.__left_numbers.configure()
        self.__left_numbers.configure(height=int(left_config["height"][-1]) + amount)
        pass

    def change_right_size(self, amount: int):
        right_config = self.__right_numbers.configure()
        # self.__left_numbers.configure(height=int(left_config["height"][-1]) + self.__small_h)
        self.__right_numbers.configure(height=int(right_config["height"][-1]) + amount)

    def add_verticals(self):
        # the left and right number lists are the vertical ones
        new_num = len(self.__left)
        self.change_left_size(self.__small_h)
        self.change_right_size(self.__small_h)
        # left_config = self.__left_numbers.configure()
        # right_config = self.__right_numbers.configure()
        # self.__left_numbers.configure(height=int(left_config["height"][-1]) + self.__small_h)
        # self.__right_numbers.configure(height=int(right_config["height"][-1]) + self.__small_h)
        self.add_left(new_num)
        self.add_right(new_num)

    def get_top(self) -> tk.Canvas:
        return self.__top_numbers

    def get_bottom(self) -> tk.Canvas:
        return self.__bottom_numbers

    def get_left(self) -> tk.Canvas:
        return self.__left_numbers

    def get_right(self) -> tk.Canvas:
        return self.__right_numbers
