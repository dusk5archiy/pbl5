import os
import traceback

if __name__ == "__main__":
    from loguru import logger

    try:
        from model.config import ConfigModel
        import yaml

        CONFIG_FILE_PATH = "../config/config.yml"

        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            config_content = yaml.safe_load(f)

        config = ConfigModel(**config_content)
        logger.success("Configuration validated successfully.")

        env_file_content = f"""#!/bin/bash

export FRONTEND_PORT={config.front.port}
export BACKEND_PORT={config.back.port}
export AI_PORT={config.ai.port}
    """
        os.makedirs("../var", mode=0o777, exist_ok=True)
        with open("../var/env.sh", "w") as g:
            g.write(env_file_content)

        os.chmod("../var/env.sh", mode=0o777)

        logger.success("Created startup env successfully.")

    except Exception as e:
        logger.exception(f"ERROR: Fail to validate configuration: {e}")
        exit(1)
