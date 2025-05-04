from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langfuse.decorators import observe, langfuse_context
from airops.utils import get_available_integration_actions
from airops import prompts, models
from airops.tools import get_action_details, tavily_extract, tavily_search
from pydantic import BaseModel
from typing import Any, List, Type, Dict


MODEL = 'gpt-4.1'


def make_agent(
        tools: List[BaseTool], prompt_template: str, output_model: Type[BaseModel], llm: str = MODEL
) -> Runnable:
    """
    Create an agent runnable.
    """
    parser = PydanticOutputParser(pydantic_object=output_model)
    partial_variables = {"format_instructions": parser.get_format_instructions()}
    agent_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "you are a helpful AI assistant"),
            ("human", prompt_template),
            ("placeholder", "{agent_scratchpad}")
        ]
    ).partial(**partial_variables)
    model = ChatOpenAI(model=llm, temperature=0)
    agent = create_tool_calling_agent(llm=model, tools=tools, prompt=agent_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, max_iterations=10)
    return agent_executor | RunnableLambda(lambda x: x["output"]) | parser


def create_integration_action_agent() -> Runnable:
    """
    Create an integration action agent.
    """
    return make_agent(
        tools = [get_action_details, tavily_search, tavily_extract],
        prompt_template = prompts.CREATE_INTEGRATION_ACTION_PROMPT,
        output_model = models.AgentOutput,
    )


@observe()
def run_integration_action_agent(workflow_context: Dict[str, Any], user_request: str) -> Dict[str, Any]:
    """
    Run an integration action agent on supplied inputs

    Args:
        workflow_context (Dict[str, Any]): workflow outputs at time of user request
        user_request (str): user request
    """
    integration_action_agent = create_integration_action_agent()
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    result = integration_action_agent.invoke({
        'available_integration_actions': get_available_integration_actions(),
        'workflow_context': workflow_context, 'user_request': user_request
    }, config={'callbacks': [langfuse_handler]})
    return {**result.model_dump(), 'langfuse_trace_id': langfuse_handler.trace.id}


def create_test_case_agent() -> Runnable:
    """
    Creates the agent that writes test cases (used in evaluation module)
    """
    return make_agent(
        tools = [get_action_details, tavily_search, tavily_extract],
        prompt_template = prompts.CREATE_TEST_CASE_PROMPT,
        output_model = models.TestCase,
        llm='gpt-4.1-mini' # we care less about fidelity here and this is much faster
    )
