# 使用skopeo --config获取的镜像简单配置，并不是umoci unpack后的完整config.json
from __future__ import annotations
from typing import List, Optional, TypedDict
from datetime import datetime

class Config(TypedDict):
    Env: List[str]
    Entrypoint: List[str]
    Volumes: List[str]
    WorkingDir: str
    Labels: dict[str, str]

class Rootfs(TypedDict):
    type: str
    diff_ids: List[str]

class History(TypedDict):
    created: datetime
    created_by: str
    comment: str
    empty_layer: Optional[bool]

class OCIShallowConfig(TypedDict):
    created: datetime
    architecture: str
    os: str
    config: Config
    rootfs: Rootfs
    history: List[History]
