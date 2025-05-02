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
        If you are unable to populate required values using the available keys from the worklow outputs object, you must either:
        * populate with you best guess of one of a KNOWN set of options.
        * indicate the user must supply this field to you by returning {{user_input}}
    """)


class TestCase(BaseModel):
    action_applicable: bool = Field(..., description="whether the integration action makes sense/can be configured wth the given workflow output")
    user_request: Optional[str] = Field(None, description="the synthetic user request that should trigger the integration action")
    action_config: Dict[str, Any] = Field(..., description="""
        the inputs to supply the integration action.
        keys should match the inputs schema for the integration action.
        values should be liquid references to workflow inputs or step outputs.
        If you are unable to populate required values using the available keys from the worklow outputs object, you must either:
        * populate with you best guess of one of a KNOWN set of options.
        * indicate the user must supply this field to you by returning {{user_input}}
    """)
