import tkinter as tk
from modularmotifs.core.colorization import Change, PrettierTwoColorRows

class ChangeButtonState:
    string: tk.StringVar
    change: Change
    
    def __init__(self, string: tk.StringVar, row: int, pretty: PrettierTwoColorRows):
        self.string = string
        self.row = row
        self.pretty = pretty
        self._update_string()
        pass
    
    def change(self) -> Change:
        return self.pretty.get_change(self.row)
    
    def _update_string(self):
        # print(self.string.get())
        self.string.set(self.change().perms.to_str())
        # print(self.string.get())
        pass
    
    @classmethod
    def toggle(cls, oldchange: Change) -> Change:
        row = oldchange.row
        p = oldchange.perms.value
        n = oldchange.necc.value
        
        new_change = Change.from_ints(row, p + 1, n)
        return new_change
    
    @classmethod
    def toggle_backwards(cls, oldchange: Change) -> Change:
        row = oldchange.row
        p = oldchange.perms.value
        n = oldchange.necc.value
        
        new_change = Change.from_ints(row, p - 1, n)
        return new_change
    
    # def toggle(self, newchange: Change) -> Change:
    #     row = self.change().row
    #     p = self.change().perms.value
    #     n = self.change().necc.value
        
    #     new_change = Change.from_ints(row, p + 1, n)
    #     self._update_string()
    #     return self.change
        
        
    