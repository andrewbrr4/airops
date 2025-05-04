import os, time, joblib
from tqdm import tqdm
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from langfuse.decorators import observe, langfuse_context
from openai import RateLimitError
from airops import utils
from airops.agents import (
    run_integration_action_agent,
    create_test_case_agent,
    create_validate_output_agent
)
from typing import Dict, Any, Union, List
from langfuse import Langfuse


REPO_ROOT = utils.get_repo_root()
LANGFUSE = Langfuse()


@observe()
def create_test_case(
        integration_action: Dict[str, str], workflow_context: Dict[str, Any]
) -> Union[Dict[str, Any], None]:
    """
    Creates a single test case from a workflow context and desired integration action.
    A test case here is a synthetic user request on a given workflow context,
        that is meant to point to a given integration action
    """
    try:
        test_case_agent = create_test_case_agent()
        langfuse_handler = langfuse_context.get_current_langchain_handler()
        result = test_case_agent.invoke({
            "workflow_context": workflow_context,
            "integration": integration_action["integration"],
            "action": integration_action["action"],
        }, config={"callbacks": [langfuse_handler]}).model_dump()
        return {
            'workflow_context': workflow_context,
            'user_request': result['user_request'],
            'expected_result': {**integration_action, 'action_config': result['action_config']},
        }
    except RateLimitError:
        time.sleep(60)
        return create_test_case(integration_action, workflow_context)
    except Exception as e:
        print(f'Error: {e}')
        return None


def create_test_cases(target_fp: str) -> List[Dict[str, Any]]:
    """
    Given all sample workflow context and available integrations, create a suite of test cases

    Args:
        target_fp (str): Path to the where we store the test cases
    """
    if os.path.exists(target_fp):
        return joblib.load(target_fp)
    test_cases = []
    for action in tqdm(utils.get_available_integration_actions(), desc="Actions"):
        futures = []
        with ThreadPoolExecutor() as executor:
            for sample in utils.get_sample_workflow_contexts():
                futures.append(executor.submit(create_test_case, action, sample))
            for f in as_completed(futures):
                result = f.result()
                if result is not None and result['action_applicable']:
                    test_cases.append(result)
    joblib.dump(test_cases, target_fp)
    return test_cases


@observe()
def run_validate_output_agent(user_request: str, agent_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses an agent to validate that the action config from a test case result is well-structured
    """
    validation_agent = create_validate_output_agent()
    langfuse_handler = langfuse_context.get_current_langchain_handler()
    return validation_agent.invoke({
        'user_request': user_request, 'agent_output': agent_output
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
                if value == "{value_missing}":
                    count += 1
        return count, total
    count, total = recurse(config)
    return (count / total) if total > 0 else 0


def score_test_case_result(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates test case results using various metrics
    """
    expected = test_case['expected_result']
    agent_result = test_case['agent_run_result']
    validation_agent_result = run_validate_output_agent(test_case['user_request'], agent_result)
    scores = {
        'action_choice_score': int(
            expected['action'] == agent_result['action'] and expected['integration'] == agent_result['integration']),
        'config_completeness_score': calculate_completeness(agent_result['action_config']),
        'config_accuracy_score': validation_agent_result['config_accuracy_score']['value'],
        'config_accuracy_score_reason': validation_agent_result['config_accuracy_score']['reason'],
        'exposition_score': validation_agent_result['exposition_score']['value'],
        'exposition_score_reason': validation_agent_result['exposition_score']['reason'],
    }
    for key, val in scores.items():
        LANGFUSE.score(trace_id=agent_result['langfuse_trace_id'], name=key, value=val)
    return {**test_case, **scores}


def evaluate_agent():
    """
    Creates test cases, runs the agent against each test case and evaluate the results,
        adding scores to the langfuse traces and dumping final results to local file
    """
    test_cases = create_test_cases(f'{REPO_ROOT}/eval/test_cases.joblib')
    scored_test_cases = []
    for tc in tqdm(test_cases):
        tc['agent_run_result'] = run_integration_action_agent(tc['context'], tc['user_request'])
        scored_test_cases.append(score_test_case_result(tc))

    test_results = {'scored_test_cases': scored_test_cases}
    for metric in ['action_choice_score', 'config_completeness_score', 'config_accuracy_score', 'exposition_score']:
        test_results[f'avg_{metric}'] = sum([tc[metric] for tc in scored_test_cases]) / len(scored_test_cases)

    joblib.dump(
        test_results,
        f'{REPO_ROOT}/eval/results/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.joblib'
    )


if __name__ == '__main__':
    evaluate_agent()
