from tavily import TavilyClient
from langchain_core.tools import tool


TAVILY = TavilyClient()


@tool
def tavily_search(query: str) -> List[Dict]:
    """
    Given a plain text query, runs an internet search
    """
    return TAVILY.search(query)['results']


@tool
def tavily_extract(url: str) -> str:
    """
    Given the supplied URL, extracts all text
    """
    response = TAVILY.extract(url)['results'][0]['raw_content']
