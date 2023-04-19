import numpy as np
from archive import write_str_to_tar

LOW_SEED = 100000000
HIGH_SEED = 800000000

np.random.seed(42)
seeds = np.random.choice(range(LOW_SEED, HIGH_SEED), size=1000000)
parts = np.split(seeds, 1000)

for i, seed_split in enumerate(parts):
    seeds_as_str = map(lambda x: f"{x}", seed_split)
    seed_split = "\n".join(seeds_as_str)
    write_str_to_tar(seed_split, filename=f"{i}.txt", tarpath="config/seeds.tar")
