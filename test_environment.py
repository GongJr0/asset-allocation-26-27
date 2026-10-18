import sys
from pathlib import Path


def main():
    if ".venv" in sys.prefix:
        expected = (Path.cwd() / ".venv").resolve()
        actual = Path(sys.prefix).resolve()
        if expected == actual:
            print("The environment is correctly set up.")
        else:
            print(
                "You are running in a virtual environment, but it is not the correct one. "
                "Check the README and see if you missed anything."
            )
    else:
        print(
            "Your code ran, but you're not using a virtual environment."
            "Check the README and see if you missed anything."
        )


if __name__ == "__main__":
    main()
