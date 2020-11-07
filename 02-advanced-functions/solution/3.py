import time


def cache(fun):
    arg_cache = {}

    def wrapper(*args):
        cached = arg_cache.get(args)
        if cached is None:
            print("cache miss!")
            result = fun(*args)
            arg_cache[args] = result
            return result
        print("cache hit!")
        return cached
    return wrapper


@cache
def fun(x, y):
    time.sleep(x)
    return x*y


print(fun(2, 5))
print(fun(1, 7))
print(fun(3, 2))
print(fun(2, 5))
print(fun(1, 1))
print(fun(1, 7))
