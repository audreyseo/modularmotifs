from modularmotifs.dsl._syntax import DesignProgramBuilder, SetVariable, ObjectInit, Literal, FromImport
from modularmotifs.core.composite_motif import CompositeMotif

class MotifProgramBuilder(DesignProgramBuilder):
    base_motif: CompositeMotif
    
    def __init__(self, base_motif: CompositeMotif):
        super().__init__(base_motif)
        self._imports.append(FromImport("modularmotifs.core", "CompositeMotif"))
        self.base_motif = base_motif
        print("CompositeMotif")
        pass
    
    def _design_statement(self) -> str:
        return SetVariable(self._design_var, ObjectInit("CompositeMotif", Literal(self._original_size[0]), Literal(self._original_size[1]))).to_python()
        
    def to_python(self) -> str:
        imports = self._imports_to_python()
        design_statement = self._design_statement()
        motifs = self._motifs_to_python()
        ops = self._ops_to_python()
        return MotifProgramBuilder._format_to_python([imports, design_statement, motifs, ops])