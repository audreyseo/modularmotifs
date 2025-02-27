import abc
# TODO: I think we would want to replace TypeGuard with TypeIs if we were all using Python 3.13...
from typing import Union, TypeGuard, Self, Optional, Type, Any, List
from types import ModuleType
from modularmotifs.core import Motif, Design, Color
from modularmotifs.core.design import PlacedMotif
import modularmotifs.motiflibrary.examples as libexamples
# from pathlib import Path

class FreshVar:
    """A source of fresh variable names
    """
    def __init__(self, base_name="x", names_to_avoid: Optional[set[str]] = None):
        """Initialize a new FreshVar instance

        Args:
            base_name (str, optional): the prefix for variable names. Defaults to "x".
            names_to_avoid (Optional[set[str]], optional): a set of variable names to avoid (i.e., because it would result in overwriting a previously defined variable). Defaults to None.
        """
        self.current = 0
        self.base_name = base_name
        self.names_to_avoid = names_to_avoid
        pass

    def get_fresh(self) -> str:
        fresh = f"{self.base_name}{self.current}"
        self.current += 1
        if self.names_to_avoid:
            while fresh in self.names_to_avoid:
                fresh = f"{self.base_name}{self.current}"
                self.current += 1
                pass
            pass
        return fresh
        

class Syntax(abc.ABC):
    """ An immutable type that represents the syntax of the DSL
    """
    
    cn = __qualname__
    
    def __init__(self):
        self.cn = self.__class__.__qualname__
        pass

    def __repr__(self) -> str:
        return f"{self.cn}"

    @abc.abstractmethod
    def to_python(self) -> str:
        return ""

    def __str__(self) -> str:
        return self.to_python()

    def __eq__(self, other: 'Syntax'):
        # TODO: Find out what type other should have
        # if it returns the same code, it's the same
        return self.to_python() == other.to_python()

    def __hash__(self):
        # as a bare minimum, let's treat anything that returns the same code as the same
        return hash(self.to_python())
    pass


class Import(Syntax):
    # cn = __qualname__
    imported_module: str
    def __init__(self, mod: str, _as: Optional[str] = None):
        super().__init__()
        self.imported_module = mod
        self._as = _as
        pass

    def __repr__(self) -> str:
        return f"{self.cn}({self.imported_module})"

    def usename(self) -> str:
        if self._as:
            return self._as
        return self.imported_module

    def to_python(self) -> str:
        as_clause = ""
        if self._as is not None:
            as_clause = f" as {self._as}"
            pass
        return f"import {self.imported_module}{as_clause}"
    pass

class FromImport(Import):
    imports: list[str]
    def __init__(self, mod: str, *imports):
        super().__init__(mod)
        self.imports = imports
        pass
    
    def to_python(self) -> str:
        return f"from {self.imported_module} import {", ".join(self.imports)}"

class Expr(Syntax):
    cn = __qualname__
    pass

primitive = Union[int, float, str]

class Literal(Expr):
    # cn = __qualname__
    def __init__(self, const: Union[primitive, list[Expr]]):
        super().__init__()
        self.const = const
        # if isinstance(const, primitive):
        #     print("primitive")
        #     pass
        # else:
        #     print("list")
        #     pass
        pass

    def is_int(self) -> TypeGuard[int]:
        return isinstance(self.const, int)

    def is_str(self) -> TypeGuard[str]:
        return isinstance(self.const, str)

    def is_float(self) -> TypeGuard[float]:
        return isinstance(self.const, float)

    def is_list(self) -> TypeGuard[list]:
        return isinstance(self.const, List)


    def __repr__(self) -> str:
        return f"{self.cn}({self.to_python()})"

    def to_python(self) -> str:
        if self.is_str():
            return "\"" + self.const + "\""
        if self.is_list():
            print(self.const)
            return f"[{", ".join(list(map(lambda x: x.to_python(), self.const)))}]"
        return str(self.const)
    pass

class Variable(Expr):
    # cn = __qualname__
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        pass

    def __repr__(self) -> str:
        return f"{self.cn}({self.name})"
    
    def to_python(self) -> str:
        return self.name

class ObjectInit(Expr):
    cn = __qualname__
    def __init__(self, className: str,  *args: Expr):
        super().__init__()
        self.className = className
        self.args = args
        pass

    def to_python(self) -> str:
        args = ", ".join(list(map(lambda x: x.to_python(), self.args)))
        return f"{self.className}({args})"
    pass

class AttrAccess(Expr):
    def __init__(self, obj: Expr, key: Expr):
        super().__init__()
        self.obj = obj
        self.key = key
        pass

    def to_python(self) -> str:
        return f"{self.obj}[{self.key}]"
    pass

class ModuleRef(Expr):
    def __init__(self, module: str):
        super().__init__()
        self.module = module
        pass

    def to_python(self) -> str:
        return self.module

class ModuleAccess(Expr):
    def __init__(self, module: Expr, attr: str):
        super().__init__()
        self.module = module
        self.attr = attr
        pass

    def to_python(self) -> str:
        return f"{self.module.to_python()}.{self.attr}"

class ObjectAccess(Expr):
    def __init__(self, v: Variable, prop: str):
        super().__init__()
        self.v = v
        self.prop = p
        pass

    def to_python(self) -> str:
        return f"{self.v}.{self.prop}"
    pass

class ObjectMethodCall(Expr):
    def __init__(self, v: Variable, method: str, *args: Expr):
        super().__init__()
        self.v = v
        self.method = method
        self.args = args
        pass

    def to_python(self) -> str:
        args = ", ".join(list(map(lambda x: x.to_python(), self.args)))
        return f"{self.v}.{self.method}({args})"

    pass

class KeywordArg(Expr):
    def __init__(self, key: str, e: Expr):
        super().__init__()
        self.key = key
        self.e = e
        pass
    
    def to_python(self) -> str:
        return f"{self.key}={self.e.to_python()}"

class Statement(Syntax):
    pass
    
class DesignOp(Statement):
    cn = __qualname__

    def __init__(self, d: Variable, op_name: str, fresh: FreshVar):
        super().__init__()
        self.d = d
        self.op_name = op_name
        # source of fresh variable names
        self.fresh = fresh

    @abc.abstractmethod
    def inverse(self) -> 'DesignOp':
        pass
    pass

class SetVariable(Statement):
    def __init__(self, x: Variable, expr: Expr):
        super().__init__()
        self.x = x
        self.expr = expr
        pass

    def to_python(self) -> str:
        return f"{self.x} = {self.expr}"


class AddMotif(DesignOp):
    cn = __qualname__

    def __init__(self, v: Variable, d: Variable, m: Expr, x: Expr, y: Expr, fresh: FreshVar):
        super().__init__(d, "add_motif", fresh)
        # where the placed motif is stored -- should be a fresh variable
        self.v = v
        # the motif to be added
        self.m = m
        # the x and y coordinates
        self.x = x
        self.y = y
        pass

    def inverse(self) -> DesignOp:
        return RemoveMotif(self.d, self.v, self.fresh)

    def to_python(self) -> str:
        return f"{self.v} = {self.d}.{self.op_name}({self.m}, {self.x}, {self.y})"

    pass

class RemoveMotif(DesignOp):
    def __init__(self, d: Variable, placedmotif: Variable, fresh: FreshVar):
        super().__init__(d, "remove_motif", fresh)
        # self.d = d
        self.placed_motif = placedmotif
        pass

    def inverse(self) -> DesignOp:
        return AddMotif(Variable(self.fresh.get_fresh()),
                        self.d,
                        ObjectMethodCall(self.placed_motif, "motif"),
                        ObjectMethodCall(self.placed_motif, "x"),
                        ObjectMethodCall(self.placed_motif, "y"),
                        self.fresh)
    def to_python(self) -> str:
        return f"{self.d}.{self.op_name}({self.placed_motif})"
    pass

class SizeOp(DesignOp):
    def __init__(self, d: Variable, op_name: str, fresh: FreshVar, at_index: Optional[Expr] = None, contents: Optional[Expr] = None):
        super().__init__(d, op_name, fresh)
        self.at_index = at_index
        self.contents = contents
        pass
    
    def get_at_index(self) -> str:
        return "" if not self.at_index else (f"at_index={self.at_index.to_python()}" if not isinstance(self.at_index, KeywordArg) else self.at_index.to_python())
    
    def get_args_to_python(self) -> list[str]:
        args = []
        at_index = self.get_at_index()
        if at_index:
            args.append(at_index)
        contents = self.contents.to_python() if self.contents else ""
        if contents:
            args.append(contents)
        return args

class AddRow(SizeOp):
    def __init__(self, v: Variable, d: Variable, fresh: FreshVar, at_index: Optional[Expr] = None, contents: Optional[Expr] = None):
        super().__init__(d, "add_row", fresh, at_index=at_index, contents=contents)
        self.v = v
        pass
    
    def inverse(self) -> DesignOp:
        return RemoveRow(Variable(self.fresh.get_fresh()),
                         Variable(self.fresh.get_fresh()),
                         self.d,
                         self.v,
                         self.fresh)
        
    def to_python(self) -> str:
        args = self.get_args_to_python()
        # []
        # at_index = self.get_at_index()
        # if at_index:
        #     args.append(at_index)
        # contents = self.contents.to_python() if self.contents else ""
        # if contents:
        #     args.append(contents)
        return f"{self.v} = {self.d}.{self.op_name}({", ".join(args)})"
    pass

class RemoveRow(SizeOp):
    def __init__(self, indexVar: Variable, removed: Variable, d: Variable, fresh: FreshVar, at_index: Optional[Expr]=None):
        super().__init__(d, "remove_row", fresh, at_index=at_index)
        self.indexVar = indexVar
        self.removed = removed
        pass
    
    def inverse(self) -> DesignOp:
        return AddRow(Variable(self.fresh.get_fresh()),
                      self.d,
                      self.indexVar,
                      self.fresh,
                      contents=self.removed)
    def to_python(self) -> str:
        return f"{self.indexVar}, {self.removed} = {self.d}.{self.op_name}({self.get_at_index()})"
    pass

class AddColumn(SizeOp):
    def __init__(self, v: Variable, d: Variable, fresh: FreshVar, at_index: Optional[Expr]=None, contents: Optional[Expr] = None):
        super().__init__(d, "add_column", fresh, at_index=at_index, contents=contents)
        self.v = v
        pass
    
    def inverse(self) -> DesignOp:
        return RemoveColumn(Variable(self.fresh.get_fresh()),
                         Variable(self.fresh.get_fresh()),
                         self.d,
                         self.v,
                         self.fresh)
        
    def to_python(self) -> str:
        args = self.get_args_to_python()
        # at_index = self.get_at_index()
        # contents = f", contents={self.contents.to_python()}" if self.contents else ""
        return f"{self.v} = {self.d}.{self.op_name}({", ".join(args)})"
    pass

class RemoveColumn(SizeOp):
    def __init__(self, indexVar: Variable, removed: Variable, d: Variable, fresh: FreshVar, at_index: Optional[Expr]=None):
        super().__init__(d, "remove_column", fresh, at_index=at_index)
        self.indexVar = indexVar
        self.removed = removed
        pass
    
    def inverse(self) -> DesignOp:
        return AddColumn(Variable(self.fresh.get_fresh()),
                      self.d,
                      self.indexVar,
                      self.fresh,
                      contents=self.removed)
    def to_python(self) -> str:
        return f"{self.indexVar}, {self.removed} = {self.d}.{self.op_name}({self.get_at_index()})"
    pass

class DesignInterpreter:
    design: Design
    design_var: str
    _motifs: dict[str, Motif]
    _imports: list[Import]
    _placed_motifs: dict[str, PlacedMotif]
    _classes: set[str] = set([Motif.__name__, Design.__name__])
    _builder: 'DesignProgramBuilder'
    _vars_to_vals: dict[Variable, Any]

    def __init__(self, design: Design, design_var: str, motifs: dict[str, Motif], imports: list[Import], builder: 'DesignProgramBuilder'):
        self.cn = self.__class__.__qualname__
        self.design = design
        self.design_var = design_var
        self._motifs = motifs
        self._imports = imports
        self._placed_motifs = dict()
        self._builder = builder
        self._vars_to_vals = dict()
        
        pass

    def eval(self, e: Expr):
        def map_eval_over(itr: list[Expr]):
            return list(map(lambda x: self.eval(x), itr))
        
        def get_args_keyword_args(exprs: list[Expr]):
            args = map_eval_over(list(filter(lambda x: not isinstance(x, KeywordArg), exprs)))
            keywordargs = list(filter(lambda x: isinstance(x, KeywordArg), exprs))
            keywordargs = [(kwa.key, self.eval(kwa.e)) for k in keywordargs]
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
            assert e.className in self._classes, f"{self.cn}.eval: the class {e.className} is not supported for object initialization"
            args, keywordargs = get_args_keyword_args(e.args)
            return eval(e.className)(*args, **keywordargs)
            pass
        if isinstance(e, ObjectAccess):
            return getattr(self.eval(e.v), e.prop)
        if isinstance(e, ObjectMethodCall):
            # args = map_eval_over(e.args)
            args, keywordargs = get_args_keyword_args(e.args)
            return getattr(self.eval(e.v), method)(*args, **keywordargs)
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
            assert self.design_var == action.d.name, f"{self.cn}.interpret: design name {action.d.name} not recognized"
            pm = self.eval(action.placed_motif)
            self.design.remove_motif(pm)
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
        d = list(filter(lambda x: (isinstance(x, SetVariable) and
                              isinstance(x.expr, ObjectInit) and
                              x.expr.className == "Design"),
                   l))
        assert d, f"{cls.init_list.__qualname__}: found no Design variables set in list {l}"
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
        
        
        motifs = list(filter(lambda x: (isinstance(x, SetVariable) and
                                        isinstance(x.expr, ObjectInit) and
                                        x.expr.className == "Motif"),
                             l))
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

    def to_python(self) -> str:
        def map_to_python(l: list[Syntax]) -> list[str]:
            return list(map(lambda x: x.to_python(), l))
        imports = "\n".join(map_to_python(self._imports))
        design_statement = SetVariable(self._design_var, ObjectInit("Design", Literal(self._original_size[0]), Literal(self._original_size[1]))).to_python()
        motifs = "\n".join(map_to_python(self._motif_creations))
        ops = "\n".join(map_to_python(self._actions[:self._index + 1]))
        return "\n\n".join([imports, design_statement, motifs, ops])

    def add_modularmotifs_motif_library(self) -> Self:
        print(libexamples.__name__)
        self.add_import(libexamples, _as="libexamples")

        for m in libexamples.motifs:
            self.load_motif(m, libexamples.motifs[m], e=AttrAccess(ModuleAccess(ModuleRef("libexamples"), "motifs"), Literal(m)))
            pass
        
        return self

    def get_interpreter(self) -> DesignInterpreter:
        return DesignInterpreter(self.base_design, self._design_var.name, self._motifs, self._imports, self)

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
            self._actions = self._actions[:self._index + 1]
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

    def add_motif(self, name: str, x: int, y: int) -> DesignOp:
        assert name in self._motif_name_to_expr, f"{self.cn}.add_motif: could not find motif with name {name}, did you forget to load_motif it?"
        return self._add_action(AddMotif(self._get_fresh_var(), self._design_var, self._motif_name_to_expr[name], Literal(x), Literal(y), self._fresh))

    def remove_motif(self, name: str) -> DesignOp:
        assert name in self.get_placed_motifs(), f"{self.cn}.remove_motif: could not find a placed motif with name {name}"
        
        return self._add_action(RemoveMotif(Variable(name), self._fresh))
    
    def add_row(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)
        
        return self._add_action(AddRow(self._get_fresh_var(), self._design_var, at_index=at_index_arg, fresh=self._fresh))
    
    def add_column(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)
        
        return self._add_action(AddColumn(self._get_fresh_var(), self._design_var, at_index=at_index_arg, fresh=self._fresh))
    
    def remove_row(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)
        
        return self._add_action(RemoveRow(self._get_fresh_var(),
                                       self._get_fresh_var(),
                                       self._design_var,
                                       at_index=at_index_arg,
                                       fresh=self._fresh))
        
    def remove_column(self, at_index: Optional[int] = None) -> DesignOp:
        at_index_arg = None if not at_index else Literal(at_index)
        
        return self._add_action(RemoveColumn(self._get_fresh_var(),
                                             self._get_fresh_var(),
                                             self._design_var,
                                             at_index=at_index_arg,
                                             fresh=self._fresh))
    
    def remove_last_action(self) -> DesignOp:
        assert self.can_undo(), f"{self.remove_last_action.__qualname__}: No last action to remove"
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
    pass



if __name__ == "__main__":
    c1 = Literal(1)
    c2 = Literal(3.0)
    c3 = Literal([1, 3.0])
    c4 = Literal([1, 1, 1])
    c5 = Literal("constant")

    fresh = FreshVar()
    
    c6 = AddMotif(Variable(fresh.get_fresh()), Variable(fresh.get_fresh()), Variable(fresh.get_fresh()), Literal(10), Literal(11), fresh)

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
