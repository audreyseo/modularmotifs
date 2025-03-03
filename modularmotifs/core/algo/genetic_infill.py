"""Genetic algorithm for infilling a rectangular region with motifs.

We optimizes the placement of multiple motifs over a given region using GA. 
We assumes that all motifs in the provided list have identical dimensions. 
The region is divided into a grid where each cell hosts one full motif.
Each candidate solution encodes two components:
  - offsets: a list of horizontal shifts (one per grid row), and 
  - grid: a 2D list (rows x columns) indicating which motif to place in each cell.

The fitness of a candidate is determined solely by the float cost via calculate_float_lengths
"""

import random
import copy
from typing import List, Any, Iterable, Tuple, Generator

from modularmotifs.core.design import PlacedMotif
from modularmotifs.core.pixel_grid import PixelGrid
from modularmotifs.core.rgb_color import RGBColor
from modularmotifs.core.motif import Motif, Color
from modularmotifs.core.algo.calc_floats import calculate_float_lengths

DEFAULT_FORE: RGBColor = RGBColor.Fore() #RGBColor(0, 0, 0)
DEFAULT_BACK: RGBColor = RGBColor.Back() #RGBColor(255, 255, 255)
DEFAULT_INVIS: RGBColor = RGBColor.Invis() #RGBColor(128, 128, 128)

class _Design(PixelGrid):
    __height: int
    __width: int
    __canvas: list[list[Color]]

    def __init__(self, height: int, width: int):
        self.__height = height
        self.__width = width
        self.__canvas = [
            self.__new_row()
            for _ in range(self.__height)
        ]
        self.fore_color: RGBColor = DEFAULT_FORE
        self.back_color: RGBColor = DEFAULT_BACK
        self.invis_color: RGBColor = DEFAULT_INVIS

    def __new_row(self) -> list[Color]:
        return [_Design.default_pixel_data() for _ in range(self.__width)]
    
    @classmethod
    def default_pixel_data(cls) -> Color:
        return Color.INVIS

    def width(self) -> int:
        return self.__width
    
    def height(self) -> int:
        return self.__height
    
    def get_rgb(self, x: int, y: int) -> RGBColor:
        match self.get_color(x, y):
            case Color.FORE:
                return self.fore_color
            case Color.BACK:
                return self.back_color
            case Color.INVIS:
                return self.invis_color
        raise ValueError("I don't know which color this is!")
    
    def add_motif(self, m: Motif, x: int, y: int):
        for iy, row in enumerate(m):
            for ix, col in enumerate(row):
                self.__canvas[y + iy][x + ix] += col
    
    def complete(self) -> bool:
        for row in self.__canvas:
            for px in row:
                if px.col == Color.INVIS:
                    return False
        return True

    def get_color(self, x: int, y: int) -> Color:
        return self.__canvas[y][x]
    
    def __iter__(self) -> Generator[Iterable[Tuple[Color, int, int]], None, None]:
        for y in range(self.__height):
            yield [(self.get_color(x, y), x, y) for x in range(self.__width)]

def genetic_infill_region(
    design: _Design,
    motifs_list: List[Motif],
    region_x: int,
    region_y: int,
    region_width: int,
    region_height: int,
    pop_size: int = 50,
    generations: int = 100,
    mutation_rate: float = 0.1
) -> List[PlacedMotif]:
    """
    Infill a rectangular region in the design by selecting motifs from a provided list using a genetic algorithm.
    
    Assumes all motifs in motifs_list have the same dimensions.
    The region is divided into a grid where each cell hosts one full motif.
    Each candidate solution is a dictionary with:
      - "offsets": a list of horizontal offsets for each row (range [0, max_offset]),
      - "grid": a 2D list (num_rows x num_cols) of indices, each corresponding to an entry in motifs_list.
    
    The fitness is evaluated on a simulated design by placing the motifs as specified and computing
    the float cost via calculate_float_lengths (sum of float strand lengths).
    
    Args:
        design (Design): The Design object to update.
        motifs_list (List[Motif]): List of available motifs.
        region_x (int): x-coordinate of the region's top-left corner.
        region_y (int): y-coordinate of the region's top-left corner.
        region_width (int): Width of the region.
        region_height (int): Height of the region.
        pop_size (int): Population size for the genetic algorithm.
        generations (int): Number of generations to run.
        mutation_rate (float): Mutation probability.
    
    Returns:
        List[PlacedMotif]: List of PlacedMotif instances added to the design for the best candidate.
    
    Raises:
        ValueError: If the region is too small or no motifs are provided.
    """
    if not motifs_list:
        raise ValueError("motifs_list is empty.")
    
    # Assume all motifs have identical dimensions.
    tile_width = motifs_list[0].width()
    tile_height = motifs_list[0].height()
    
    num_cols = region_width // tile_width
    num_rows = region_height // tile_height
    
    if num_cols < 1 or num_rows < 1:
        raise ValueError("Region too small to place any full motif.")
        
    max_offset = region_width - (num_cols * tile_width)
    num_motifs = len(motifs_list)
    
    # Candidate representation: dictionary with keys "offsets" and "grid".
    # "offsets": list of length num_rows, each in [0, max_offset].
    # "grid": list of lists with dimensions (num_rows x num_cols), each entry in [0, num_motifs-1].
    # ""
    def random_candidate() -> dict:
        return {
            "offsets": [random.randint(0, max_offset) for _ in range(num_rows)],
            "grid": [[random.randint(0, num_motifs - 1) for _ in range(num_cols)] for _ in range(num_rows)]
        }
    
    def simulate(candidate: dict) -> Any:
        """Simulate candidate placement on a temporary design and return the float cost."""
        temp_design = _Design(region_height, region_width)
        try:
            for r in range(num_rows):
                offset = candidate["offsets"][r]
                for c in range(num_cols):
                    motif_index = candidate["grid"][r][c]
                    motif_to_place = motifs_list[motif_index]
                    x = offset + c * tile_width
                    y = r * tile_height
                    if x + tile_width > region_width or y + tile_height > region_height:
                        continue
                    temp_design.add_motif(motif_to_place, x, y)
            float_strands = calculate_float_lengths(temp_design, treat_invisible_as_bg=True)
            # We need an l_p norm for some p > 1 since sum of float lengths is "constant"
            cost = (sum(len(fs) ** 5 for fs in float_strands)) ** (1.0 / 5.0)
            # print(cost)
        except Exception as e:
            cost = float("inf")
        return cost, temp_design
    
    def crossover(parent1: dict, parent2: dict) -> dict:
        child = {"offsets": [], "grid": []}
        for r in range(num_rows):
            # For offsets, randomly choose from one parent.
            child["offsets"].append(random.choice([parent1["offsets"][r], parent2["offsets"][r]]))
            # For each grid row, perform one-point crossover.
            if num_cols > 1:
                point = random.randint(1, num_cols - 1)
                row_child = parent1["grid"][r][:point] + parent2["grid"][r][point:]
            else:
                row_child = [random.choice([parent1["grid"][r][0], parent2["grid"][r][0]])]
            child["grid"].append(row_child)
        return child
    
    def mutate(candidate: dict):
        # Mutate offsets.
        for r in range(num_rows):
            if random.random() < mutation_rate:
                candidate["offsets"][r] = random.randint(0, max_offset)
        # Mutate grid.
        for r in range(num_rows):
            for c in range(num_cols):
                if random.random() < mutation_rate:
                    candidate["grid"][r][c] = random.randint(0, num_motifs - 1)
    
    # Initialize population.
    population = [random_candidate() for _ in range(pop_size)]
    best_candidate = None
    best_cost = float("inf")
    
    # Run genetic algorithm across generations.
    for g in range(generations):
        print(f"Generation {g}")
        scored = [(simulate(candidate)[0], candidate) for candidate in population]
        scored.sort(key=lambda x: x[0])
        if scored[0][0] < best_cost:
            best_cost = scored[0][0]
            best_candidate = copy.deepcopy(scored[0][1])
        survivors = [ind for (_, ind) in scored[:4]]
        new_population = []
        while len(new_population) < pop_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            child = crossover(parent1, parent2)
            mutate(child)
            new_population.append(child)
        population = new_population
        print(best_cost)
    
    if best_candidate is None:
        raise RuntimeError("No valid candidate found by the genetic algorithm.")
    
    # Apply the best candidate configuration on the actual design.
    placed_motifs = []
    for r in range(num_rows):
        offset = best_candidate["offsets"][r]
        for c in range(num_cols):
            motif_index = best_candidate["grid"][r][c]
            motif_to_place = motifs_list[motif_index]
            x = region_x + offset + c * tile_width
            y = region_y + r * tile_height
            placed = design.add_motif(motif_to_place, x, y)
            placed_motifs.append(placed)
    
    return placed_motifs

# region main
if __name__ == "__main__":
    from modularmotifs.motiflibrary.examples import bird_motifs, motifs
    from modularmotifs.core.util import rgbcolors_to_image

    MOTIFS = motifs

    # Compile a list of motifs.
    motifs_list = list(MOTIFS.values())
    
    # Define design dimensions.
    design_width = 24
    design_height = 24
    test_design = _Design(design_height, design_width)
    
    # Define the tiling region (entire design area).
    region_x = 0
    region_y = 0
    region_width = design_width
    region_height = design_height
    
    # Run the genetic algorithm based infill.
    placed = genetic_infill_region(
        test_design, motifs_list,
        region_x, region_y, region_width, region_height,
        pop_size=100, generations=1, mutation_rate=0.05
    )
    
    # Convert design's color data to a 2D list of RGBColor objects.
    color_grid = []
    for y in range(test_design.height()):
        row = []
        for x in range(test_design.width()):
            row.append(test_design.get_rgb(x, y))
        color_grid.append(row)
    
    # Export the design to a PNG image with each design "pixel" scaled up.
    img = rgbcolors_to_image(color_grid, square_size=10)
    img.save("test_genetic_infill.png")
    print("Test genetic infill design saved to test_genetic_infill.png")

# endregion