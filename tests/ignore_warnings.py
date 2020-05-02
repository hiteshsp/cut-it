import warnings

def ignore_warnings(test_method):
    """
        Method to ignore warnings which are enabled by unittest
    """
    def do_pass(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_method(self, *args, **kwargs)
    return do_pass