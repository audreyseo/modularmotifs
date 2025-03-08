from modularmotifs.dsl._syntax import *
from modularmotifs.dsl._syntax import FreshVar, Operation, Variable

class ColorOp(Operation):
    c: Variable
    
    
    def __init__(self, c: Variable, op_name: str, fresh: FreshVar):
        super().__init__(op_name, fresh)
        # the colorization variable that the color op is being done on
        self.c = c
        
    pass

class SwapColors(ColorOp):
    cindex1: Expr
    cindex2: Expr
    
    def __init__(self, c: Variable, cindex1: Expr, cindex2: Expr,  fresh: FreshVar):
        super().__init__(c, "swap_colors", fresh)
        self.cindex1 = cindex1
        self.cindex2 = cindex2
        pass
    
    def inverse(self) -> ColorOp:
        return SwapColors(self.c, self.cindex2, self.cindex1, self.fresh)
    
    def to_python(self) -> str:
        return f"{self.c}.{self.op_name}({self.cindex1}, {self.cindex2})"
    pass

class AddColor(ColorOp):
    v: Variable
    color: Expr
    
    def __init__(self, v: Variable, c: Variable, color: Expr, fresh: FreshVar):
        super().__init__(c, "add_color", fresh)
        self.v = v
        self.color = color
        pass
    
    def inverse(self) -> Operation:
        return RemoveColor(Variable(self.fresh.get_fresh()),
                           self.c,
                           self.v,
                           self.fresh)
    
    def to_python(self) -> str:
        return f"{self.v} = {self.c}.{self.op_name}({self.color})"
    pass

class RemoveColor(ColorOp):
    color: Variable
    index: Expr
    
    def __init__(self, color: Variable, c: Variable, index: Expr, fresh: FreshVar):
        super().__init__(c, "remove_color", fresh)
        self.color = color
        self.index = index
        pass
    
    def inverse(self) -> Operation:
        return AddColor(Variable(self.fresh.get_fresh()),
                        self.c,
                        self.color,
                        self.fresh)
    
    def to_python(self) -> str:
        return f"{self.color} = {self.c}.{self.op_name}({self.index})"

class AddChanges(ColorOp):
    v: Variable
    change: Expr
    row: Optional[Expr]
    fg: Optional[Expr]
    bg: Optional[Expr]
    
    def __init__(self, v: Variable, c: Variable, change: Expr, fresh: FreshVar, row: Optional[Expr] = None, fg: Optional[Expr]=None, bg: Optional[Expr]=None):
        super().__init__(c, "add_changes", fresh)
        self.v = v
        self.row = row
        self.fg = fg
        self.bg = bg
        pass
    
    def get_args(self) -> list[Expr]:
        args = [self.change]
        if self.row:
            args.append(self.row)
            pass
        if self.fg:
            args.append(self.fg)
            pass
        if self.bg:
            args.append(self.bg)
            pass
        return args
    
    def inverse(self) -> Operation:
        return RemoveChanges(Variable(self.fresh.get_fresh()),
                             Variable(self.fresh.get_fresh()),
                             Variable(self.fresh.get_fresh()),
                             Variable(self.fresh.get_fresh()),
                             self.c,
                             self.fresh,
                             row=self.v)
    
    def to_python(self) -> str:
        args = self.get_args()
        
        return f"{self.v} = {self.c}.{self.op_name}({", ".join(list(map(lambda x: x.to_python(), args)))})"
    
class RemoveChanges(ColorOp):
    last: Variable
    change: Variable
    fg: Variable
    bg: Variable
    row: Optional[Expr]
    
    def __init__(self, last: Variable, change: Variable, fg: Variable, bg: Variable, c: Variable, fresh: FreshVar, row: Optional[Expr] = None):
        super().__init__(c, "remove_changes", fresh)
        self.last = last
        self.change = change
        self.fg = fg
        self.bg = bg
        self.row = row
        pass
    
    def inverse(self) -> Operation:
        return AddChanges(Variable(self.fresh.get_fresh()),
                          self.c,
                          self.change,
                          self.fresh,
                          row=self.row,
                          fg=self.fg,
                          bg=self.bg)
    
    def get_args(self) -> list[Expr]:
        args = []
        if self.row:
            args.append(self.row)
            pass
        return args
    
    def to_python(self) -> str:
        args = self.get_args()
        args = [x.to_python() for x in args]
        
        return f"{self.last}, {self.change}, {self.fg}, {self.bg} = {self.c}.{self.op_name}({", ".join(args)})"