Pokémon TCG AI Battle Challenge (cabt Engine) — AI Context & Architecture Blueprint

This document acts as an executive brief and technical guide to align your IDE's AI system with the rules, requirements, and state transitions of the Pokémon Trading Card Game (PTCG) AI Battle Challenge (Pokéca ABC 2026).

1. Project Objective & Challenge Parameters

The goal is to develop an intelligent agent capable of playing the standard Pokémon Trading Card Game at a competitive, championship level.

Platform: Kaggle (Simulation Competition Track).

Engine: cabt Engine (built for kaggle-environments by Matsuo Institute and HEROZ).

Execution Time Limit: 10 minutes cumulative time per match per player. Exceeding 10 minutes leads to an immediate loss. Speed and computational efficiency are critical constraint vectors.

Target Approach: Hybrid Heuristics + Genetic Algorithm Parameter Optimization. The agent will read game state parameters, process them using mutated scalar weights, and output the optimal action index.

2. Environment Interface & Game State Architecture (POMDP)

The competition is framed as a Partially Observable Markov Decision Process (POMDP). The agent receives an observation dictionary on its turn, calculates its utility space, and returns list indices representing actions.

                  ┌─────────────────────────────────┐
                  │          Kaggle Engine          │
                  └────────────────┬────────────────┘
                                   │
                    Sends Turn     │  Receives Action
                    Observation    │  Selection Index
                                   ▼
                  ┌─────────────────────────────────┐
                  │           Your Agent            │
                  │   (Genetic Heuristic / POMDP)   │
                  └─────────────────────────────────┘


Observation Payload Structure

Each turn, the state is passed to the agent as obs_dict["select"] and obs_dict["current"]:

{
    "logs": [...],           # History of plays, damage, and search actions
    "current": {             # Current board state (None during initial deck selection)
        "players": [
            {                # Index 0: Self
                "active": [Pokemon],      # Size 0 or 1. Active Pokémon on board
                "bench": [Pokemon],       # Max size 5. List of benched Pokémon
                "hand": [Card],           # Revealed hand card structures
                "handCount": int,         # Disclosed total hand size
                "prize": [Card],          # Face-down prize cards (hidden as None)
                "deckCount": int,         # Remaining library count
                "discard": [Card],        # Discard pile contents
                "poisoned": bool, "burned": bool, "asleep": bool, "paralyzed": bool, "confused": bool
            },
            {                # Index 1: Opponent
                "active": [Pokemon],
                "bench": [Pokemon],
                "handCount": int,         # Hand cards are hidden (represented by count only)
                "prize": [Card],          # Face-down prize cards
                "deckCount": int,
                "discard": [Card]
            }
        ],
        "stadium": Card,     # Active stadium card on field
        "turn": int,         # Game turn counter
        "firstPlayer": bool  # True if player 1 is taking the first turn
    },
    "select": {              # Available choices for the current decision frame
        "option": [Option],  # List of legal decisions presented by the engine
        "maxCount": int,     # Maximum number of options that must be selected
        "minCount": int      # Minimum number of options that must be selected
    }
}


Action Contract

The engine only returns strictly legal moves. The agent's task is to analyze obs_dict["select"]["option"] and return a list of integer indices mapping to the chosen option(s).

Output signature: list[int] of length between minCount and maxCount.

3. The Genetic Algorithm Workflow

Our strategic engine is built to evolve the weights of a parameterized evaluation network. Instead of hardcoding relative card values, we expose variables to natural selection.

The Chromosome (DNA) Representation

The DNA is a normalized vector of floats representing game priorities:

DNA Gene Index

Gene Parameter

Ideal Goal

0

weight_prize_card

Weight of taking prize cards (victory condition)

1

weight_active_hp

Value assigned to keeping our Active Pokémon alive

2

weight_bench_hp

Preservation coefficient for benched Pokémon

3

weight_energy_attach

Value of energy card attachment density

4

weight_hand_advantage

Marginal value of holding a large card hand

5

weight_status_condition

Value penalizing negative status effects on active

6

weight_opponent_active_damage

Offensive aggression multiplier against opponent active

The Fitness Function Evaluation

An agent's fitness is evaluated across a generation of matches to minimize variance caused by coin flips and card shuffling:

$$Fitness = (W \times 1000) + (P \times 100) + (E \times 10) - (KO \times 50) - (T \times 5)$$

Where:

$W = 1$ if match won, else $0$

$P$ = Count of prize cards taken

$E$ = Successfully attached energy cards

$KO$ = Own active/benched Pokémon knocked out

$T$ = Total turn steps taken (encourages fast execution/tempo)

4. Development Goals & Evolution Milestones

Phase 1 (Baseline Simulation): Run mock battles using a parameter-driven Python agent playing against a randomized agent.

Phase 2 (Genetic Tuning): Set up a localized evolutionary script that generates 50 agents, breeds them using multipoint crossover, mutates genes with Gaussian noise, and tests them over 500 generation loops.

Phase 3 (Kaggle Export): Package the optimal evolved weight matrix directly inside agent.py, bundle it with your specified deck.csv, and submit it as a .tar.gz directly to Kaggle.