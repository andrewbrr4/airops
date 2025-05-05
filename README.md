# AirOps Agent Take-Home

This repo contains the completed solution to the [AirOps agent take-home assignment](https://airopshq.notion.site/Integration-Agent-Take-Home-Assessment-1c31f419db8a8046ae41e6722123811c#1c31f419db8a8046a87fe5f3cb849574)

## Environment Setup
* install [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) on your machine if you don't already have it
* create a new conda environment - use python 3.11 (some later versions cause dependency issues)
* activate your conda environment for the following steps 
* install python requirements:
  * install pip (`conda install pip`)
  * install requirements file (`pip install -r requirements.txt`)
  * install the repo python module (`pip install .`)
  * install jupyter to run notebooks (`conda install jupyter`)
  * create a jupyter kernel from your conda environment to run notebooks (`python -m ipykernel install --user --name={env_name}`)
* ensure the environment you are running in has the required API Keys as env variables:
  * OPENAI_API_KEY
  * TAVILY_API_KEY (you can sign up [here](https://tavily.com/), includes 1000 free searches/month)
  * Langfuse env vars for tracing:
    * you will need to [create a free account](https://cloud.langfuse.com/auth/sign-up), then contact the owner to be added to the project.
    * set LANGFUSE_HOST, LANGFUSE_PUBLIC and LANGFUSE_SECRET values
  * set the env variable MODEL_NAME to your chose OpenAI llm model

Now you should be set to run the scripts and notebooks for the solution!

## Using the Agent
You can call the agent using the `run_agent.ipynb` notebook.
Just supply your user request and context workflow and call the `run_integration_action_agent` function.

## Agent Evaluation
You can evaluate the agent's performance using the `evaluate_agent.ipynb` notebook.
When you call the `evaluate_agent` function it will execute the following steps:
* generate a set of test cases
* run the agent against each test case
* score the agent's output for each test case using a variety of metrics:
  * how well the agent's integration action choice matches the test case expectation
  * what percentage of required values the agent was able to fill out for the action config
  * a separate LLM-as-a-judge agent's evaluation of the output

These scores will be returned to you from the function and also dumped locally.
They will also be available with the Langfuse trace.

NOTE: by default, this function will test all possible action integrations across all 5 sample workflow contexts.
As such, it will take a while, and depending on your OpenAI organization plan, you may run into rate limiting or context window errors.
It is recommended you use a cheap or fast model (such as gpt-4.1-mini) for this purpose.

## Traceability
Once you make an account, contact the owner of this repo to be added to the project.
You will then be able to view traces and evaluation scores in the [web ui](https://us.cloud.langfuse.com/project/cmaaekmlb0047ad0762o0z5t8).