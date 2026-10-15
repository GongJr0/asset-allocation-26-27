# Setting up the environment

## Dependency manager

The repository and dependencies are managed with `uv`, a python environment manager. There are multiple ways to get it working in your computers.

**You already have Python and `pip`:**
```bash
pip install pipx
pipx install uv # uv should now be accessible
```

**You don't have Python available:**

```bash
# Linux and macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS only with homebrew (recommended for macOS if you have homebrew installed)
brew install uv
```

```powershell
# Windows with winget (recommended)
winget install -e --id astral-sh.uv

# Windows with an install script
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## How to use the environment

After installing `uv`, packages already added to the environment and pushed to the repository (by anyone) can be installed with a single command:

```bash
uv sync
```

Adding/removing a package to the environment is as simple as:

```bash
uv add <package-name>
uv remove <package-name>
```

## Setting up jupyter notebooks

The dependencies needed for jupyter notebooks are already in the environment.
A notebook can be edited and executed with an editor like VSCode, or via a jupyter server in the web browser.

Before running a notebook, you need to install a kernel, you can run the following commands once and the kernel will be available both in an editor and in a jupyter server:

```bash
uv sync
uv run python -m ipykernel install --user --name "asset-allocation" --display-name "Asset Alloca
tion"
```

If you're planning to use a web browser to edit, use:

```bash
uv run jupyter notebook
```

This will start a server and open a new tab in your browser. To stop the server, go to the terminal you typed the command and press `Ctrl+C` (alternatively close the terminal window). For VSCode, you can install the [Python](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-extension-pack) and [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) extension packs through the extension marketplace and edit notebooks in the editor.


## Check if you set up the environment correctly

After the following steps, you can use the test notebook and python script to verify that the environment is set up correctly.

```bash
# Test if the environmnt is reachable to run python scripts
uv run test_environment.py
```
If the following command does not work at all, you should check the uv installation steps. If it works but tells you that you're not in the correct environment, you can try again after running:

```bask
# linux and macOS
source .venv/bin/activate
```

```powershell
# Windows
.venv\Scripts\activate.ps1
```

This will force `uv` (and your terminal) to use the environment in this repository.


## Optional: Add yourself as an author

Open the `pyproject.toml` file and find the `authors` field under the `[project]` section. You can add your information to that list like:

```toml
authors = [
    {name = "Some Name", email = "<some-email>@student.uw.edu.pl"},
    { ... }, # add yourself here
]
```
