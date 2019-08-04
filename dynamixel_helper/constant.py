############################################
#              Verbosity
############################################

verbose_level = {'quiet': 0, 'minimal': 1, 'detailed': 2}


def assert_verbosity(verbosity):
    """Safety check for verbosity string.

    Args:
        verbosity: 'quiet' or 'minimal' or 'detailed'
    Raises:
        RuntimeError: If the verbosity string is not in verbose_level
    """
    if verbosity not in verbose_level:
        print("Helper: [ERROR]")
        print("        An undefined verbosity option has been detected.")
        print("        Supported options: {}".format(verbose_level.keys()))
        raise RuntimeError
