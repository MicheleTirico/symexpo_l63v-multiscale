#!/bin/bash

# python3 examples/od_matrix/symexpo_l63v-multiscale_closest_nodes.py   # TEST
python3 examples/od_matrix/symexpo_l63v-multiscale_get_points_filtered.py # 1. fiter points to say if it si inside, outside, start and end
python3 examples/od_matrix/symexpo_l63v-multiscale_get_distances.py # 2. distance between nodes in matsim and find the closest port
python3 examples/od_matrix/symexpo_l63v-multiscale_distances_points_sym-mat_inside.py # 3. compute distance between nodes in matsim and in Symuvia
python3 examples/od_matrix/symexpo_l63v-multiscale_od_matrix.py # 4. compute od matrix
python3 examples/od_matrix/symexpo_l63v-multiscale_od_matrix_for_sym.py # 5 compute final od matrix for simulation

