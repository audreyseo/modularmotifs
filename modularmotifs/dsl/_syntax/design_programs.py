# from modularmotifs.dsl._syntax.basic_ast import *
from modularmotifs.dsl._syntax.operations import *


class DesignInterpreter:
    design: Design
    design_var: str
    _motifs: dict[str, Motif]
    _imports: list[Import]
    _placed_motifs: dict[str, PlacedMotif]
    _classes: set[str] = set([Motif.__name__, Design.__name__])
    _builder: "DesignProgramBuilder"
    _vars_to_vals: dict[Variable, Any]

    def __init__(
        self,
        design: Design,
        design_var: str,
        motifs: dict[str, Motif],
        imports: list[Import],
        builder: "DesignProgramBuilder",
    ):
        self.cn = self.__class__.__qualname__
        self.design = design
        self.design_var = design_var
        self._motifs = motifs
        self._imports = imports
        self._placed_motifs = dict()
        self._builder = builder
        self._vars_to_vals = dict()

        pass

    def placed_name(self, pm: PlacedMotif) -> Optional[str]:
        try:
            key = next(key for key, value in self._placed_motifs.items() if value == pm)
            return key
        except StopIteration:
            return None

    def eval(self, e: Expr):
        def map_eval_over(itr: list[Expr]):
            return list(map(lambda x: self.eval(x), itr))

        def get_args_keyword_args(exprs: list[Expr]):
            args = map_eval_over(
                list(filter(lambda x: not isinstance(x, KeywordArg), exprs))
            )
            keywordargs = list(filter(lambda x: isinstance(x, KeywordArg), exprs))
            keywordargs = [(kwa.key, self.eval(kwa.e)) for kwa in keywordargs]
            keywordargs = {k: e for k, e in keywordargs}
            return args, keywordargs

        if isinstance(e, Literal):
            return e.const
        if isinstance(e, Variable):
            if e in self._vars_to_vals:
                return self._vars_to_vals[e]
            n = e.name
            if n in self._motifs:
                return self._motifs[n]
            if n in self._placed_motifs:
                return self._placed_motifs[n]
            if n == self.design_var:
                return self.design
            assert False, f"{self.cn}.eval: no such name {n}"
            pass
        if isinstance(e, ObjectInit):
            assert (
                e.className in self._classes
            ), f"{self.cn}.eval: the class {e.className} is not supported for object initialization"
            args, keywordargs = get_args_keyword_args(e.args)
            return eval(e.className)(*args, **keywordargs)
            pass
        if isinstance(e, ObjectAccess):
            return getattr(self.eval(e.v), e.prop)
        if isinstance(e, ObjectMethodCall):
            # args = map_eval_over(e.args)
            args, keywordargs = get_args_keyword_args(e.args)
            return getattr(self.eval(e.v), e.method)(*args, **keywordargs)
        if isinstance(e, KeywordArg):
            return self.eval(e.e)
        # Avoid unprincipled eval if we can...
        maybeMotif = self._builder._get_motif(e)
        if maybeMotif:
            return maybeMotif
        if isinstance(e, ModuleRef) or isinstance(e, ModuleAccess):
            return eval(e.to_python())
        if isinstance(e, AttrAccess):
            return eval(e.obj.to_python())[self.eval(e.key)]
        assert False, f"{self.cn}.eval: impossible kind of expr encountered '{e}'"

    def interpret(self, action: DesignOp):
        # TODO: Fix
        if isinstance(action, AddMotif):
            motif = self.eval(action.m)
            x = self.eval(action.x)
            y = self.eval(action.y)
            res = self.design.add_motif(motif, x, y)
            self._placed_motifs[action.v.name] = res
            return res
        if isinstance(action, RemoveMotif):
            assert (
                self.design_var == action.d.name
            ), f"{self.cn}.interpret: design name {action.d.name} not recognized"
            pm = self.eval(action.placed_motif)
            self.design.remove_motif(pm)
            return
        if isinstance(action, Motifify):
            assert (
                self.design_var == action.d.name
            ), f"{self.cn}.interpret: design name {action.d.name} not recognized"
            args = [action.x0, action.y0, action.x1, action.y1]
            args = [self.eval(arg) for arg in args]
            res = self.design.motifify(*args)
            self._motifs[action.v.name] = res
            self._vars_to_vals[action.v] = res
            self._builder.load_motif(action.v.name, res, action.v)
            return res
        if isinstance(action, UnMotifify):
            assert (
                action.v in self._vars_to_vals
            ), f"{self.cn}.interpret: cannot find {action.v} in _vars_to_vals"
            # basically just set the value of the variable action.v to None
            self._motifs[action.v.name] = None
            self._vars_to_vals[action.v] = None
            return
        if isinstance(action, SizeOp):
            ind = self.eval(action.at_index) if action.at_index else -1
            if isinstance(action, RemoveRow):
                i, r = self.design.remove_row(at_index=ind)
                self._vars_to_vals[action.indexVar] = i
                self._vars_to_vals[action.removed] = r
                return
            if isinstance(action, RemoveColumn):
                i, r = self.design.remove_column(at_index=ind)
                self._vars_to_vals[action.indexVar] = i
                self._vars_to_vals[action.removed] = r
                return
            if isinstance(action, AddRow) or isinstance(action, AddColumn):
                contents = self.eval(action.contents) if action.contents else None
                if isinstance(action, AddRow):
                    v = self.design.add_row(at_index=ind, contents=contents)
                    self._vars_to_vals[action.v] = v
                    return
                if isinstance(action, AddColumn):
                    v = self.design.add_column(at_index=ind, contents=contents)
                    self._vars_to_vals[action.v] = v
                    return
        pass


class DesignProgramBuilder:
    _imports: list[Import]
    _fresh: FreshVar
    _actions: list[DesignOp]
    _index: int

    _motifs: dict[str, Motif]
    _design_var: Variable
    cn: str = __qualname__
    base_design: Design
    _motif_name_to_expr: dict[str, Expr]
    # TODO: actually use
    _motif_creations: list[SetVariable]
    _expr_to_motif_name: dict[Expr, str]
    _original_size: tuple[int, int]

    def __init__(self, base_design: Design):
        self._imports = list()
        self._imports.append(FromImport("modularmotifs.core", "Design"))
        self._fresh = FreshVar()
        self._actions = list()
        self._index = -1
        self._design_var = self._get_fresh_var()
        self.base_design = base_design
        self._motifs = dict()
        self._motif_name_to_expr = dict()
        self._expr_to_motif_name = dict()
        self._motif_creations = list()
        self._original_size = (self.base_design.width(), self.base_design.height())
        pass

    @classmethod
    def init_list(cls, l: list[Syntax], fresh: FreshVar) -> Self:
        # TODO: Account for when a design is actually imported from another file. This would amount to searching for a design variable that's being used and then searching for where that design variable comes from. What we have here though is a good enough first step
        d = list(
            filter(
                lambda x: (
                    isinstance(x, SetVariable)
                    and isinstance(x.expr, ObjectInit)
                    and x.expr.className == "Design"
                ),
                l,
            )
        )
        assert (
            d
        ), f"{cls.init_list.__qualname__}: found no Design variables set in list {l}"
        # list is nonempty => get the first thing
        d = d[0]
        # this is technically unsafe, so TODO: FIX
        base_design = eval(d.expr.to_python())

        dpb = DesignProgramBuilder(base_design)
        dpb.add_modularmotifs_motif_library()

        imports = list(filter(lambda x: isinstance(x, Import), l))
        for i in imports:
            if i not in dpb._imports:
                dpb._imports.append(i)
                pass
            pass

        dpb._fresh = fresh
        dpb._design_var = d.x

        motifs = list(
            filter(
                lambda x: (
                    isinstance(x, SetVariable)
                    and isinstance(x.expr, ObjectInit)
                    and x.expr.className == "Motif"
                ),
                l,
            )
        )
        for m in motifs:
            # TODO: FIX, also unsafe
            m_eval = eval(m.expr.to_python())
            dpb.load_motif(m.x.name, m_eval)
            pass
        dpb._motif_creations.extend(motifs)

        interp = dpb.get_interpreter()
        actions = list(filter(lambda x: isinstance(x, DesignOp), l))
        for a in actions:
            dpb._actions.append(a)
            interp.interpret(a)
            dpb._index += 1

        return dpb, interp

    def load_motif(self, name: str, m: Motif, e: Optional[Expr] = None) -> Self:
        self._motifs[name] = m
        if e:
            self._motif_name_to_expr[name] = e
            self._expr_to_motif_name[e] = name
            pass
        else:
            # TODO: add another set_variable to self._motif_creations
            pass
        return self

    def _get_motif(self, m: Union[str, Expr]) -> Optional[Motif]:
        if isinstance(m, str) and m in self._motifs:
            return self._motifs[m]
        if isinstance(m, Expr) and m in self._expr_to_motif_name:
            mname = self._expr_to_motif_name[m]
            if mname in self._motifs:
                return self._motifs[mname]
            pass
        return None

    @classmethod
    def map_to_python(cls, l: list[Syntax]) -> list[str]:
        return list(map(lambda x: x.to_python(), l))

    def _imports_to_python(self) -> str:
        return "\n".join(DesignProgramBuilder.map_to_python(self._imports))

    def _motifs_to_python(self) -> str:
        return "\n".join(DesignProgramBuilder.map_to_python(self._motif_creations))

    def _design_statement(self) -> str:
        design_statement = SetVariable(
            self._design_var,
            ObjectInit(
                "Design",
                Literal(self._original_size[0]),
                Literal(self._original_size[1]),
            ),
        ).to_python()
        return design_statement

    def _ops_to_python(self) -> str:
        return "\n".join(
            DesignProgramBuilder.map_to_python(self._actions[: self._index + 1])
        )

    @classmethod
    def _format_to_python(cls, l: list[str]) -> str:
        return "\n\n".join(l)

    def to_python(self) -> str:
        imports = self._imports_to_python()
        design_statement = self._design_statement()
        motifs = self._motifs_to_python()
        ops = self._ops_to_python()
        return DesignProgramBuilder._format_to_python(
            [imports, design_statement, motifs, ops]
        )

    def add_modularmotifs_motif_library(self) -> Self:
        print(libexamples.__name__)
        self.add_import(libexamples, _as="libexamples")

        for m in libexamples.motifs:
            self.load_motif(
                m,
                libexamples.motifs[m],
                e=AttrAccess(
                    ModuleAccess(ModuleRef("libexamples"), "motifs"), Literal(m)
                ),
            )
            pass

        return self

    def get_interpreter(self) -> DesignInterpreter:
        return DesignInterpreter(
            self.base_design, self._design_var.name, self._motifs, self._imports, self
        )

    def _get_fresh_var(self):
        return Variable(self._fresh.get_fresh())

    def has_import(self, i: Import) -> bool:
        return i in self._imports

    def add_import(self, m: ModuleType, _as: Optional[str] = None) -> Self:
        self._imports.append(Import(m.__name__, _as=_as))
        return self

    def _get_design_var(self) -> Variable:
        return self._design_var

    def get_latest_action(self) -> DesignOp:
        return self._actions[self._index]

    def _overwrite(self):
        """
        If at any point we add another action that overwrites past, undone actions, we overwrite the old history
        """
        if self._index < self.num_actions() - 1:
            self._actions = self._actions[: self._index + 1]
            pass
        pass

    def get_placed_motifs(self):
        placed_names = [a.v.name for a in self._actions if isinstance(a, AddMotif)]
        return placed_names

    def _add_action(self, d: DesignOp):
        self._overwrite()
        self._actions.append(d)
        self._index += 1
        return d

    def motifify(self, x0: int, y0: int, x1: int, y1: int) -> DesignOp:
        return self._add_action(
            Motifify(
                self._get_fresh_var(),
                self._design_var,
                Literal(x0),
                Literal(y0),
                Literal(x1),
                Literal(y1),
                self._fresh,
            )
        )

    def add_motif(self, name: str, x: int, y: int) -> DesignOp:
        assert (
            name in self._motif_name_to_expr
        ), f"{self.cn}.add_motif: could not find motif with name {name}, did you forget to load_motif it?"
        return self._add_action(
            AddMotif(
                self._get_fresh_var(),
                self._design_var,
                self._motif_name_to_expr[name],
                Literal(x),
                Literal(y),
                self._fresh,
            )
        )

    def remove_motif(self, name: str) -> DesignOp:
        assert (
            name in self.get_placed_motifs()
        ), f"{self.cn}.remove_motif: could not find a placed motif with name {name}"

        return self._add_action(
            RemoveMotif(self._design_var, Variable(name), self._fresh)
        )

    def add_row(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)

        return self._add_action(
            AddRow(
                self._get_fresh_var(),
                self._design_var,
                at_index=at_index_arg,
                fresh=self._fresh,
            )
        )

    def add_column(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)

        return self._add_action(
            AddColumn(
                self._get_fresh_var(),
                self._design_var,
                at_index=at_index_arg,
                fresh=self._fresh,
            )
        )

    def remove_row(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)

        return self._add_action(
            RemoveRow(
                self._get_fresh_var(),
                self._get_fresh_var(),
                self._design_var,
                at_index=at_index_arg,
                fresh=self._fresh,
            )
        )

    def remove_column(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)

        return self._add_action(
            RemoveColumn(
                self._get_fresh_var(),
                self._get_fresh_var(),
                self._design_var,
                at_index=at_index_arg,
                fresh=self._fresh,
            )
        )

    def remove_last_action(self) -> DesignOp:
        assert (
            self.can_undo()
        ), f"{self.remove_last_action.__qualname__}: No last action to remove"
        old_index = self._index
        self._index -= 1
        return self._actions.pop(old_index)

    def can_undo(self) -> bool:
        return self._index >= 0

    def can_redo(self) -> bool:
        return self._index < self.num_actions() - 1

    def undo(self) -> Optional[DesignOp]:
        if self.can_undo():
            old_index = self._index
            self._index -= 1
            return self._actions[old_index].inverse()
        return None

    def num_actions(self) -> int:
        return len(self._actions)

    def redo(self) -> Optional[DesignOp]:
        if self.can_redo():
            self._index += 1
            return self._actions[self._index]
        return None

    # def load_base_design(self) -> Self:
    #     # TODO: complete
    #     return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.base_design})"

    pass


if __name__ == "__main__":
    c1 = Literal(1)
    c2 = Literal(3.0)
    c3 = Literal([1, 3.0])
    c4 = Literal([1, 1, 1])
    c5 = Literal("constant")

    fresh = FreshVar()

    c6 = AddMotif(
        Variable(fresh.get_fresh()),
        Variable(fresh.get_fresh()),
        Variable(fresh.get_fresh()),
        Literal(10),
        Literal(11),
        fresh,
    )

    syntax = [c1, c2, c3, c4, c5, c6, c6.inverse(), c6.inverse().inverse()]

    for c in syntax:
        print(repr(c))
        print(c.to_python())
        pass

    builder = DesignProgramBuilder(Design(10, 10))
    builder.add_modularmotifs_motif_library()
    interp = builder.get_interpreter()
    op = builder.add_motif("plus-3x3", 0, 0)
    _ = builder.add_motif("crosshair-3x3", 3, 3)

    print(op)
    res = interp.interpret(op)
    print(res)
    print(builder.to_python())

    pass
