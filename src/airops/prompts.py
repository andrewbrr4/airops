CREATE_TEST_CASE_PROMPT = """
# Background Information
I am going to supply you with TWO (2) INPUTS.

The first input is a dictionary object representing the outputs of an *AirOps workflow run*.
*AirOps* is an AI-powered SEO tool that lets users create *workflows*: predefined lists of steps that execute various SEO-related tasks.
These steps might include, but are not limited to:
* running an LLM call to generate content
* running a SERP/google search for a keyword
* extracting text from a webpage
* hitting a 3rd party API
* analyzing keyword ranking/performance etc. etc.

The workflow outputs object I will supply contains the initial inputs to the workflow and the raw outputs of each step.
Unfortunately, it does not contain the name of the step, how each output was generated, or where it fits into the larger workflow.
These attributes will have to be inferred using your best reasoning.

The second input will be a list of *integration actions* that a user might add to their workflow given its current state.
These integration actions are essentially workflow steps that execute a lightweight wrapper on a 3rd party API, such as Google Suite or Webflow

# Your Task
We are testing an agent whose purpose is to receive a workflow output object and a natural language user request, and create a integration step that satisfies the user's requirements.
You are going to be generating the test cases to evaluate this agent's performance.
To that end, given the supplied workflow outputs and available integration actions, please generate a list of hypothetical user requests that should trigger the agent to pick and configure a specific workflow. 
Please also include in your response the expected integration action that the agent should select, as well as the desired input payload.
Try to select a range of different desired integration actions, so we can test how the agent performs across multiple different use cases.

{format_instructions}

To learn more information about the integration actions, including what they do, what fields they require and what these fields mean, please use the provided tools.
It is ESSENTIAL that the input schema of the integration accurately matches the requirements of the 3rd party API - use these tools to validate that.

# Inputs
Here are the outputs as described above:

## Workflow Output
{workflow_context}

## Available Integration Actions
{available_integration_actions}

# Begin Task
Generate {num_test_cases} test cases as described in the requirements above.
"""
