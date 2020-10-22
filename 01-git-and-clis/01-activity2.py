import argparse
import os
import random
import time

if os.path.basename(os.getcwd()) != "01-git-and-clis":
    print("set your current directory to be inside this week's folder")

parser = argparse.ArgumentParser(description="tests your argument knowledge")
parser.add_argument(
    "-e", action="store_true",
    help="A flag argument which must be present, indicating a value of True"
)
parser.add_argument(
    "-f", action="store_true",
    help="A flag argument which must not be present"
)
parser.add_argument(
    "-g", action="store_true",
    help="A flag argument which must be present"
)
parser.add_argument(
    "string_arg", type=str,
    help="A string argument which must be equal to (without first space): Hel$lo'\", W\\orld!"
)
parser.add_argument(
    "numeric_arg", type=int,
    help="An integer argument which must be any even integer"
)
parser.add_argument(
    "relative_current_path", type=str,
    help="A string argument which must be the path to the file 01-activity1.py, using a relative path"
)
parser.add_argument(
    "relative_previous_path", type=str,
    help="A string argument which must be the path to the file outline.md, using a relative path"
)
parser.add_argument(
    "absolute_path", type=str,
    help="A string argument which must be any valid absolute file path"
)

args = parser.parse_args()


def check(valid_fn, arg, arg_name):
    if valid_fn(arg):
        print(f"your {arg_name} was correct")
        return
    print(f"your {arg_name} was wrong, received: {str(arg)}")
    exit(0)


check(
    lambda x: x,
    args.e, "flag (e)"
)
check(
    lambda x: not x,
    args.f, "flag (f)"
)
check(
    lambda x: x,
    args.g, "flag (g)"
)
check(
    lambda x: x == "Hel$lo'\", W\\orld!",
    args.string_arg, "string_arg"
)
check(
    lambda x: x % 2 == 0,
    args.numeric_arg, "numeric_arg"
)
check(
    lambda x: (
        os.path.isfile(x)
        and (not os.path.isabs(x))
        and (os.path.basename(x) == "01-activity1.py")
    ),
    args.relative_current_path, "relative_current_path"
)
check(
    lambda x: (
        os.path.isfile(x)
        and (not os.path.isabs(x))
        and (os.path.basename(x) == "outline.md")
    ),
    args.relative_previous_path, "relative_previous_path"
)
check(
    lambda x: os.path.isfile(x) and os.path.isabs(x),
    args.absolute_path, "absolute_path"
)

print("all arguments correct!")

time.sleep(1)

line = random.randint(3000, 7000)

alphabet = list("abcdefghijklmnopqrstuvwxyz")

for i in range(10000):
    if i == line:
        print("good job!", random.randint(100000, 999999))
    random.shuffle(alphabet)
    print("wow!", "".join(alphabet), random.randint(100000, 999999))
