import tkinter as tk
from modularmotifs.ui.interface import KnitWindow, GRID_HEIGHT, GRID_WIDTH
from collections.abc import Callable
from modularmotifs.core.composite_motif import CompositeMotif
from modularmotifs.dsl._motif_builder import MotifProgramBuilder

class MotifWindow(KnitWindow):
    _design: CompositeMotif
    
    def __init__(self):
        self._design = CompositeMotif(GRID_WIDTH, GRID_HEIGHT)
        pb = MotifProgramBuilder(self._design)
        super().__init__(design=self._design, title="Motif Canvas", save_motif=False, program_builder=pb)
        self._design = CompositeMotif(GRID_WIDTH, GRID_HEIGHT)
        
        # interp = pb.get_interpreter()
        # self._init_underlying(pb, interp)
        # self._program_builder = pb
        pass
    
    
    def _init_save(self) -> Callable:
        save_handler = super()._init_save()
        def new_save_handler(e):
            print(self._design)
            print(self._program_builder)       
            return save_handler(e)
        return new_save_handler
    pass

if __name__ == "__main__":
    MotifWindow()