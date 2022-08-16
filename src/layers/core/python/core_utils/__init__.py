# -*- coding: utf-8 -*-
import os


def load_environment_variables():
    try:
        from dotenv import load_dotenv
    except ImportError:
        pass
    else:
        if os.getenv("DEVELOPER") == "DeployUnittest":
            load_dotenv("./.env", override=False)
        load_dotenv()


load_environment_variables()
