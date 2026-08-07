"""
Workflow helper utilities.
"""

from datetime import datetime


def mark_completed(state, agent_name):
    """
    Mark an agent as completed.
    """

    if agent_name not in state.completed_agents:
        state.completed_agents.append(agent_name)


def mark_failed(state, error):
    """
    Mark workflow as failed.
    """

    state.failed = True
    state.error = str(error)


def serialize_state(state):
    """
    Convert workflow state into a dictionary.
    """

    return {
        "experiment_id": state.experiment.id,
        "current_agent": state.current_agent,
        "completed_agents": state.completed_agents,
        "failed": state.failed,
        "error": state.error,
        "finished": state.finished,
        "results": state.results,
    }


def execution_timestamp():
    """
    Current UTC timestamp.
    """

    return datetime.utcnow().isoformat()