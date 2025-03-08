from dataclasses import dataclass
from modularmotifs.core.rgb_color import RGBAColor
from modularmotifs.dsl._syntax import *
from modularmotifs.dsl._syntax import FreshVar, Operation, Variable
from modularmotifs.core.colorization import PrettierTwoColorRows, Change
import copy

class ColorOp(Operation):
    c: Variable
    
    
    def __init__(self, c: Variable, op_name: str, fresh: FreshVar):
        super().__init__(op_name, fresh)
        # the colorization variable that the color op is being done on
        self.c = c
        
    pass

@dataclass
class SwapColors(ColorOp):
    c: Variable
    cindex1: Expr
    cindex2: Expr
    fresh: FreshVar
    
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

@dataclass
class AddColor(ColorOp):
    v: Variable
    c: Variable
    color: Expr
    fresh: FreshVar
    
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

@dataclass
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

@dataclass
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

@dataclass 
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
    pass

@dataclass
class SetChanges(ColorOp):
    old_change: Variable
    c: Variable
    new_change: Expr
    row: Expr
    fresh: FreshVar
    
    def __init__(self, old_change: Variable, c: Variable, new_change: Expr, row: Expr, fresh: FreshVar):
        super().__init__(c, "set_changes", fresh)
        self.old_change = old_change
        self.new_change = new_change
        self.row = row
        pass
    
    def inverse(self) -> Operation:
        return SetChanges(Variable(self.fresh.get_fresh()),
                          self.c,
                          self.old_change,
                          self.row,
                          self.fresh)
        
    def to_python(self) -> str:
        return f"{self.old_change} = {self.c}.{self.op_name}({self.new_change}, {self.row})"
    

class ColorizationInterpreter(DesignInterpreter):
    _builder: 'ColorizationProgramBuilder'
    _vars_to_objs: dict[str, Any]
    
    def __init__(self, builder: 'ColorizationProgramBuilder'):
        self.cn = self.__class__.__qualname__
        self._builder = builder
        self._vars_to_objs = dict()
        self._vars_to_objs[self._builder._pretty_var.name] = self._builder._pretty
        pass
    
    def eval(self, e: Expr) -> Any:
        if isinstance(e, Variable):
            return self._vars_to_objs[e.name]
        else:
            if isinstance(e, ObjectInit):
                return eval(e.to_python())
            return super().eval(e)
        
    
    def interpret(self, op: ColorOp):
        match op:
            case SwapColors(c, cindex1, cindex2, _):
                self.eval(c).swap_colors(self.eval(cindex1), self.eval(cindex2))
                pass
            case SetChanges(old, c, new, row, _):
                res = self.eval(c).set_changes(self.eval(new), self.eval(row))
                self._vars_to_objs[old.name] = res
            case AddColor(v, c, color, _):
                res = self.eval(c).add_color(self.eval(color))
                self._vars_to_objs[v.name] = res


class ColorizationProgramBuilder:
    """Helps you build a Colorization program and manages user state
    """
    _pretty: PrettierTwoColorRows
    _pretty_var: Variable
    _actions: list[ColorOp]
    _original_changes: list[Change]
    _index: int
    _fresh: FreshVar
    
    def __init__(self, pretty: PrettierTwoColorRows):
        self._pretty = pretty
        self._actions = list()
        self._original_changes = copy.deepcopy(self._pretty._changes)
        self._index = -1
        self._fresh = FreshVar()
        self._pretty_var = Variable(self._fresh.get_fresh())
        pass
    
    def get_interpreter(self):
        return ColorizationInterpreter(self)
    
    def get_fresh_var(self) -> Variable:
        return Variable(self._fresh.get_fresh())
    
    def num_actions(self) -> int:
        return len(self._actions)
    
    def can_undo(self) -> bool:
        return self._index >= 0
    
    def can_redo(self) -> bool:
        return self._index < self.num_actions() - 1
    
    def undo(self) -> ColorOp:
        old_index = self._index
        self._index -= 1
        return self._actions[old_index].inverse()
    
    def redo(self) -> ColorOp:
        self._index += 1
        return self._actions[self._index]
    
    def _add_action(self, op: ColorOp):
        self._index += 1
        self._actions.append(op)
        pass
    
    def _remove_last_action(self):
        self._index -= 1
        self._actions.pop(-1)
        pass
        
    
    def swap_colors(self, i1: int, i2: int) -> ColorOp:
        op = SwapColors(self._pretty_var,
                        Literal(i1),
                        Literal(i2),
                        self._fresh)
        self._add_action(op)
        return op
    
    def set_changes(self, c: Change, row: int) -> ColorOp:
        op = SetChanges(self.get_fresh_var(),
                        self._pretty_var,
                        ObjectInit("Change", 
                                   Literal(c.row),
                                   ObjectAccess(ObjectAccess(Variable("Change"), "Permissions"), c.perms.to_str()),
                                   ObjectAccess(ObjectAccess(Variable("Change"), "Necessity"), c.necc.to_str())
                        ),
                        Literal(row),
                        self._fresh)
        self._add_action(op)
        return op
    
    @classmethod
    def rgba_color_to_syntax(cls, color: RGBAColor) -> Expr:
        r, g, b, alpha = color.rgba_tuple()
        return ObjectInit("RGBAColor", Literal(r), Literal(g), Literal(b), Literal(alpha))
    
    def add_color(self, color: RGBAColor) -> ColorOp:
        op = AddColor(self.get_fresh_var(),
                      self._pretty_var,
                      ColorizationProgramBuilder.rgba_color_to_syntax(color),
                      self._fresh
                      )
        self._add_action(op)
        return op
    
    
    
    
    
if __name__ == "__main__":
    p = PrettierTwoColorRows(Design(10, 10), 
                             [RGBAColor.from_hex("#FFFFFF"),
                              RGBAColor.from_hex("#FF00FF"),
                              RGBAColor.from_hex("#00FF00")],
                             [Change.from_ints(0, 1, 1),
                              Change.from_ints(2, 3, 1),
                              Change.from_ints(4, 4, 2)])
    
    builder = ColorizationProgramBuilder(p)
    
    interp = builder.get_interpreter()
    
    op = builder.swap_colors(0, 1)
    interp.interpret(op)
    print(op)
    
    op = builder.set_changes(Change.from_ints(0, 3, 1), 1)
    interp.interpret(op)
    print(op)
    
    op = builder.undo()
    interp.interpret(op)
    print(op)
    
    op = builder.redo()
    interp.interpret(op)
    print(op)