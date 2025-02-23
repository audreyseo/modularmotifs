import tkinter as tk
from typing import Optional

class GridLabels:
    top_labels: list[tk.Label]
    bottom_labels: list[tk.Label]
    right_labels: list[tk.Label]
    left_labels: list[tk.Label]
    
    def __init__(self):
        self.top_labels = []
        self.bottom_labels = []
        self.right_labels = []
        self.left_labels = []
        pass
    
    def add_top_label(self, l: tk.Label):
        self.top_labels.append(l)
        pass
    
    def add_bottom_label(self, l: tk.Label):
        self.bottom_labels.append(l)
        pass
    
    def add_right_label(self, l: tk.Label):
        self.right_labels.append(l)
        pass
    
    def add_left_label(self, l: tk.Label):
        self.left_labels.append(l)
        pass
    
    def add_tb_label(self, l: tk.Label, row: int):
        if row == -1:
            self.add_top_label(l)
            pass
        else:
            self.add_bottom_label(l)
            pass
        pass
    
    def add_lr_label(self, l: tk.Label, col: int):
        if col == -1:
            self.add_left_label(l)
            pass
        else:
            self.add_right_label(l)
            pass
        pass
    
    def get_lr_labels(self, row: int):
        return self.left_labels[row], self.right_labels[row]
    
    def get_tb_labels(self, col: int):
        return self.top_labels[col], self.bottom_labels[col]
    
    def grid_remove_lr(self, row: int):
        self.left_labels[row].grid_remove()
        self.right_labels[row].grid_remove()
        pass
    
    def grid_remove_tb(self, col: int):
        self.top_labels[col].grid_remove()
        self.bottom_labels[col].grid_remove()
        pass
    
    def grid_remove_right(self):
        for l in self.right_labels:
            l.grid_remove()
            pass
        pass
    
    def grid_remove_bottom(self):
        for l in self.bottom_labels:
            l.grid_remove()
            pass
        pass
    
    def get_bottom_label(self, col: int):
        return self.bottom_labels[col]
    def get_top_label(self, col: int):
        return self.top_labels[col]
    def get_right_label(self, row: int):
        return self.right_labels[row]
    def get_left_label(self, row: int):
        return self.left_labels[row]
    
    pass