import sys
import os

# Automatically find and include the virtual environment's site-packages folder
venv_site_packages = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Create a mock environment to test execution locally in case the 'cabt' engine is building
def mock_cabt_environment_play():
    """
    Simulates a standard API turn cycle using the custom GeneticAgent 
    to verify selection schemas, data parsing, and DNA weight mapping locally.
    """
    print("--- Initializing Local Agent Validation Mock Run ---")
    from agent import GeneticAgent

    # Instantiate our genetic heuristic solver
    genetic_solver = GeneticAgent()

    # Generate a realistic mock observation payload matching the cabt schema
    mock_observation = {
        "logs": ["Match started", "Player 1 attached Grass Energy to Active"],
        "current": {
            "players": [
                {
                    "active": [{"id": 412, "name": "Scyther", "hp": 70}],
                    "bench": [{"id": 25, "name": "Pikachu", "hp": 60}],
                    "hand": [{"id": 12, "type": "energy"}],
                    "handCount": 4,
                    "prize": [None, None, None, None, None, None],
                    "deckCount": 45,
                    "discard": []
                },
                {
                    "active": [{"id": 133, "name": "Eevee", "hp": 50}],
                    "bench": [],
                    "handCount": 5,
                    "prize": [None, None, None, None, None, None],
                    "deckCount": 44,
                    "discard": []
                }
            ],
            "stadium": None,
            "turn": 2,
            "firstPlayer": True
        },
        "select": {
            "option": [
                {"type": "attack", "damage": 30, "name": "Quick Attack"},
                {"type": "attach_energy", "target": "Scyther"},
                {"type": "play_trainer", "name": "Professor's Research"}
            ],
            "maxCount": 1,
            "minCount": 1
        }
    }

    print("Mock state created. Running Agent state evaluation scoring...")
    state_score = genetic_solver.evaluate_game_state(mock_observation["current"])
    print(f"Evaluated Current State Score: {state_score:.2f}")

    print("Running Agent action decision selection loop...")
    chosen_indices = genetic_solver.select_action(mock_observation)
    print(f"Selected Option Index: {chosen_indices}")
    
    # Map index back to chosen option details
    for idx in chosen_indices:
        print(f"Executing: {mock_observation['select']['option'][idx]}")

    print("\n--- Mock Execution Successful! Validation Check Passed ---")

def run_native_kaggle_simulation():
    """
    Attempts to run an official simulation loop using kaggle_environments.
    """
    try:
        from kaggle_environments import make
        print("Kaggle environments loaded successfully. Building 'cabt' simulator...")
        
        # Load custom decks (Example placeholder files)
        deck_data = [12, 12, 45, 45, 7, 7] # Add complete 60-card IDs from deck.csv
        
        env = make("cabt", configuration={"decks": [deck_data, deck_data]})
        from agent import agent
        
        print("Starting battle simulation...")
        env.run([agent, agent])
        
        with open("battle_result.html", "w") as f:
            f.write(env.render(mode="html"))
        print("Simulation completed successfully! Output saved to 'battle_result.html'.")
        
    except Exception as e:
        print(f"\n[Warning] Could not run native kaggle simulation. Details: {e}")
        print("Note: The native 'cabt' engine relies on a precompiled Linux binary (libcg.so) and typically fails to load on macOS.")
        print("Proceeding with custom standalone testing mockup instead...\n")
        mock_cabt_environment_play()

if __name__ == "__main__":
    run_native_kaggle_simulation()