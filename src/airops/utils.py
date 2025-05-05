import json, os, time
from pathlib import Path
from typing import List, Dict, Any
import functools
from openai import RateLimitError


def get_repo_root():
    """
    Util that gives us root of the repo, helps for location file paths dynamically
    """
    return Path(__file__).resolve().parent.parent.parent


def get_available_integration_actions() -> List[Dict[str, str]]:
    """
    Gets all available integration actions
    """
    repo_root = get_repo_root()
    with open(f'{repo_root}/context/integration_actions.json', 'r') as f:
        integration_actions = sorted(json.load(f), key=lambda x: x['integration'])
        for action in integration_actions:
            action["inputs_schema"] = [
                field for field in action["inputs_schema"] if field["interface"] != "integration"
            ]
    return [{
        'integration': ia['integration'], 'action': ia['action']
    } for ia in integration_actions]


def get_sample_workflow_contexts() -> List[Dict[str, Any]]:
    """
    Gets all sample workflow contexts stored locally
    """
    sample_workflow_contexts = []
    repo_root = get_repo_root()
    for file in os.listdir(f'{repo_root}/context/sample_workflows/'):
        fp = os.path.join(f'{repo_root}/context/sample_workflows/', file)
        with open(fp, 'r') as file:
            sample_workflow_contexts.append(json.load(file))
    return sample_workflow_contexts


def handle_errors(retries=3, sleep_time=60):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except RateLimitError as e:
                    if retries is not None and attempt >= retries:
                        raise
                    attempt += 1
                    print(f"Retryable error: {e}. Retrying in {sleep_time} seconds... (Attempt {attempt})")
                    time.sleep(sleep_time)
                except Exception as e:
                    print(f"Error: {e}")
                    return None

        return wrapper

    return decorator
