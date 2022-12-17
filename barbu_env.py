# Reference MultiAgentEnv: https://github.com/ray-project/ray/blob/master/rllib/env/wrappers/pettingzoo_env.py

from barbu_game import BarbuGame
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from gym import spaces


class BarbuMultiAgentEnv(MultiAgentEnv):
    observation_space = spaces.Dict(
        {
            "player_cards": spaces.Tuple(
                spaces.Discrete(53, start=-1) for _ in range(13)
            ),
            "round_cards": spaces.Tuple(
                spaces.Discrete(53, start=-1) for _ in range(8)
            )
        }
    )

    action_space = spaces.Discrete(52)

    _agent_ids = ("player_0", "player_1", "player_2", "player_3")

    def __init__(self, rule="reds"):
        super().__init__()
        self.game = BarbuGame(rule)
        

    def reset(self):
        self.game = BarbuGame("reds")

        starter = self.game.get_next_player()

        return {f"player_{starter}": {
            "player_cards": self.game.player_cards[starter],
            "round_cards": self.game.round_cards,
        }}

        
    
    def step(self, action):
        reward = {
            "player_0": 0,
            "player_1": 0,
            "player_2": 0,
            "player_3": 0
        }

        done = {
            "player_0": False,
            "player_1": False,
            "player_2": False,
            "player_3": False
        }

        acting_player = self.game.get_next_player()

        try:
            raise Exception(action)
            self.game.set_player_input(acting_player, action[f"player_{acting_player}"])
        except AssertionError as e:
            print(e)
            
            reward[f"player_{acting_player}"] = -100
            done = {p: True for p in done}
            return {}, reward, done, {}

        if self.game.is_last_player_in_round():
            point_diffs = self.game.evaluate_round()
            self.game.round_start_player = self.game.get_next_player()

            for i in range(4):
                reward[f"player_{i}"] = point_diffs[i]


        if self.game.game_finished():
            done = {p: True for p in done}

            return {}, reward, done, {}

        next_player = self.game.get_next_player()

        obs = {f"player_{next_player}": {
            "player_cards": self.game.player_cards[next_player],
            "round_cards": self.game.round_cards,
        }}

        return obs, reward, done, {}

    def close(self):
        pass

    def seed(self, seed=None):
        if seed is not None:
            self.game.set_seed(seed)
        else:
            self.game.set_seed(np.random.randint(2**32))

    def render(self, mode='text'):
        pass