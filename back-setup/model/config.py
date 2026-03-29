from pydantic import BaseModel, model_validator, field_validator


def check_port(port: int) -> None:
    assert isinstance(port, int)
    port_min = 1023
    port_max = 65535
    if not port_min <= port <= port_max:
        raise ValueError(f"Port must be between {port_min} and {port_max}.")


class ConfigModel(BaseModel):
    class ConfigModelBase(BaseModel):
        port: int

        @field_validator("port")
        def validate_port(cls, port: int) -> int:
            check_port(port)
            return port

    front: ConfigModelBase
    back: ConfigModelBase
    ai: ConfigModelBase

    @model_validator(mode="after")
    def validator(self) -> "ConfigModel":
        port_list = [self.front.port, self.back.port, self.ai.port]
        if len(set(port_list)) < len(port_list):
            raise ValueError("Duplicated ports.")
        return self


if __name__ == "__main__":
    pass
