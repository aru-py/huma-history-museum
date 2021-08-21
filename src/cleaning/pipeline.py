"""
pipeline.py

Small library to be used for performing
complex manipulations on deeply nested
data.

"""

import random
from functools import partial
import json


class Pipeline:

    def __init__(self,
                 func=None,
                 key=None,
                 name=None,
                 throw=None,
                 seq_dump=None):

        self.pipe = {}

        if func:
            # wrap function with pipeline
            self.__name__ = func.__name__
            self.pipe[self.__name__] = func
        else:
            # if name not provided, use a random name
            self.__name__ = name if name else str(random.randint(1000, 9999))


        self.key = key
        self.loss = {}
        self.seq_dump = seq_dump
        self.is_func = func

        if throw is None:
            throw = []
        self.throw = throw

    def __getitem__(self, key):
        if key not in self.pipe:
            raise KeyError
        return self.pipe[key]

    def __setitem__(self, key, pipe, **kwargs):

        if not isinstance(pipe, Pipeline):
            raise Exception

        self.pipe[key] = pipe
        pipe.__name__ = key

    def __call__(self, objs):

        if not isinstance(objs, list):
            if self.is_func:
                return self.is_func(objs)
            raise RuntimeError

        self.loss[self.__name__] = len(objs)
        pipe_no = 0
        for k, f in self.pipe.items():
            for i in range(len(objs)):
                try:
                    if hasattr(f, 'key') and f.key:
                        objs[i][f.key] = f(objs[i][f.key])
                    else:
                        objs[i] = f(objs[i])
                except Exception as e:
                    objs[i] = None
                    if self.throw:
                        print(e)

            objs = list(filter(None, objs))
            pipe_no += 1
            if self.seq_dump:
                with open(f'steps/{pipe_no}_{k[:14]}.json', 'w+') as j:
                    json.dump(objs, j)

            self.loss[k] = len(objs)
        return list(filter(None, objs))

    def __str__(self):
        return self.__name__

    def clear(self):
        self.pipe.clear()

    def add(self, func, **kwargs):
        pipe_func = Pipeline(func, **kwargs)
        self.pipe[str(pipe_func)] = pipe_func
        return func

    def add_to(self, pipe_key, **kwargs):
        if pipe_key not in self.pipe:
            self[pipe_key] = Pipeline(name=pipe_key)
        return partial(self[pipe_key].add, **kwargs)
