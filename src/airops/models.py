from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


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
        values should be one of the following:
        * liquid references to workflow inputs or step outputs (e.g. {{step_1.output}} or {{step_1.output.attribute}})
        * values that are explicitly given by the user in the prompt (e.g. "send an email to person@example.com")
        * if a field has finite set of options (like a boolean), or has a default value, and it is clear which one to apply, you can chose that value
        * if a required field cannot be populated in one of these ways, use {{value_missing}}
        NOTE: if a value exists as part of a workflow input or step output, you MUST provide the liquid reference, and NOT the literal value.
    """)


class TestCase(BaseModel):
    action_applicable: bool = Field(..., description="whether the integration action makes sense/can be configured wth the given workflow output")
    user_request: Optional[str] = Field(None, description="the synthetic user request that should trigger the integration action")
    action_config: Dict[str, Any] = Field(..., description="""
        the inputs to supply the integration action.
        keys should match the inputs schema for the integration action.
        values should be one of the following:
        * liquid references to workflow inputs or step outputs (e.g. {{step_1.output}} or {{step_1.output.attribute}})
        * values that are explicitly given by the user in the prompt (e.g. "send an email to person@example.com")
        * if a field has finite set of options (like a boolean), or has a default value, and it is clear which one to apply, you can chose that value
        * if a required field cannot be populated in one of these ways, use {{value_missing}}
        NOTE: if a value exists as part of a workflow input or step output, you MUST provide the liquid reference, and NOT the literal value.
    """)
