import os

from core_utils import (
    load_environment_variables,
)

load_environment_variables()
try:
    if not os.getenv("DEVELOPER"):
        print("patching...")
        from aws_xray_sdk.core import patch_all

        patch_all()
except Exception as e:
    print(str(e))
