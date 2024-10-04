import csv


# Funzione per leggere i valori dal file CSV
def read_rewards_config(file_path):
    with open(file_path, mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            return {
                "FOOD_REWARD": int(row["FOOD_REWARD"]),
                "GHOST_REWARD": int(row["GHOST_REWARD"]),
                "DANGER_ZONE_REWARD": int(row["DANGER_ZONE_REWARD"]),
                "CAPSULE_REWARD": int(row["CAPSULE_REWARD"]),
                "BLANK_REWARD": float(row["BLANK_REWARD"]),
                "THETA": float(row["THETA"]),
                "DISCOUNT_FACTOR": float(row["DISCOUNT_FACTOR"]),
                "SAFETY_DISTANCE": int(row["SAFETY_DISTANCE"]),
                "MAX_ITERATIONS": int(row["MAX_ITERATIONS"]),
                "NOISE": float(row["NOISE"]),
            }


# Legge i valori dal file CSV
rewards_config = read_rewards_config("parameters.csv")

# Assegna i valori alle variabili
FOOD_REWARD = rewards_config["FOOD_REWARD"]
GHOST_REWARD = rewards_config["GHOST_REWARD"]
DANGER_ZONE_REWARD = rewards_config["DANGER_ZONE_REWARD"]
CAPSULE_REWARD = rewards_config["CAPSULE_REWARD"]
BLANK_REWARD = rewards_config["BLANK_REWARD"]
THETA = rewards_config["THETA"]
SAFETY_DISTANCE = rewards_config["SAFETY_DISTANCE"]
MAX_ITERATIONS = rewards_config["MAX_ITERATIONS"]
NOISE = rewards_config["NOISE"]

# Scrive nuove righe nel file CSV per ogni valore di DISCOUNT_FACTOR
with open("parameters.csv", mode="w", newline="") as file:
    csv_writer = csv.writer(file)
    # Scrive l'intestazione
    csv_writer.writerow(
        [
            "FOOD_REWARD",
            "GHOST_REWARD",
            "DANGER_ZONE_REWARD",
            "CAPSULE_REWARD",
            "BLANK_REWARD",
            "THETA",
            "DISCOUNT_FACTOR",
            "SAFETY_DISTANCE",
            "MAX_ITERATIONS",
            "NOISE",
        ]
    )
    for i in range(11):
        DISCOUNT_FACTOR = round(i * 0.1, 1)
        csv_writer.writerow(
            [
                FOOD_REWARD,
                GHOST_REWARD,
                DANGER_ZONE_REWARD,
                CAPSULE_REWARD,
                BLANK_REWARD,
                THETA,
                DISCOUNT_FACTOR,
                SAFETY_DISTANCE,
                MAX_ITERATIONS,
                NOISE,
            ]
        )
