# Setup Local PC (First Time)



# Setup Droplet (First Time)
- SSH login to the server:
    ```sh
    ssh bot-250
    ```
- Install `uv` for `python` management (one line command):
    ```sh
    command -v uv >/dev/null && echo "uv already installed!" || { curl -LsSf https://astral.sh/uv/install.sh | sh && grep -q "alias uvo=" ~/.bashrc || echo "alias uvo='PYTHONOPTIMIZE=2 uv'" >> ~/.bashrc; source ~/.bashrc; }
    ```
    <!-- or
    ```sh
    command -v uv >/dev/null && echo "uv already installed!" || { curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc; }
    ```-->
    <!-- or
    ```sh
    command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc; }
    ``` -->

# Discord Server (New Semester)
- Create a new discord server from the following template:
    ```
    https://discord.new/pQ2GPFUGSjTB
    ```

# Setup Droplet (New Semester)
- Create folder (say `fall25`), enter it, `git clone` repo and skip updates for `info.toml`:
    ```sh
    mkdir fall25 && cd $_ && git clone https://github.com/shs-cse/uv-hikari-bot.git . && git update-index --skip-worktree info.toml
    ```
- If `credentials` in a different folder already exists (may be last semester), copy over to the new folder.
    ```sh
    cp ../creds-folder/*.json ./
    ```
- Run bot
    ```sh
    uvo run main.py
    ```
    - Equivalent to `uv run python -OO main.py`

# Setup Bot
- Invite bot to server (installation link looks like this):
    `
    https://discord.com/oauth2/authorize?client_id=...
    `
- Give [`@bot`](.) role to the bot

# Dev Notes
## How to update [`info.toml`](./info.toml) file pattern in `git`
- Don't track changes in the file:
    ```bash
    git update-index --skip-worktree info.toml
    ```
- Track changes in the file again:
    ```bash
    git update-index --no-skip-worktree info.toml
    ```
## Python debugging
- Run in debug mode with no optimization level:
    ```sh
    uv run main.py
    ```
- Add breakpoints in code:
    ```py
    if __debug__: breakpoint()
    ```