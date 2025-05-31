def get_nested_value(data_dict, path, default=None):
    """
    Retrieves a value from a nested dictionary or list structure using a dot-separated path.

    Args:
        data_dict (dict): The dictionary to traverse.
        path (str): A dot-separated path to the desired value (e.g., "user.name.first").
                    Can also include list indices (e.g., "items.0.name").
        default: The value to return if the path is not found or an error occurs.
                 Defaults to None.

    Returns:
        The value at the specified path, or the default value.
    """
    if not isinstance(data_dict, dict):
        return default

    keys = path.split('.')
    val = data_dict
    for key in keys:
        if isinstance(val, dict):
            val = val.get(key) # Using .get() which defaults to None if key is missing
        elif isinstance(val, list):
            try:
                idx = int(key)
                if 0 <= idx < len(val):
                    val = val[idx]
                else: # Index out of bounds
                    return default
            except ValueError: # Key is not a valid integer for list index
                return default
        else: # Current val is not a dict or list, so cannot traverse further
            return default

        if val is None: # If at any point we get None, and default is None, we can stop.
                        # If default is something else, we continue until the end to return that specific default.
            if default is None:
                return None # Return None early if that's the default
            # If default is not None, we might still want to continue if a later part of path exists
            # on a non-None default. But for typical API responses, this early exit is fine.
            # However, to strictly return default only at the end:
            # just let it continue, and if it fails, the final 'else' or end of loop returns default.
            # For now, if val becomes None, we stop and return default.
            return default

    return val if val is not None else default
