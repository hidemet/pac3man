from pacman import Directions
from game import Agent
import api
import random
import util
import sys
from collections import defaultdict

FOOD_REWARD = 10
GHOST_REWARD = -1000
DANGER_ZONE_REWARD = -500
CAPSULE_REWARD = 100
BLANK_REWARD = -0.04
WALL_REWARD = 0

THETA = 0.001
DISCOUNT_FACTOR = 0.9
SAFETY_DISTANCE = 1


class MDPAgentCopy(Agent):
    def __init__(self, max_iterations=500, noise=0.2):
        self.max_iterations = max_iterations
        self.noise = noise

        self.map_width = None
        self.map_height = None
        self.wall_positions = None
        self.rewards = dict()
        self.values = util.Counter()
        self.legal_positions = None

        self.move_offsets = {
            Directions.NORTH: (0, 1),
            Directions.SOUTH: (0, -1),
            Directions.EAST: (1, 0),
            Directions.WEST: (-1, 0),
        }

    def registerInitialState(self, game_state):
        self.corners = api.get_corners(game_state)
        self.map_width, self.map_height = api.get_map_dimensions(game_state)
        # Uso frozenset per evitare che il set venga modificato
        """
        Hashing: frozenset, essendo immutabile, ha un valore hash. Questo significa che può essere utilizzato in contesti che richiedono l'hashing, come chiavi di dizionario o elementi di altri set. L'immobilità garantisce che il valore hash rimanga costante, rendendo le operazioni di hashing e confronto potenzialmente più efficienti per collezioni grandi o per l'uso in strutture dati complesse.
        """
        self.wall_positions = frozenset(api.get_walls(game_state))
        self.legal_positions = frozenset(
            (x, y)
            for x in range(self.map_width)
            for y in range(self.map_height)
            if (x, y) not in self.wall_positions
        )
        self.rewards = {pos: BLANK_REWARD for pos in self.legal_positions}

        self.previous_foods = set()

    def final(self, state):
        # print("Il gioco è finito")
        # print("Punteggio: ", game_state.getScore())
        pass

    def value_iteration(self):
        for i in range(self.max_iterations):
            delta = 0
            for cell in self.legal_positions:
                cell_value = self.values[cell]
                self.values[cell] = self._get_best_policy(cell)
                delta = max(delta, abs(cell_value - self.values[cell]))
            if delta < THETA:
                # print("Iterazioni: ", i)
                return i

    def _get_best_policy(self, cell):
        return max(
            self.__compute_q_value_from_values(cell, action)
            for action in self.move_offsets
        )

    def __compute_q_value_from_values(self, cell, action):
        return sum(
            prob * (self.rewards[next_cell] + DISCOUNT_FACTOR * self.values[next_cell])
            for next_cell, prob in self.__get_transition_states_and_probs(cell, action)
        )

    def __get_transition_states_and_probs(self, cell, action):
        x, y = cell
        dx, dy = self.move_offsets[action]
        intended_next_cell = (x + dx, y + dy)

        if intended_next_cell in self.wall_positions:
            return [(cell, 1.0)]

        transitions = [(intended_next_cell, 1 - self.noise)]

        perpendicular_actions = (
            [Directions.EAST, Directions.WEST]
            if action in [Directions.NORTH, Directions.SOUTH]
            else [Directions.NORTH, Directions.SOUTH]
        )
        for side_action in perpendicular_actions:
            dx, dy = self.move_offsets[side_action]
            side_cell = (x + dx, y + dy)
            if side_cell in self.legal_positions:
                transitions.append((side_cell, self.noise / 2))
            else:
                transitions.append((cell, self.noise / 2))

        return transitions

    def _update_rewards(self, state):
        food_positions = set(api.get_food(state))
        capsule_positions = set(api.get_capsules(state))
        ghost_positions = set(api.get_ghosts(state))

        danger_zones = set(
            api.get_danger_zones(
                state,
                api.whereAmI(state),
                ghost_positions,
                self.map_width,
                self.map_height,
                SAFETY_DISTANCE,
            )
        )

        blank_positions = (
            self.legal_positions
            - food_positions
            - capsule_positions
            - ghost_positions
            - danger_zones
        )

        ghost_reward, danger_reward = api.calculate_ghost_and_danger_zone_rewards(
            state, GHOST_REWARD, DANGER_ZONE_REWARD
        )

        self.rewards.update(
            {pos: FOOD_REWARD for pos in food_positions - self.previous_foods}
        )
        self.previous_foods = food_positions
        self.rewards.update({pos: CAPSULE_REWARD for pos in capsule_positions})
        self.rewards.update({pos: ghost_reward for pos in ghost_positions})
        self.rewards.update({pos: danger_reward for pos in danger_zones})
        self.rewards.update({pos: BLANK_REWARD for pos in blank_positions})

    def getAction(self, state):
        self._update_rewards(state)
        self.value_iteration()
        pacman_pos = api.whereAmI(state)
        legal_actions = api.legalActions(state)
        legal_actions.remove(Directions.STOP)

        best_action = max(
            legal_actions,
            key=lambda action: self.__compute_q_value_from_values(pacman_pos, action),
        )
        return api.makeMove(best_action, legal_actions)
