def read_yaml(filename: str):
    """
    Read a YAML configuration file.

    @param filename: the name of the file to be read within the config directory.

    Returns: A dictionary of the YAML file's contents.
    """
    import yaml

    contents = None
    with open(filename, 'r') as f:
        contents = yaml.safe_load(f)

    return contents
        
