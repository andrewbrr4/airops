import os, time, joblib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from langfuse.decorators import observe, langfuse_context
from openai import RateLimitError
from airops import utils
from airops.agents import create_test_case_agent
from typing import Dict, Any, Union, List


REPO_ROOT = utils.get_repo_root()
TEST_CASES_FP = f'{REPO_ROOT}/eval/test_cases.joblib'


@observe()
def create_test_case(
        integration_action: Dict[str, str], sample_context: Dict[str, Any]
) -> Union[Dict[str, Any], None]:
    """
    Creates a single test case from a workflow context and desired integration action.
    A test case here is a synthetic user request on a given workflow context,
        that is meant to point to a given integration action
    """
    try:
        test_case_agent = create_test_case_agent()
        langfuse_handler = langfuse_context.get_current_langchain_handler()
        results = test_case_agent.invoke({
            "workflow_context": sample_context,
            "integration": integration_action["integration"],
            "action": integration_action["action"],
        }, config={"callbacks": [langfuse_handler]})
        return {**integration_action, 'context': sample_context, **results.model_dump()}
    except RateLimitError:
        time.sleep(60)
        return create_test_case(integration_action, sample_context)
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


def evaluate_agent():
    test_cases = create_test_cases(TEST_CASES_FP)
    for tc in test_cases:
        ...


if __name__ == '__main__':
    evaluate_agent()
