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

Now you should be set to run the scripts and notebooks for the solution!

## Using the Agent
You can call the agent using the `run_agent.ipynb` notebook.
Just supply your user request and context workflow and call the `run_integration_action_agent` function.

## Agent Evaluation
The `evaluation.py` module contains a script that runs the agent over a set of test cases and evaluates its performance using a variety of metrics.
