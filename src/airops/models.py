from pydantic import BaseModel, Field


class IntegrationAction(BaseModel):
    integration: str = Field(..., description="the 3rd party platform in which to take the action")
    action: str = Field(..., description="the action to take")

class IntegrationActionPayload(BaseModel):
    integration_action: IntegrationAction = Field(..., description="""
        which integration action is chosen. must be one of the known, pre-supplied options.
    """)
    action_config: Dict[str, Any] = Field(..., description="""
        the inputs to supply the integration action.
        keys should match the inputs schema for the integration action.
        values should be liquid values/references to workflow output steps (e.g. step_x.output.key) - NOT literal values.
    """)
