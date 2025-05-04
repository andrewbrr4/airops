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

The second input will be an example of an *integration action* that a user might add to their workflow given its current state.
Integration actions are essentially workflow steps that execute a lightweight wrapper on a 3rd party API, such as Google Suite or Webflow

# Your Task
We are testing an agent whose purpose is to receive a workflow output object and a natural language user request, and create an integration step that satisfies the user's requirements.
You are going to be generating the test cases to evaluate this agent's performance.
To that end, given the supplied workflow outputs and integration action, please generate a hypothetical user request that should trigger the agent to pick and configure that action step.
Please also include in your response a mock-up of the desired payload for the integration action.

Values for the mocked payload MUST be one of the following:
* liquid references to workflow inputs or step outputs (e.g. {{step_1.output}} or {{step_1.output.attribute}})
* values that are explicitly given by the user in the prompt (e.g. "send an email to person@example.com")
* if a field has finite set of options (e.g. a boolean field must be one of [True, False] or ['']), and the user's prompt makes it clear which one to apply, you can use that value
* if a required field cannot be populated in one of these ways, you can set the value to {{missing}}, indicating that it must be given by the user.

If there is no reasonable way that the integration action can be configured given the supplied workflow outputs and prompt, you can indicate this and return nulls for the action and payload fields in your response.

{format_instructions}

To learn more information about the integration actions, including what they do, what fields they require and what these fields mean, please use the provided tools.
These tools will help you understand if an integration action can be configured given the outputs available.
You MUST use these tools - at a bare minimum the `get_action_details` tool is mandatory - to ensure that your config is properly formatted.

# Inputs
Here are the outputs as described above:

## Workflow Output
{workflow_context}

## Integration Action
Integration: {integration}
Action: {action}

# Begin Task
Generate the test cases as described in the requirements above.

As a reminder, values for the action config payload MUST BE:
* liquid references to workflow inputs or step outputs (e.g. {{step_1.output}} or {{step_1.output.attribute}})
* values that are explicitly given by the user in the prompt (e.g. "send an email to person@example.com")
* if a field has finite set of options (e.g. a boolean field must be one of [True, False] or ['']), and the user's prompt makes it clear which one to apply, you can use that value
* if a required field cannot be populated in one of these ways, you can set the value to {{missing}}, indicating that it must be given by the user.
This formatting is key.
"""
