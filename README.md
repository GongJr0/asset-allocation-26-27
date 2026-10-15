# Setting up the environment

## Git and GitHub

Having a GitHub account is required but not enough to make sure you can keep a up-to-date copy of the repository on you computer.
You Git as well, however, there's a good chance you already have it. 
Run following command in your terminal to check:

```bash
# If you're on macOS, this command will also install git if you don't have it yet
git --version
```
If you see a version number, you can skip the next step.
If not, you can install Git by following the instructions on the [official website](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

### How to use git and GitHub

There are many guides around interacting with Git; here, we will focus on the simplest option for people not faimilar with the command line.
You can download and install the [GitHub Desktop](https://desktop.github.com/) application.
This application will let you copy the repository to your system and keep it up to date with a few clicks.
Log in with your GitHub account and clone the repository to your computer following the [official instructions](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-a-repository-from-github-to-github-desktop).

 - **Confirming you're up to date:** After cloning the repository, you can now access changes made by others, as well as pushing your own changes to the repository.
The app will often notify you when there are changes made to the repository and you don't have the latest version. 
The right corner of the top bar will show a "Fetch origin" button, that button will confirm you're looking at the latest version of the repository.

- **Syncing changes:** When it says "Pull origin" instead, it means there are changes made by others that you don't have yet. Click the button to get the latest version of the repository.

- **Making changes:** After you changed some files and committed them (follow [this guide](https://docs.github.com/en/desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project-in-github-desktop) to learn how to make commits with the app), the button will say "Push origin" instead. When you click it, your changes will be uploaded to the repository and everyone will have access to them.

There are more to learn and more advanced features, but there's no need to go beyond this for our purposes. 

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

### Navigating to the repository folder

You now have access to `uv`, to use it in your terminal, you first need to navigate to the repository folder.
This can be done with the `cd` (`c`hange `d`irectory) and `ls` (`l`i`s`t) commands.
`ls` will list the available files and folders inside the current folder, and `cd path/to/folder` will change the terminal's working directory to the specified folder.
For VSCode users, the GitHub desktop app will let you open the repository in VSCode, any terminal opened in VSCode afterwards will already be in the correct folder.

### Activating the environment

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
