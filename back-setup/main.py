import os
import traceback

if __name__ == "__main__":
    from colorama import Fore, init

    try:
        from model.config import ConfigModel
        import yaml

        init()

        CONFIG_FILE_PATH = "../config/config.yml"

        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            config_content = yaml.safe_load(f)

        config = ConfigModel(**config_content)
        print(Fore.GREEN + "[-- DONE --] Configuration validated successfully.")

        env_file_content = f"""#!/bin/bash

export FRONTEND_PORT={config.front.port}
export NEXT_PUBLIC_BACKEND_PORT={config.back.port}
    """
        os.makedirs("../var", mode=0o777, exist_ok=True)
        with open("../var/env.sh", "w") as g:
            g.write(env_file_content)

        os.chmod("../var/env.sh", mode=0o777)

        print(Fore.GREEN + "[-- DONE --] Created startup env successfully.")

    except Exception as e:
        traceback.print_exc()
        print(Fore.RED + f"[-- FAIL --] Fail to validate configuration: {e}")
        exit(1)
