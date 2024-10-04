import subprocess
import csv
import os
import re
import time
import psutil

PROJECT_DIR = r"C:\Users\nico\Documents\GitHub\pacman\reinforcement"

run_count = 0


def run_pacman_with_parameters(params):
    global run_count
    run_count += 1
    print(f"Starting run {run_count}")

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

    print(f"Updated parameters for run {run_count}")

    # Run the Pacman command with a timeout
    command = f"python pacman.py -p MDPAgentCopy -l smallGrid -n 10000 -q"
    print(f"Executing command: {command}")
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            shell=True,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=1200,  # 5 minutes timeout
        )
        end_time = time.time()
        print(f"Pacman execution completed in {end_time - start_time:.2f} seconds")
    except subprocess.TimeoutExpired:
        print(f"Run {run_count} timed out after 5 minutes")
        return None, params

    print(f"Pacman output for run {run_count}:")
    print(result.stdout)
    print(result.stderr)

    # Extract win rate
    win_rate_line = next(
        (line for line in result.stdout.split("\n") if line.startswith("Win Rate:")),
        None,
    )
    win_rate = None
    if win_rate_line:
        match = re.search(r"\(([\d.]+)\)", win_rate_line)
        if match:
            win_rate = float(match.group(1))

    print(f"Extracted win rate for run {run_count}: {win_rate}")

    return win_rate, params


# Main execution
input_csv_path = os.path.join(PROJECT_DIR, "parameters.csv")
output_csv_path = os.path.join(PROJECT_DIR, "win_rates.csv")

with open(input_csv_path, "r") as input_csvfile:
    reader = csv.DictReader(input_csvfile)
    input_fieldnames = reader.fieldnames

output_fieldnames = (
    input_fieldnames + ["Win Rate"]
    if "Win Rate" not in input_fieldnames
    else input_fieldnames
)

with open(input_csv_path, "r") as input_csvfile, open(
    output_csv_path, "w", newline=""
) as output_csvfile:
    reader = csv.DictReader(input_csvfile)
    writer = csv.DictWriter(output_csvfile, fieldnames=output_fieldnames)
    writer.writeheader()

    for row in reader:
        print(f"\nProcessing parameter set {run_count + 1}")
        start_time = time.time()

        params = {
            k: (
                True
                if v.lower() == "true"
                else (
                    False
                    if v.lower() == "false"
                    else (
                        int(v)
                        if k in ["SAFETY_DISTANCE", "MAX_ITERATIONS"]
                        else float(v)
                    )
                )
            )
            for k, v in row.items()
        }

        win_rate, _ = run_pacman_with_parameters(params)

        output_row = {**row, "Win Rate": win_rate if win_rate is not None else "N/A"}
        output_row = {k: v for k, v in output_row.items() if k in output_fieldnames}

        writer.writerow(output_row)

        end_time = time.time()
        print(
            f"Parameter set {run_count} completed in {end_time - start_time:.2f} seconds"
        )

        # Print current memory usage
        process = psutil.Process(os.getpid())
        print(f"Current memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")

print("All parameter sets have been processed and win rates saved to win_rates.csv")
