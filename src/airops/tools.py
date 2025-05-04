from tavily import TavilyClient
from langchain_core.tools import tool
from typing import List, Dict
from pathlib import Path
import json


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
with open(f'{REPO_ROOT}/context/integration_actions.json', 'r') as f:
    INTEGRATION_ACTIONS = sorted(json.load(f), key = lambda x: x['integration'])
    for action in INTEGRATION_ACTIONS:
        action["inputs_schema"] = [field for field in action["inputs_schema"] if field["interface"] != "integration"]
TAVILY = TavilyClient()


@tool
def get_action_details(integration: str, action: str) -> Dict:
    """
    Given an integration name and action, returns details on the action execution, input schema,
        and links to relevant 3rd party API documentation
    """
    return [
        ia for ia in INTEGRATION_ACTIONS if ia['integration'] == integration and ia['action'] == action
    ][0]


@tool
def tavily_extract(url: str) -> str:
    """
    Given the supplied URL, extracts all text
    """
    return TAVILY.extract(url)['results'][0]['raw_content']


@tool
def tavily_search(query: str) -> List[Dict]:
    """
    Given a plain text query, runs an internet search
    """
    return TAVILY.search(query)['results']
