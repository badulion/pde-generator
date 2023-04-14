import numpy as np

LOW_SEED = 10000000
HIGH_SEED = 80000000

np.random.seed(42)
seeds = np.random.choice(range(LOW_SEED, HIGH_SEED), size=1000000)
parts = np.split(seeds, 100)

for i, seed_split in enumerate(parts):
    seed_split = [f"{seed}\n" for seed in seed_split]
    with open(f"config/seeds/seeds_{i}.txt", 'w') as f:
        f.writelines(seed_split)
