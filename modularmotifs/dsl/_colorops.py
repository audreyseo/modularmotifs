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

    def __init__(self, c: Variable, cindex1: Expr, cindex2: Expr, fresh: FreshVar):
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
        return RemoveColor(Variable(self.fresh.get_fresh()), self.c, self.v, self.fresh)

    def to_python(self) -> str:
        return f"{self.v} = {self.c}.{self.op_name}({self.color})"

    pass


@dataclass
class RemoveColor(ColorOp):
    color: Variable
    c: Variable
    index: Expr
    fresh: FreshVar

    def __init__(self, color: Variable, c: Variable, index: Expr, fresh: FreshVar):
        super().__init__(c, "remove_color", fresh)
        self.color = color
        self.index = index
        pass

    def inverse(self) -> Operation:
        return AddColor(
            Variable(self.fresh.get_fresh()), self.c, self.color, self.fresh
        )

    def to_python(self) -> str:
        return f"{self.color} = {self.c}.{self.op_name}({self.index})"


@dataclass
class AddChanges(ColorOp):
    v: Variable
    c: Variable
    change: Expr
    fresh: FreshVar
    row: Optional[Expr]
    fg: Optional[Expr]
    bg: Optional[Expr]

    def __init__(
        self,
        v: Variable,
        c: Variable,
        change: Expr,
        fresh: FreshVar,
        row: Optional[Expr] = None,
        fg: Optional[Expr] = None,
        bg: Optional[Expr] = None,
    ):
        super().__init__(c, "add_changes", fresh)
        self.v = v
        self.change = change
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
        return RemoveChanges(
            Variable(self.fresh.get_fresh()),
            Variable(self.fresh.get_fresh()),
            Variable(self.fresh.get_fresh()),
            Variable(self.fresh.get_fresh()),
            self.c,
            self.fresh,
            row=self.v,
        )

    def to_python(self) -> str:
        args = self.get_args()

        return f"{self.v} = {self.c}.{self.op_name}({", ".join(list(map(lambda x: x.to_python(), args)))})"


@dataclass
class RemoveChanges(ColorOp):
    last: Variable
    change: Variable
    fg: Variable
    bg: Variable
    c: Variable
    fresh: FreshVar
    row: Optional[Expr]

    def __init__(
        self,
        last: Variable,
        change: Variable,
        fg: Variable,
        bg: Variable,
        c: Variable,
        fresh: FreshVar,
        row: Optional[Expr] = None,
    ):
        super().__init__(c, "remove_changes", fresh)
        self.last = last
        self.change = change
        self.fg = fg
        self.bg = bg
        self.row = row
        pass

    def inverse(self) -> Operation:
        return AddChanges(
            Variable(self.fresh.get_fresh()),
            self.c,
            self.change,
            self.fresh,
            row=self.row,
            fg=self.fg,
            bg=self.bg,
        )

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

    def __init__(
        self,
        old_change: Variable,
        c: Variable,
        new_change: Expr,
        row: Expr,
        fresh: FreshVar,
    ):
        super().__init__(c, "set_changes", fresh)
        self.old_change = old_change
        self.new_change = new_change
        self.row = row
        pass

    def inverse(self) -> Operation:
        return SetChanges(
            Variable(self.fresh.get_fresh()),
            self.c,
            self.old_change,
            self.row,
            self.fresh,
        )

    def to_python(self) -> str:
        return f"{self.old_change} = {self.c}.{self.op_name}({self.new_change}, {self.row})"


@dataclass
class ColorOpBlock(ColorOp):
    c: Variable
    fresh: FreshVar
    ops: list[ColorOp]

    def __init__(self, c: Variable, fresh: FreshVar, *ops):
        super().__init__(c, "dummy", fresh)
        self.ops = list(ops)
        pass

    def inverse(self) -> Operation:
        return self.__class__.__init__(
            self.c, self.fresh, *[op.inverse() for op in self.ops].reverse()
        )

    def to_python(self) -> str:
        ops = [op.to_python() for op in self.ops]
        return "\n".join(ops)


class ColorizationInterpreter(DesignInterpreter):
    _builder: "ColorizationProgramBuilder"
    _vars_to_objs: dict[str, Any]

    def __init__(self, builder: "ColorizationProgramBuilder"):
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
            print(type(e), e)
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
            case RemoveColor(color, c, index, _):
                res = self.eval(c).remove_color(self.eval(index))
                self._vars_to_objs[color.name] = res
            case AddChanges(v, c, change, _, row, fg, bg):
                args = [change, row, fg, bg]
                args = [a for a in args if a]
                args = [self.eval(arg) for arg in args]
                res = self.eval(c).add_changes(*args)
                self._vars_to_objs[v.name] = res


class ColorizationProgramBuilder:
    """Helps you build a Colorization program and manages user state"""

    _pretty: PrettierTwoColorRows
    _pretty_var: Variable
    _actions: list[ColorOp]
    _original_changes: list[Change]
    _index: int
    _fresh: FreshVar
    _current_block: Optional[list[ColorOp]] = None

    def __init__(self, pretty: PrettierTwoColorRows):
        self.cname = self.__class__.__qualname__
        self._pretty = pretty
        self._actions = list()
        self._original_changes = copy.deepcopy(self._pretty._changes)
        self._index = -1
        self._fresh = FreshVar()
        self._pretty_var = Variable(self._fresh.get_fresh())
        pass

    def started_block(self):
        return self._current_block is not None

    def start_block(self):
        """Start a block of operations that can be added all at once.

        Subsequent calls that add actions will add the actions to this new block instead.
        """
        assert (
            not self.started_block()
        ), f"{self.cname}.start_block: operation block already started!"
        self._current_block = []
        pass

    def abort_block(self):
        """Abort the block that is currently being worked on

        This is unrecoverable! All actions in the currently working block will be lost.
        """
        assert (
            self.started_block()
        ), f"{self.cname}.abort_block: operation block never started!"
        self._current_block = None
        pass

    def end_block(self):
        """End the block that is currently being worked on, and add it to the list of actions.

        Subsequent calls that add actions will add them to the actions list once more.
        """
        assert (
            self.started_block()
        ), f"{self.cname}.end_block: operation block never started!"
        current_block = self._current_block
        self._current_block = None
        self._add_action(ColorOpBlock(self._pretty_var, self._fresh, *current_block))

    def get_interpreter(self):
        return ColorizationInterpreter(self)

    def get_fresh_var(self) -> Variable:
        return Variable(self._fresh.get_fresh())

    def num_actions(self) -> int:
        return len(self._actions)

    def can_undo(self) -> bool:
        return self._index >= 0 and not self.started_block()

    def can_redo(self) -> bool:
        return self._index < self.num_actions() - 1 and not self.started_block()

    def undo(self) -> ColorOp:
        old_index = self._index
        self._index -= 1
        return self._actions[old_index].inverse()

    def redo(self) -> ColorOp:
        self._index += 1
        return self._actions[self._index]

    def _overwrite(self):
        if self._index < self.num_actions() - 1:
            self._actions = self._actions[: self._index + 1]
            pass
        pass

    def _add_action(self, op: ColorOp):
        if self.started_block():
            self._current_block.append(op)
            pass
        else:
            self._overwrite()
            self._index += 1
            self._actions.append(op)
            pass
        pass

    def _remove_last_action(self):
        if self.started_block():
            self._current_block.pop(-1)
            pass
        else:
            self._index -= 1
            self._actions.pop(-1)
            pass
        pass

    def swap_colors(self, i1: int, i2: int) -> ColorOp:
        op = SwapColors(self._pretty_var, Literal(i1), Literal(i2), self._fresh)
        self._add_action(op)
        return op

    @classmethod
    def change_to_syntax(cls, c: Change) -> Expr:
        return ObjectInit(
            "Change",
            Literal(c.row),
            ObjectAccess(
                ObjectAccess(Variable("Change"), "Permissions"), c.perms.to_str()
            ),
            ObjectAccess(
                ObjectAccess(Variable("Change"), "Necessity"), c.necc.to_str()
            ),
        )

    def set_changes(self, c: Change, row: int) -> ColorOp:
        op = SetChanges(
            self.get_fresh_var(),
            self._pretty_var,
            ColorizationProgramBuilder.change_to_syntax(c),
            Literal(row),
            self._fresh,
        )
        self._add_action(op)
        return op

    def add_changes(
        self,
        c: Change,
        row: Optional[int],
        fg: Optional[RGBAColor],
        bg: Optional[RGBAColor],
    ) -> ColorOp:
        op = AddChanges(
            self.get_fresh_var(),
            self._pretty_var,
            ColorizationProgramBuilder.change_to_syntax(c),
            self._fresh,
            row=Literal(row) if row else None,
            fg=ColorizationProgramBuilder.rgba_color_to_syntax(fg) if fg else None,
            bg=ColorizationProgramBuilder.rgba_color_to_syntax(bg) if bg else None,
        )
        self._add_action(op)
        return op

    @classmethod
    def rgba_color_to_syntax(cls, color: RGBAColor) -> Expr:
        r, g, b, alpha = color.rgba_tuple()
        return ObjectInit(
            "RGBAColor", Literal(r), Literal(g), Literal(b), Literal(alpha)
        )

    def add_color(self, color: RGBAColor) -> ColorOp:
        op = AddColor(
            self.get_fresh_var(),
            self._pretty_var,
            ColorizationProgramBuilder.rgba_color_to_syntax(color),
            self._fresh,
        )
        self._add_action(op)
        return op

    def remove_color(self, index: int) -> ColorOp:
        op = RemoveColor(
            self.get_fresh_var(), self._pretty_var, Literal(index), self._fresh
        )
        self._add_action(op)
        return op


if __name__ == "__main__":
    p = PrettierTwoColorRows(
        Design(10, 10),
        [
            RGBAColor.from_hex("#FFFFFF"),
            RGBAColor.from_hex("#FF00FF"),
            RGBAColor.from_hex("#00FF00"),
        ],
        [
            Change.from_ints(0, 1, 1),
            Change.from_ints(2, 3, 1),
            Change.from_ints(4, 4, 2),
        ],
    )

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
