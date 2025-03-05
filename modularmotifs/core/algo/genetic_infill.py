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
from typing import List, Any

from modularmotifs.core.design import Design, PlacedMotif
from modularmotifs.core.motif import Motif
from modularmotifs.core.algo.calc_floats import calculate_float_lengths

# Genetic Algorithm Infill Function
def genetic_infill_region(
    design: Design,
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
    def random_candidate() -> dict:
        return {
            "offsets": [random.randint(0, max_offset) for _ in range(num_rows)],
            "grid": [[random.randint(0, num_motifs - 1) for _ in range(num_cols)] for _ in range(num_rows)]
        }
    
    def simulate(candidate: dict) -> Any:
        """Simulate candidate placement on a temporary design and return the float cost."""
        temp_design = Design(region_height, region_width)
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
            cost = (sum(len(fs) ** 3 for fs in float_strands)) ** (1.0 / 3.0)
            # cost = sum(len(fs) for fs in float_strands)
            # color_grid = []
            # for y in range(temp_design.height()):
            #     row = []
            #     for x in range(temp_design.width()):
            #         row.append(temp_design.get_rgba(x, y))
            #     color_grid.append(row)
            # img = rgbcolors_to_image(color_grid, square_size=10)
            # img.save(f"{id(candidate)}_test_genetic_infill_{cost}.png")
        except Exception:
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
        print(g)
        scored = [(simulate(candidate)[0], candidate) for candidate in population]
        scored.sort(key=lambda x: x[0])
        if scored[0][0] < best_cost:
            best_cost = scored[0][0]
            best_candidate = copy.deepcopy(scored[0][1])
        survivors = [ind for (_, ind) in scored[:pop_size // 2]]
        new_population = []
        while len(new_population) < pop_size:
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            child = crossover(parent1, parent2)
            mutate(child)
            new_population.append(child)
        population = new_population
    
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
    from modularmotifs.motiflibrary.examples import motifs, bird_motifs
    from modularmotifs.core.design import Design
    from modularmotifs.core.util import rgbcolors_to_image

    MOTIFS = bird_motifs

    # Compile a list of motifs.
    motifs_list = list(MOTIFS.values())
    
    # Define design dimensions.
    design_width = 80
    design_height = 80
    test_design = Design(design_height, design_width)
    
    # Define the tiling region (entire design area).
    region_x = 0
    region_y = 0
    region_width = design_width
    region_height = design_height
    
    # Run the genetic algorithm based infill.
    placed = genetic_infill_region(
        test_design, motifs_list,
        region_x, region_y, region_width, region_height,
        pop_size=20, generations=10, mutation_rate=0.1
    )
    
    # Convert design's color data to a 2D list of RGBAColor objects.
    color_grid = []
    for y in range(test_design.height()):
        row = []
        for x in range(test_design.width()):
            row.append(test_design.get_rgba(x, y))
        color_grid.append(row)
    
    # Export the design to a PNG image with each design "pixel" scaled up.
    img = rgbcolors_to_image(color_grid, square_size=10)
    img.save("test_genetic_infill.png")
    print("Test genetic infill design saved to test_genetic_infill.png")

