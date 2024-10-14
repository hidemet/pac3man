from pacman import Directions
from game import Agent
import api
import random
import util
import sys
from collections import defaultdict

FOOD_REWARD = 10.0
GHOST_REWARD = -500.0
DANGER_ZONE_REWARD = -250.0
CAPSULE_REWARD = 50.0
BLANK_REWARD = -0.04
THETA = 0.001
DISCOUNT_FACTOR = 0.6
SAFETY_DISTANCE = 1
MAX_ITERATIONS = 500
NOISE = 0.2
GHOSTBUSTER_MODE = True


class MDPAgent(Agent):
    def __init__(self):
        self.max_iterations = MAX_ITERATIONS
        self.noise = NOISE
        self.ghostbuster_mode = GHOSTBUSTER_MODE
        self.map_width = None
        self.map_height = None
        self.wall_positions = None
        self.rewards = dict()
        self.values = util.Counter()
        self.legal_states = None

        self.move_offsets = {
            Directions.NORTH: (0, 1),
            Directions.SOUTH: (0, -1),
            Directions.EAST: (1, 0),
            Directions.WEST: (-1, 0),
        }

    def registerInitialState(self, game_state):
        """
        Registra lo stato iniziale del gioco.

        Args:
            game_state (GameState): Lo stato iniziale del gioco.
        """
        self.corners = api.get_corners(game_state)
        self.map_width, self.map_height = api.get_map_dimensions(game_state)
        # Uso frozenset per evitare che il set venga modificato
        """
        Hashing: frozenset, essendo immutabile, ha un valore hash. Questo significa che può essere utilizzato in contesti che richiedono l'hashing, come chiavi di dizionario o elementi di altri set. L'immobilità garantisce che il valore hash rimanga costante, rendendo le operazioni di hashing e confronto potenzialmente più efficienti per collezioni grandi o per l'uso in strutture dati complesse.
        """
        self.wall_positions = frozenset(api.get_walls(game_state))
        self.legal_states = frozenset(
            (x, y)
            for x in range(self.map_width)
            for y in range(self.map_height)
            if (x, y) not in self.wall_positions
        )

    def final(self, game_state):
        # Numero di iterazioni effettuate
        # print("Il gioco è finito")
        # print("Punteggio: ", game_state.getScore())
        pass

    def value_iteration(self):
        for i in range(self.max_iterations):
            delta = 0
            for state in self.legal_states:
                state_value = self.values[state]
                self.values[state] = self._get_best_policy(state)
                delta = max(delta, abs(state_value - self.values[state]))
            if delta < THETA:
                # print(" ha superato la soglia con  iterazioni : ", i)
                return i

    def _get_best_policy(self, state):
        """
        Restituisce la migliore policy (azione) per uno stato dato.

        Args:
            state (tuple): Lo stato attuale.

        Returns:
            (float): La migliore azione da intraprendere nello stato dato.
        """

        return max(
            self.__compute_q_value_from_values(state, action)
            for action in self.move_offsets
        )

    def __compute_q_value_from_values(self, state, action):
        """
        Calcola il Q-value per uno stato e un'azione dati.

        Args:
            state (tuple): Lo stato attuale.
            action (str): L'azione da intraprendere.

        Returns:
            (float): Il q-value calcolato.
        """

        return sum(
            prob
            * (self.rewards[next_state] + DISCOUNT_FACTOR * self.values[next_state])
            for next_state, prob in self.__get_transition_states_and_probs(
                state, action
            )
        )

    def _next_state(self, state, offset):
        """
        Calcola lo stato successore dato uno stato attuale e lo spostamento (offset).

        Args:
            state (tuple): Lo stato attuale.
            offset (tuple): L'offset da applicare allo stato attuale.

        Returns:
            (tuple): Lo stato successivo.
        """
        next_state = (int(state[0] + offset[0]), int(state[1] + offset[1]))
        return state if next_state in self.wall_positions else next_state

    def __get_transition_states_and_probs(self, state, action):
        """
        Dato una stato attuale e l'azione da intraprendere restituisce gli stati successori e le probabilità di transizione.

        Args:
            state (tuple): Lo stato attuale.
            action (str): L'azione da intraprendere.

        Returns:
            (list): Una lista di tuple contenenti lo stato successore e la probabilità di transizione.
        """

        x, y = state
        dx, dy = self.move_offsets[action]
        intended_next_state = self._next_state(state, self.move_offsets[action])

        transitions = [(intended_next_state, 1 - self.noise)]

        perpendicular_actions = (
            [Directions.EAST, Directions.WEST]
            if action in [Directions.NORTH, Directions.SOUTH]
            else [Directions.NORTH, Directions.SOUTH]
        )

        noise_sum = 0
        for side_action in perpendicular_actions:
            dx, dy = self.move_offsets[side_action]
            side_state = (x + dx, y + dy)
            if side_state in self.wall_positions:
                noise_sum += self.noise / 2
            else:
                transitions.append((side_state, self.noise / 2))

            if noise_sum > 0:
                transitions.append((state, noise_sum))

        return transitions

    def _update_rewards(self, game_state):
        """
        Aggiorna i reward per ogni stato in base allo stato attuale del gioco.

        Args:
            game_state (GameState): Lo stato attuale del gioco.
        """
        food_positions = set(api.get_food(game_state))
        capsule_positions = set(api.get_capsules(game_state))
        ghost_positions = set(api.get_ghosts(game_state))

        danger_zones = set(
            api.get_danger_zones(
                game_state,
                api.whereAmI(game_state),
                ghost_positions,
                self.map_width,
                self.map_height,
                SAFETY_DISTANCE,
            )
        )

        blank_positions = (
            self.legal_states
            - food_positions
            - capsule_positions
            - ghost_positions
            - danger_zones
        )

        ghost_reward, danger_reward = GHOST_REWARD, DANGER_ZONE_REWARD

        if self.ghostbuster_mode:
            ghost_reward, danger_reward = api.calculate_ghost_and_danger_zone_rewards(
                game_state, GHOST_REWARD, DANGER_ZONE_REWARD
            )

        self.rewards.update({pos: FOOD_REWARD for pos in food_positions})
        # self.previous_foods = food_positions
        self.rewards.update({pos: CAPSULE_REWARD for pos in capsule_positions})
        self.rewards.update({pos: ghost_reward for pos in ghost_positions})
        self.rewards.update({pos: danger_reward for pos in danger_zones})
        self.rewards.update({pos: BLANK_REWARD for pos in blank_positions})

    def getAction(self, game_state):
        self._update_rewards(game_state)
        self.value_iteration()
        pacman_pos = api.whereAmI(game_state)
        legal_actions = api.legalActions(game_state)
        legal_actions.remove(Directions.STOP)

        best_action = max(
            legal_actions,
            key=lambda action: self.__compute_q_value_from_values(pacman_pos, action),
        )
        return api.makeMove(best_action, legal_actions)
