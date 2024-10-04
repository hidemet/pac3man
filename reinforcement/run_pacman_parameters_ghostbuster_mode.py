import subprocess
import csv
import os
import re

# Definisci il percorso della directory del progetto
PROJECT_DIR = r"C:\Users\nico\Documents\GitHub\pacman\reinforcement"


def run_pacman_with_parameters(params):
    # Percorso completo del file myVapCopyAgents.py
    agent_file_path = os.path.join(PROJECT_DIR, "myVapCopyAgents.py")

    # Update the MDPAgentCopy class with new parameters
    with open(agent_file_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("FOOD_REWARD ="):
            lines[i] = f"FOOD_REWARD = {params['FOOD_REWARD']}\n"
        elif line.startswith("GHOST_REWARD ="):
            lines[i] = f"GHOST_REWARD = {params['GHOST_REWARD']}\n"
        elif line.startswith("DANGER_ZONE_REWARD ="):
            lines[i] = f"DANGER_ZONE_REWARD = {params['DANGER_ZONE_REWARD']}\n"
        elif line.startswith("CAPSULE_REWARD ="):
            lines[i] = f"CAPSULE_REWARD = {params['CAPSULE_REWARD']}\n"
        elif line.startswith("BLANK_REWARD ="):
            lines[i] = f"BLANK_REWARD = {params['BLANK_REWARD']}\n"
        elif line.startswith("THETA ="):
            lines[i] = f"THETA = {params['THETA']}\n"
        elif line.startswith("DISCOUNT_FACTOR ="):
            lines[i] = f"DISCOUNT_FACTOR = {params['DISCOUNT_FACTOR']}\n"
        elif line.startswith("SAFETY_DISTANCE ="):
            lines[i] = f"SAFETY_DISTANCE = {params['SAFETY_DISTANCE']}\n"
        elif line.startswith("GHOSTBUSTER_MODE ="):
            lines[i] = f"GHOSTBUSTER_MODE = {params['GHOSTBUSTER_MODE']}\n"
        elif line.startswith("MAX_ITERATIONS ="):
            lines[i] = f"MAX_ITERATIONS = {params['MAX_ITERATIONS']}\n"
        elif line.startswith("NOISE ="):
            lines[i] = f"NOISE = {params['NOISE']}\n"

    with open(agent_file_path, "w") as f:
        f.writelines(lines)

    # Run the Pacman command and capture the output
    command = f"python pacman.py -p MDPAgentCopy -l mediumClassic -n 100 -q"
    result = subprocess.run(
        command, shell=True, cwd=PROJECT_DIR, capture_output=True, text=True
    )

    # Debug: Print full output
    print("Full Pacman output:")
    print(result.stdout)

    # Filter the output for the "Win Rate:" line and extract the float value in parentheses
    win_rate_line = next(
        (line for line in result.stdout.split("\n") if line.startswith("Win Rate:")),
        None,
    )
    win_rate = None
    if win_rate_line:
        match = re.search(r"\(([\d.]+)\)", win_rate_line)
        if match:
            win_rate = float(match.group(1))

    # Debug: Print extracted win rate
    print(f"Extracted win rate: {win_rate}")

    return win_rate, params


# Percorso completo del file CSV di input
input_csv_path = os.path.join(PROJECT_DIR, "parameters.csv")

# Percorso completo del file CSV di output
output_csv_path = os.path.join(PROJECT_DIR, "win_rates.csv")

# Read parameters from CSV, run Pacman for each set, and save win rates
with open(input_csv_path, "r") as input_csvfile, open(
    output_csv_path, "w", newline=""
) as output_csvfile:
    reader = csv.DictReader(input_csvfile)
    fieldnames = list(reader.fieldnames) + ["Win Rate"]
    writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        # Convert string values to appropriate types
        params = {
            "FOOD_REWARD": float(row["FOOD_REWARD"]),
            "GHOST_REWARD": float(row["GHOST_REWARD"]),
            "DANGER_ZONE_REWARD": float(row["DANGER_ZONE_REWARD"]),
            "CAPSULE_REWARD": float(row["CAPSULE_REWARD"]),
            "BLANK_REWARD": float(row["BLANK_REWARD"]),
            "THETA": float(row["THETA"]),
            "DISCOUNT_FACTOR": float(row["DISCOUNT_FACTOR"]),
            "SAFETY_DISTANCE": int(row["SAFETY_DISTANCE"]),
            "GHOSTBUSTER_MODE": bool(row["GHOSTBUSTER_MODE"]),
            "MAX_ITERATIONS": int(row["MAX_ITERATIONS"]),
            "NOISE": float(row["NOISE"]),
        }
        win_rate, params = run_pacman_with_parameters(params)

        # Write parameters and win rate to output CSV
        output_row = {**row, "Win Rate": win_rate if win_rate is not None else "N/A"}
        writer.writerow(output_row)

print("All parameter sets have been processed and win rates saved to win_rates.csv")
