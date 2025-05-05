import os, joblib
from tqdm import tqdm
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from langfuse.decorators import observe, langfuse_context
from airops import utils
from airops.agents import (
    run_integration_action_agent,
    create_test_case_agent,
    create_validate_output_agent
)
from typing import Dict, Any, Union, List
from langfuse import Langfuse


LANGFUSE = Langfuse()
METRICS = ['action_choice_score', 'config_completeness_score',
    'config_input_schema_score', 'config_input_values_score', 'exposition_score']


@observe()
@utils.handle_errors(3, 60)
def create_test_case(
        integration_action: Dict[str, str], workflow_context: Dict[str, Any]
) -> Union[Dict[str, Any], None]:
    """
    Creates a single test case from a workflow context and desired integration action.
    A test case here is a synthetic user request on a given workflow context,
        that is meant to point to a given integration action
    """
    test_case_agent = create_test_case_agent()
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    result = test_case_agent.invoke({
        "workflow_context": workflow_context,
        "integration": integration_action["integration"],
        "action": integration_action["action"],
    }, config={"callbacks": [langfuse_handler]}).model_dump()
    return {
        'workflow_context': workflow_context, 'user_request': result['user_request'],
        'expected_result': {**integration_action, 'action_config': result['action_config']},
        'action_applicable': result['action_applicable']
    }


def create_test_cases(target_fp: str) -> List[Dict[str, Any]]:
    """
    Given all sample workflow context and available integrations, create a suite of test cases

    Args:
        target_fp (str): Path to the where we store the test cases
    """
    if os.path.exists(target_fp):
        return joblib.load(target_fp)
    test_cases = []
    for action in tqdm(utils.get_available_integration_actions(), desc="create test cases"):
        futures = []
        with ThreadPoolExecutor() as executor:
            for sample in utils.get_sample_workflow_contexts():
                futures.append(executor.submit(create_test_case, action, sample))
            for f in as_completed(futures):
                result = f.result()
                if result is not None and result.pop('action_applicable'):
                    test_cases.append(result)
    joblib.dump(test_cases, target_fp)
    return test_cases


@observe()
def run_validate_output_agent(
        workflow_context: Dict[str, Any], user_request: str, agent_output: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Uses an agent to validate that the action config from a test case result is well-structured
    """
    validation_agent = create_validate_output_agent()
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    return validation_agent.invoke({
        'workflow_context': workflow_context, 'user_request': user_request, 'agent_output': agent_output
    }, config={"callbacks": [langfuse_handler]}).model_dump()


def calculate_completeness(config: Dict[str, Any]) -> float:
    """
    Counts the percentage of missing values in the given config
    """
    def recurse(d):
        count = 0
        total = 0
        for value in d.values():
            if isinstance(value, dict):
                nested_count, nested_total = recurse(value)
                count += nested_count
                total += nested_total
            else:
                total += 1
                if 'value_missing' in value:
                    count += 1
        return count, total
    count, total = recurse(config)
    pct_missing = (count / total) if total > 0 else 0
    return 1 - pct_missing


@utils.handle_errors(3, 60)
def run_and_score_test_case(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates test case results using various metrics
    """
    expected = test_case['expected_result']
    agent_result = run_integration_action_agent(test_case['workflow_context'], test_case['user_request'])
    validation_agent_result = run_validate_output_agent(
        test_case['workflow_context'], test_case['user_request'], agent_result)
    scores = {
        'action_choice_score': int(
            expected['action'] == agent_result['integration_action']['action']
            and expected['integration'] == agent_result['integration_action']['integration']
        ),
        'config_completeness_score': calculate_completeness(agent_result['action_config']),
    }
    for metric in METRICS:
        scores[metric] = validation_agent_result[metric]['score']
        scores[f'{metric}_reason'] = validation_agent_result[metric]['reason']
    for key, val in scores.items():
        LANGFUSE.score(trace_id=agent_result['langfuse_trace_id'], name=key, value=val)
    return {**test_case, 'agent_result': agent_result, **scores}


def evaluate_agent():
    """
    Creates test cases, runs the agent against each test case and evaluate the results,
        adding scores to the langfuse traces and dumping final results to local file
    """
    repo_root = utils.get_repo_root()
    test_cases = create_test_cases(f'{repo_root}/eval/test_cases.joblib')

    scored_test_cases = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_and_score_test_case, tc) for tc in test_cases]
        for future in tqdm(as_completed(futures), total=len(futures), desc="run and score test cases"):
            result = future.result()
            if result is not None:
                scored_test_cases.append(result)

    test_results = {'scored_test_cases': scored_test_cases}
    for metric in METRICS:
        test_results[f'avg_{metric}'] = sum([tc[metric] for tc in scored_test_cases]) / len(scored_test_cases)

    joblib.dump(test_results,
        filename=f'{repo_root}/eval/results/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.joblib')
    return test_results
