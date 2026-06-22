import argparse
import json
import sys

from pathlib import Path
from typing import Any
from pydantic import BaseModel

from moon_claude.core.bus import PingCommand, PongResult, CoreStartedEvent


# 定义默认输出路径
_OUTPUT_PATH = Path(__file__).parent.parent / "WIRE_PROTOCOL.md"


# 从 pydantic 模型生成一个带字段表、JSON Schema 和可选示例的 Markdown 小节
def _model_section(name: str, model: type, example: dict | None = None):
    schema = model.model_json_schema()  # type: ignore
    props = schema.get("properties", {})
    required: set[str] = set(schema.get("required", []))

    table = ""
    if props:
        table = "\n| Field | Type | Required |\n|---|---|---|\n"
        for field_name, field_info in props.items():
            ftype = field_info.get("type", "object")
            if "anyOf" in field_info:
                ftype = " | ".join(t.get("type", "?") for t in field_info["anyOf"])
            req = "yes" if field_name in required else "no"
            table += f"| `{field_name}` | `{ftype}` | {req} |\n"

    schema_block = f"\n```json\n{json.dumps(schema, indent=2)}\n```\n"

    example_block = ""
    if example:
        example_block = f"\n**Example:**\n\n```json\n{json.dumps(example, indent=2)}\n```\n"

    return f"### {name}\n{table}{schema_block}{example_block}"