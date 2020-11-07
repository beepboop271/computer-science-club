def convert_types(*types):
    def decorator(fun):
        def wrapper(*args):
            converted = []
            for i in range(len(args)):
                # call the corresponding type function on each arg
                converted.append(types[i](args[i]))
            # instead of using fun(*args), replace the args with
            # our converted arg list
            return fun(*converted)
        return wrapper
    return decorator


# it is also possible to replace:
#
# converted = []
# for i in range(len(args)):
#     converted.append(types[i](args[i]))
#
# by using a generator comprehension with:
#
# converted = tuple(types[i](args[i]) for i in range(len(args)))
#
# or a list comprehension with:
#
# converted = [types[i](args[i]) for i in range(len(args))]


# int, float, and bool are functions
@convert_types(int, int, float, bool)
def fun(x, y, z, flag):
    if flag:
        return pow(x+y, int(z), 1000)
    return (x+y)**z


print(fun(1, 2, 3, 4))
print(fun("1", 5.8, "5.9", 1))
