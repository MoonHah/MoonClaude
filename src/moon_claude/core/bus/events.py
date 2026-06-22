from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator


class CoreStartedEvent(BaseModel):
    type: Literal["core.started"] = "core.started"
    listen_addr: str
    version: str


# 根据 type 字段决定事件类型的判别联合
Event = Annotated[CoreStartedEvent, Discriminator("type")]
