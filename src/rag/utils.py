from typing import Dict, Any, TypeVar, Optional, Type, cast

T = TypeVar("T")


def get_config_value(
    config: Dict[str, Any],
    key: str,
    default_value: Optional[T] = None,
    required: bool = False,
    value_type: Optional[Type] = None,
) -> T:
    """
    Safely get a value from a configuration dictionary.

    Args:
        config: Configuration dictionary
        key: Key to look up in the dictionary
        default_value: Default value to return if key is not found
        required: Whether the key is required (raises ValueError if missing)
        value_type: Expected type of the value (raises TypeError if mismatch)

    Returns:
        The value from the configuration, or the default value

    Raises:
        ValueError: If the key is required but not found
        TypeError: If the value is not of the expected type
    """
    if key not in config:
        if required:
            raise ValueError(f"Required configuration key '{key}' not found")
        return cast(T, default_value)

    value = config[key]

    if (
        value_type is not None
        and value is not None
        and not isinstance(value, value_type)
    ):
        try:
            # Try to convert the value to the expected type
            value = value_type(value)
        except (ValueError, TypeError):
            raise TypeError(
                f"Configuration value for '{key}' must be of type {value_type.__name__}"
            )

    return cast(T, value)
