import json, os
from pathlib import Path
from typing import List, Dict, Any


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
