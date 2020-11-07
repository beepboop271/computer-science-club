import random


def randomly_buffer(return_chance):
    values = []

    def decorator(fun):
        def wrapper(*args, **kwargs):
            values.append(fun(*args, **kwargs))
            if random.random() < return_chance:
                # need to make a copy because we need to clear the
                # list after returning to start buffering new elements
                ret = list(values)
                # cannot do values = [] because that would create
                # a new local variable which shadows the outer one
                values.clear()
                return ret
            return None
        return wrapper
    return decorator


@randomly_buffer(0.4)
def fun(x, y):
    return x*y


for _ in range(20):
    print(fun(random.randint(1, 10), random.randint(1, 10)))
