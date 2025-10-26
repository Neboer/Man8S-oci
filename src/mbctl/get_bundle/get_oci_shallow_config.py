import json
import subprocess
from typing import Any, Dict
from mbctl.config_formats import OCIShallowConfig

# 只获取OCI配置，不拉取容器。
def get_container_shallow_config(image: str) -> OCIShallowConfig:
    """
    Return the JSON config produced by:
      skopeo inspect --config docker://{image}
    """
    cmd = ["skopeo", "inspect", "--config", f"docker://{image}"]
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return json.loads(proc.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"skopeo inspect failed: {e.stderr.strip() or e}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"failed to parse skopeo output as JSON: {e}") from e
