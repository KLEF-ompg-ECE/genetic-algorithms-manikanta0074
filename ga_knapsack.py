"""
ga_knapsack.py  —  Genetic Algorithm: 0/1 Knapsack Problem
===========================================================
This program is COMPLETE and works as-is. DO NOT rewrite it.

Your task:
  1. Read the code and understand how it works
  2. Run the 2 experiments described in README.md
  3. Save the plots and fill in your observations in README.md

HOW TO RUN
----------
    python ga_knapsack.py

PROBLEM
-------
A trekker is packing a 15 kg backpack. There are 15 items to choose from,
each with a weight and a value score. Pick items that maximise total value
without exceeding the weight limit.
"""

import random
import matplotlib.pyplot as plt
import os

# =============================================================================
# PROBLEM DATA
# =============================================================================

ITEMS = [
    # (name,                weight_kg,  value)
    ("Water bottle",          2.0,   9),
    ("First aid kit",         1.5,  10),
    ("Tent",                  4.0,  10),
    ("Sleeping bag",          3.0,   9),
    ("Torch",                 0.5,   6),
    ("Energy bars (x6)",      1.0,   7),
    ("Rain jacket",           1.0,   8),
    ("Map & compass",         0.3,   7),
    ("Camera",                1.2,   5),
    ("Extra clothes",         2.0,   4),
    ("Cooking stove",         1.5,   6),
    ("Rope (10 m)",           2.5,   5),
    ("Sunscreen",             0.3,   4),
    ("Trekking poles",        1.5,   5),
    ("Power bank",            0.8,   6),
]

NUM_ITEMS  = len(ITEMS)
MAX_WEIGHT = 15.0   # kg

WEIGHTS = [item[1] for item in ITEMS]
VALUES  = [item[2] for item in ITEMS]
NAMES   = [item[0] for item in ITEMS]


# =============================================================================
# FITNESS FUNCTION
# =============================================================================

def fitness(chromosome):
    """
    Score a knapsack solution. Higher = better.

    If total weight exceeds MAX_WEIGHT -> score = 0 (invalid solution).
    Otherwise -> score = total value packed.

    Args:
        chromosome : binary list of length NUM_ITEMS
                     1 = pack this item,  0 = leave it behind
    """
    total_weight = sum(WEIGHTS[i] for i in range(NUM_ITEMS) if chromosome[i] == 1)
    total_value  = sum(VALUES[i]  for i in range(NUM_ITEMS) if chromosome[i] == 1)
    if total_weight > MAX_WEIGHT:
        return 0
    return total_value


# =============================================================================
# GA OPERATORS
# =============================================================================

def tournament_select(population, fitnesses, k=3):
    """Pick the best individual from k random candidates."""
    candidates = random.sample(range(len(population)), k)
    winner     = max(candidates, key=lambda i: fitnesses[i])
    return population[winner][:]


def crossover(p1, p2, rate=0.8):
    """Single-point crossover: combine two parents at a random cut point."""
    if random.random() > rate:
        return p1[:]
    cut = random.randint(1, NUM_ITEMS - 1)
    return p1[:cut] + p2[cut:]


def mutate(chromosome, rate):
    """
    Bit-flip mutation: each gene flips (0->1 or 1->0) with probability rate.

    EXPERIMENT 2: this rate is controlled by mutation_rate in run_ga()
    Try: 0.01  (very rare flips  - low diversity)
         0.05  (default          - balanced)
         0.30  (frequent flips   - too chaotic)
    """
    result = chromosome[:]
    for i in range(NUM_ITEMS):
        if random.random() < rate:
            result[i] = 1 - result[i]
    return result


# =============================================================================
# GENETIC ALGORITHM
# =============================================================================

def run_ga(
    population_size = 20,
    generations     = 50,
    crossover_rate  = 0.8,
    mutation_rate   = 0.05,   # <- EXPERIMENT 2: change this value
    tournament_size = 3,
    seed            = 42,
):
    """
    Run the Genetic Algorithm to maximise knapsack value.

    KEY PARAMETER
    -------------
    mutation_rate : probability of flipping each bit each generation
                    too low  (0.01) -> population loses diversity, gets stuck
                    balanced (0.05) -> good exploration and exploitation
                    too high (0.30) -> too random, destroys good solutions

    Returns
    -------
    best_chromosome : binary list
    best_value      : int
    value_log       : list of best value per generation (for plotting)
    """
    random.seed(seed)

    population = [
        [random.randint(0, 1) for _ in range(NUM_ITEMS)]
        for _ in range(population_size)
    ]

    best_chromosome = None
    best_value      = -1
    value_log       = []

    for _ in range(generations):
        fitnesses = [fitness(c) for c in population]

        gen_best_i = max(range(population_size), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_i] > best_value:
            best_value      = fitnesses[gen_best_i]
            best_chromosome = population[gen_best_i][:]

        value_log.append(best_value)

        # Elitism: always keep the best
        next_gen = [best_chromosome[:]]
        while len(next_gen) < population_size:
            p1    = tournament_select(population, fitnesses, tournament_size)
            p2    = tournament_select(population, fitnesses, tournament_size)
            child = crossover(p1, p2, crossover_rate)
            child = mutate(child, mutation_rate)
            next_gen.append(child)

        population = next_gen

    return best_chromosome, best_value, value_log


# =============================================================================
# OUTPUT HELPERS
# =============================================================================

def print_solution(chromosome):
    total_weight = sum(WEIGHTS[i] for i in range(NUM_ITEMS) if chromosome[i] == 1)
    total_value  = sum(VALUES[i]  for i in range(NUM_ITEMS) if chromosome[i] == 1)
    packed = [NAMES[i] for i in range(NUM_ITEMS) if chromosome[i] == 1]
    valid  = total_weight <= MAX_WEIGHT
    print("\n  Best Packing List")
    print("-" * 38)
    for item in packed:
        print(f"  + {item}")
    print("-" * 38)
    print(f"  Weight : {total_weight:.1f} / {MAX_WEIGHT} kg")
    print(f"  Value  : {total_value}")
    print(f"  Valid  : {'Yes' if valid else 'No - Over limit!'}\n")


def save_plot(value_log, filename, title):
    os.makedirs("plots", exist_ok=True)
    plt.figure(figsize=(9, 4))
    plt.plot(value_log, color="seagreen", linewidth=2, marker="o", markersize=3)
    plt.xlabel("Generation")
    plt.ylabel("Best Value")
    plt.title(f"GA Convergence - {title}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"  Saved -> {filename}")


def save_combined_plot(logs_dict):
    """
    Save a single figure with all 4 experiment curves overlaid.
    logs_dict : { label_str : value_log_list }
    """
    os.makedirs("plots", exist_ok=True)
    colors = {
        "Baseline (0.05)":       "seagreen",
        "Exp 2a - rate=0.01":    "steelblue",
        "Exp 2b - rate=0.05":    "darkorange",
        "Exp 2c - rate=0.30":    "crimson",
    }
    plt.figure(figsize=(10, 5))
    for label, log in logs_dict.items():
        plt.plot(log, label=label, linewidth=2,
                 color=colors.get(label, None), marker="o", markersize=3)
    plt.xlabel("Generation")
    plt.ylabel("Best Value")
    plt.title("GA Convergence — All Experiments")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = "plots/all_experiments.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved -> {path}")


# =============================================================================
# RUN YOUR EXPERIMENTS HERE
# =============================================================================

if __name__ == "__main__":

    all_logs = {}   # collect logs for the combined plot

    # ==========================================================================
    # EXPERIMENT 1 - Baseline
    # Run as-is. Do NOT change any parameters here.
    # ==========================================================================
    print("=" * 48)
    print("  EXPERIMENT 1 - Baseline")
    print("=" * 48)

    best_chr, best_val, val_log = run_ga(
        population_size=20, generations=50,
        crossover_rate=0.8, mutation_rate=0.05,
        tournament_size=3, seed=42
    )
    print_solution(best_chr)
    print(f"  Generations run : {len(val_log)}")
    print(f"  Value at gen 1  : {val_log[0]}")
    print(f"  Final best value: {best_val}")
    save_plot(val_log, "plots/experiment_1.png",
              "Baseline  mutation_rate=0.05")
    all_logs["Baseline (0.05)"] = val_log

    # ==========================================================================
    # EXPERIMENT 2 - Vary mutation_rate
    # Three sub-runs: 0.01 | 0.05 | 0.30
    # ==========================================================================

    exp2_configs = [
        ("2a", 0.01, "plots/experiment_2a.png", "Exp 2a - rate=0.01"),
        ("2b", 0.05, "plots/experiment_2b.png", "Exp 2b - rate=0.05"),
        ("2c", 0.30, "plots/experiment_2c.png", "Exp 2c - rate=0.30"),
    ]

    for tag, rate, plot_path, label in exp2_configs:
        print("=" * 48)
        print(f"  EXPERIMENT {tag} - mutation_rate={rate}")
        print("=" * 48)

        best_chr2, best_val2, val_log2 = run_ga(
            population_size=20, generations=50,
            crossover_rate=0.8, mutation_rate=rate,
            tournament_size=3, seed=42
        )
        print_solution(best_chr2)
        print(f"  Generations run : {len(val_log2)}")
        print(f"  Value at gen 1  : {val_log2[0]}")
        print(f"  Final best value: {best_val2}")
        save_plot(val_log2, plot_path, label)
        all_logs[label] = val_log2

    # ==========================================================================
    # COMBINED PLOT — all 4 curves in one figure
    # ==========================================================================
    save_combined_plot(all_logs)
    print("\nDone! Check the plots/ directory for all output images.")