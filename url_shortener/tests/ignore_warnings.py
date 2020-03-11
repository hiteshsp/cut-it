import warnings

def ignore_warnings(test_method):
    def do_pass(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_method(self, *args, **kwargs)
    return do_pass