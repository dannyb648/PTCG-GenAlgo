import random

class GeneticAgent:
    """
    A parameterized heuristic agent for the PTCG AI Battle Challenge.
    This agent's behavior is guided by a DNA dictionary of weights,
    making it ready to be optimized using Genetic Algorithms (GA) or Neuroevolution.
    """
    def __init__(self, dna: dict = None):
        # Default starting DNA parameter weights if none are provided
        self.dna = dna if dna else {
            "weight_prize_card": 10.0,
            "weight_active_hp": 0.5,
            "weight_bench_hp": 0.3,
            "weight_energy_attach": 1.2,
            "weight_hand_advantage": 0.8,
            "weight_status_condition": -2.0,
            "weight_opponent_active_damage": 1.5,
            "weight_evolution_play": 2.5
        }

    def evaluate_game_state(self, current_state: dict) -> float:
        """
        Evaluates the perceived utility of a board state based on the agent's DNA.
        """
        if not current_state:
            return 0.0

        score = 0.0
        players = current_state.get("players", [])
        if len(players) < 2:
            return score

        # Self State Variables (Index 0)
        me = players[0]
        opp = players[1]

        # 1. Evaluate hand size advantage
        hand_count = me.get("handCount", len(me.get("hand", [])))
        score += hand_count * self.dna["weight_hand_advantage"]

        # 2. Evaluate status conditions on our active pokemon
        active_list = me.get("active", [])
        if active_list and active_list[0] is not None:
            active_pkmn = active_list[0]
            # Penalize negative statuses
            status_penalty = 0
            for cond in ["poisoned", "burned", "asleep", "paralyzed", "confused"]:
                if me.get(cond, False):
                    status_penalty += 1
            score += status_penalty * self.dna["weight_status_condition"]
            
            # Value remaining HP
            hp = active_pkmn.get("hp", 0)
            score += hp * self.dna["weight_active_hp"]

        # 3. Evaluate Bench Preservation
        for benched in me.get("bench", []):
            if benched:
                score += benched.get("hp", 0) * self.dna["weight_bench_hp"]

        # 4. Evaluate Opponent Vulnerability
        opp_active_list = opp.get("active", [])
        if opp_active_list and opp_active_list[0] is not None:
            opp_active = opp_active_list[0]
            opp_hp = opp_active.get("hp", 0)
            # Higher score for damaging or weakening opponent active
            score -= opp_hp * self.dna["weight_opponent_active_damage"]

        # 5. Reward card drawing/prizes taken (inverse of remaining prizes)
        prizes_remaining = len([p for p in me.get("prize", []) if p is not None])
        score += (6 - prizes_remaining) * self.dna["weight_prize_card"]

        return score

    def select_action(self, obs_dict: dict) -> list[int]:
        """
        Processes turn observations and selects the index/indices of the best legal option.
        """
        select_info = obs_dict.get("select")
        if not select_info:
            return [0]

        options = select_info.get("option", [])
        max_count = select_info.get("maxCount", 1)
        min_count = select_info.get("minCount", 1)

        if not options:
            return []

        # Evaluate and score individual choices based on heuristic rules
        scored_options = []
        for index, opt in enumerate(options):
            score = 0.0
            opt_type = opt.get("type", "")

            # Heuristics based on option types matching DNA parameters
            if opt_type == "attach_energy":
                score += 10.0 * self.dna["weight_energy_attach"]
            elif opt_type == "attack":
                # High priority if it executes damage
                damage = opt.get("damage", 0)
                score += (damage * 0.1) * self.dna["weight_opponent_active_damage"]
            elif opt_type == "evolve":
                score += 15.0 * self.dna["weight_evolution_play"]
            elif opt_type == "play_trainer":
                score += 5.0 * self.dna["weight_hand_advantage"]
            else:
                # Add random exploration baseline to diversify evaluations
                score += random.uniform(-0.5, 0.5)

            scored_options.append((score, index))

        # Sort the options in descending order of utility value
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        # Select the target count of indices requested by the simulation
        selected_indices = [idx for _, idx in scored_options[:max_count]]
        
        # Ensure we always return at least the minimum allowed selections
        while len(selected_indices) < min_count:
            fallback = random.choice(range(len(options)))
            if fallback not in selected_indices:
                selected_indices.append(fallback)

        return selected_indices

# Instantiated Kaggle Interface
agent_instance = GeneticAgent()

def agent(obs_dict: dict) -> list[int]:
    """
    Standard entry-point function signature defined by the Kaggle Environment interface.
    """
    return agent_instance.select_action(obs_dict)