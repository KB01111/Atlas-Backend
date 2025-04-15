import cProfile
import pstats

from app.services.agent_runner import run_agent


def profile_agent():
    """Profile the agent runner for performance analysis."""
    profiler = cProfile.Profile()
    profiler.enable()
    # Example: run a minimal agent loop (customize as needed)
    run_agent(agent_id='example', input_data={})
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20)

if __name__ == "__main__":
    profile_agent()
