
import copy

deer_raw = [
    [3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 1, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 2, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 1, 1, 3, 3, 1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 2, 2, 2, 1, 2, 1, 2, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3], 
    [3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 2, 1, 1, 2, 1, 2, 2, 2, 2, 1, 2, 3, 3, 1, 3, 3, 3, 3, 1, 3, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 1, 2, 2, 3, 3, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 2, 1, 2, 2, 3, 3, 3, 3, 3, 1, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3],
    [3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 3, 3, 3, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3],
    [3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3],
    [3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3],
    [3, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3],
    [3, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3],
    [3, 3, 2, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 2, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3],
    [2, 2, 2, 1, 2, 1, 1, 2, 2, 3, 3, 2, 1, 1, 2, 1, 2, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 1, 3, 3, 3],
    [2, 1, 1, 2, 2, 1, 2, 2, 3, 3, 3, 2, 1, 2, 2, 1, 2, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 3, 1, 3, 3, 1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 1, 1, 3],
    [2, 2, 1, 2, 2, 1, 2, 2, 3, 3, 3, 2, 1, 2, 2, 1, 2, 2, 3, 1, 3, 1, 1, 1, 3, 1, 3, 3, 3, 1, 3, 1, 1, 1, 3, 1, 3, 3, 3, 1, 3, 3, 1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 1, 3, 3],
    [3, 2, 1, 2, 2, 2, 1, 2, 3, 3, 2, 2, 1, 2, 2, 1, 1, 2, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 1, 3, 3, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3],
    [3, 2, 1, 2, 3, 2, 1, 2, 3, 3, 2, 1, 2, 2, 2, 1, 2, 2, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3],
    [3, 2, 1, 2, 2, 2, 1, 2, 2, 3, 2, 1, 2, 2, 2, 1, 2, 2, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3],
    [3, 2, 2, 1, 2, 2, 2, 1, 2, 3, 2, 2, 1, 2, 2, 2, 1, 2, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3]
]

adults = [[3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3], [3, 1, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 3, 3], [1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3], [1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1], [1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1], [1, 3, 3, 3, 1, 1, 1, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 1, 1, 1, 3, 3, 3, 1, 1], [3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1], [3, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 3, 3], [3, 1, 1, 3, 3, 1, 1, 1, 1, 1, 3, 3, 1, 1, 3, 3, 3, 1, 1, 3, 3, 1, 1, 1, 1, 1, 3, 3, 1, 1, 3, 3], [1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 1, 1, 3], [1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 3], [3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1], [3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3], [3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3], [3, 3, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3], [3, 3, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3], [3, 3, 3, 1, 1, 1, 1, 3, 1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3], [3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3], [3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3], [3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3], [3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3, 3, 3], [3, 3, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3, 3, 3], [3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 1, 1, 1, 3, 3, 3, 3, 3], [1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 3, 1, 3, 1, 3, 1, 1, 3, 3, 3, 3], [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1], [3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

children = [[3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3], [3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3], [3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3], [3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3], [3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3], [3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3], [1, 3, 1, 1, 1, 3, 1, 3, 1, 3, 1, 1, 1, 3, 1, 3], [3, 3, 1, 1, 1, 3, 3, 1, 3, 3, 1, 1, 1, 3, 3, 1], [3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3], [3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3], [1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 3, 1, 1, 3, 3], [1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 3, 1, 1, 3, 3], [3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3], [1, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 1, 1, 3]]

crosses = [[1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3], [1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3], [3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [3, 1, 1, 3, 3, 1, 3, 3, 1, 1, 3, 3], [1, 1, 3, 3, 1, 1, 1, 3, 3, 1, 1, 3], [1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1], [3, 3, 1, 3, 1, 1, 1, 3, 1, 3, 3, 1], [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1], [3, 3, 1, 3, 1, 1, 1, 3, 1, 3, 3, 1], [1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1], [1, 1, 3, 3, 1, 1, 1, 3, 3, 1, 1, 3], [3, 1, 1, 3, 3, 1, 3, 3, 1, 1, 3, 1]]

floral_meander = [[3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 3, 3, 3, 1], [1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 3, 3, 1], [1, 3, 3, 1, 1, 1, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 1, 3, 3], [3, 3, 3, 1, 1, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 1, 1], [1, 3, 3, 1, 1, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3], [3, 1, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3], [3, 3, 1, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 1, 3, 3, 3, 1, 3], [3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3, 1, 3, 1, 1, 3, 3, 1, 1, 1], [1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 1, 3, 3, 1, 1, 1, 3, 3, 1, 1], [3, 3, 3, 1, 1, 1, 1, 3, 3, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1], [3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 3]]

heart1 = [[3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3], [3, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3], [3, 3, 1, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 3], [3, 3, 1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 3], [3, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3], [3, 3, 3, 1, 1, 1, 3, 3, 3, 1, 1, 1, 3, 3], [3, 3, 3, 3, 1, 1, 1, 3, 1, 1, 1, 3, 3, 3], [1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3], [1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1], [1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3]]

hearts = [[1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1], [1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3], [3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3], [1, 3, 3, 1, 1, 3, 1, 1, 3, 1, 3, 1, 3, 1, 3, 1, 1, 3, 1, 1, 3, 3], [1, 1, 3, 3, 1, 1, 3, 3, 1, 3, 1, 3, 1, 3, 1, 3, 3, 1, 1, 3, 3, 1], [3, 1, 1, 3, 3, 1, 1, 3, 3, 1, 3, 1, 3, 1, 3, 3, 1, 1, 3, 3, 1, 1], [3, 3, 1, 1, 3, 3, 1, 1, 3, 3, 1, 3, 1, 3, 3, 1, 1, 3, 3, 1, 1, 3], [1, 3, 3, 1, 1, 3, 3, 1, 1, 3, 3, 1, 3, 3, 1, 1, 3, 3, 1, 1, 3, 3], [3, 1, 3, 3, 1, 1, 3, 3, 1, 1, 3, 3, 3, 1, 1, 3, 3, 1, 1, 3, 3, 1], [1, 3, 1, 3, 3, 1, 1, 3, 3, 1, 1, 3, 1, 1, 3, 3, 1, 1, 3, 3, 1, 3], [3, 1, 3, 1, 3, 3, 1, 1, 3, 3, 1, 1, 1, 3, 3, 1, 1, 3, 3, 1, 3, 1], [1, 3, 1, 3, 1, 1, 3, 1, 1, 3, 3, 1, 3, 3, 1, 1, 3, 1, 1, 3, 1, 3], [3, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 1], [3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3], [3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3]]

ivy = [[1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3], [3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1], [3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 1], [3, 1, 1, 1, 3, 3, 1, 3, 3, 3, 1, 3, 1, 1, 1, 3, 1, 3, 3, 3, 1, 3, 3, 1, 1, 1, 3, 1], [1, 1, 1, 1, 1, 3, 1, 3, 3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 3, 1, 3, 1, 1, 1, 1, 1, 3], [3, 1, 1, 1, 3, 3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 3, 1, 1, 1, 3, 1], [1, 3, 1, 3, 3, 3, 1, 3, 3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 3, 1, 3, 3, 3, 1, 3, 1, 1], [1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 1, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1, 1], [1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 1, 1], [3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1]]

mountain_meander = [[3, 1, 3, 3], [1, 3, 1, 3], [3, 1, 3, 1], [1, 3, 1, 3], [3, 3, 3, 1]]

ring = [[3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3], [3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3], [3, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 3], [3, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 3], [1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1], [1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1], [3, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3], [1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1], [1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1], [3, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 3], [3, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 3], [3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3], [3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3]]

snowflake = [[3, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1], [1, 3, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 3], [3, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1], [1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1], [1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1], [3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 1, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1], [3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3], [3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3], [3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3], [3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 3], [3, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3], [3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 1, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1], [1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1], [1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1], [1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1], [3, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1], [1, 3, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 1, 1, 3], [3, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1]]

sunrise = [[3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3], [3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 1], [3, 3, 1, 3, 3, 1, 3, 3, 1, 3, 3, 1], [3, 3, 3, 1, 1, 1, 1, 1, 3, 3, 3, 1], [3, 1, 3, 1, 1, 1, 1, 1, 3, 1, 3, 1]]

xs = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3], [3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3], [3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3], [3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1], [1, 3, 1, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3], [3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1], [1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3], [3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1], [1, 3, 1, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3], [3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 3, 3, 1, 3, 1], [3, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3], [3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3], [1, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3, 1, 3, 3, 3, 1, 3, 1, 3, 3, 3], [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

bud_vine = [[1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 1, 3, 3, 3, 1, 3, 1, 1, 3, 3, 3, 3, 3], [1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3, 1], [3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1], [3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 3, 1, 1, 3, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 3, 1, 1, 3], [1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 3, 1, 1, 3, 3, 1, 1, 1, 3, 1, 3, 1, 1, 1, 3, 3, 1, 1, 3, 3], [3, 3, 1, 1, 1, 3, 1, 1, 1, 3, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 1, 1, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3], [1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3], [1, 1, 3, 1, 3, 3, 3, 1, 3, 1, 1, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3]]

butterfly = [[2, 2, 1, 1, 2, 2, 1, 2, 1, 2, 2, 1, 1, 2, 2, 3], [2, 1, 1, 1, 1, 2, 2, 1, 2, 2, 1, 1, 1, 1, 2, 3], [2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 2, 3], [2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 2, 3], [2, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 2, 3], [2, 2, 2, 1, 1, 2, 1, 2, 1, 2, 1, 1, 2, 2, 2, 2], [2, 3, 2, 2, 1, 1, 2, 1, 2, 1, 1, 2, 2, 3, 2, 1], [2, 2, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2], [3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 3], [3, 2, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 2, 3, 3], [3, 2, 2, 1, 1, 2, 2, 1, 2, 2, 1, 1, 2, 2, 3, 3]]



def get_deer() -> list[list[int]]:
    deer = copy.deepcopy(deer_raw)
    # Do some preprocessing to get rid of empty columns at left and right sides
    for i in range(len(deer)):
        for j in [0, len(deer[i]) - 1]:
            if deer[i][j] == 3:
                deer[i][j] = 2
                pass
            pass
        pass
    return deer

def just_deer() -> list[list[int]]:
    deer = copy.deepcopy(deer_raw)
    deer = [row[:27] for row in deer]
    for i in range(4):
        for j in range(5, 11):
            deer[i][j] = 3
            pass
        pass
    for i in range(12, 20):
        for j in range(18, 27):
            deer[i][j] = 3
            pass
        pass
    
    return deer