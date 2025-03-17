from modularmotifs.dsl._syntax.basic_ast import *
class Operation(Statement):
    fresh: FreshVar
    op_name: str
    
    def __init__(self, op_name: str, fresh: FreshVar):
        super().__init__()
        self.op_name = op_name
        self.fresh = fresh
    
    @abc.abstractmethod
    def inverse(self) -> 'Operation':
        pass
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
                         at_index=self.v,
                         fresh=self.fresh)
        
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
                      at_index=self.indexVar,
                      fresh=self.fresh,
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
                         at_index=self.v,
                         fresh=self.fresh)
        
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
                      at_index=self.indexVar,
                      fresh=self.fresh,
                      contents=self.removed)
    def to_python(self) -> str:
        return f"{self.indexVar}, {self.removed} = {self.d}.{self.op_name}({self.get_at_index()})"
    pass
