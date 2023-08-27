import argparse
import enum
from pathlib import Path


class EnumAction(argparse.Action):
    def __init__(self, **kwargs):
        # Pop off the type value
        enum_type = kwargs.pop("type", None)

        # Ensure an Enum subclass is provided
        if enum_type is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum_type, enum.Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        kwargs.setdefault("choices", tuple(e.name for e in enum_type))

        super(EnumAction, self).__init__(**kwargs)

        self._enum = enum_type

    def __call__(self, parser, namespace, values, option_string=None):
        # Convert value back into an Enum
        value = self._enum[values]
        setattr(namespace, self.dest, value)


class PathAction(argparse.Action):
    def __init__(self, **kwargs):
        self._require_kwarg(kwargs, "nargs", "?")
        self._require_kwarg(kwargs, "type", str)
        self._require_kwarg(kwargs, "const", "")
        super(PathAction, self).__init__(**kwargs)

    def _require_kwarg(self, kwargs, name, required_value):
        try:
            if kwargs[name] != required_value:
                raise ValueError(f"{name} should be set to {required_value} or left empty")
        except KeyError:
            kwargs[name] = required_value

    def __call__(self, parser, namespace, value, option_string=None):
        if not value:
            value = None
        else:
            value = Path(value)
            if not value.is_dir():
                raise FileNotFoundError("Selected root folder does not exist")
        setattr(namespace, self.dest, value)
