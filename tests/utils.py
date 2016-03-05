import argparse


def load_args(**kwargs):
    args = argparse.Namespace(
                data=None,
                file=None,
                interactive=False,
                language=None,
                proxy=None,
                request=None,
                search_regex=None,
                search_string=None
            )
    for key, value in kwargs.iteritems():
        setattr(args, key, value)

    return args
