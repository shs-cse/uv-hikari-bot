# Create Discord Bot/Application account (First Time)
- Different from your personal accounts. Go to Discord's dev portal and create a new application.
- Take note of the bot token (secret, but can be regenerated if leaked).
# Setup Local PC (First Time)
- Install GitBash if on windows
- ssh stuff. You may skip creating new username (just use root)
- For more details, go to https://github.com/shs-cse/discord-bot/


# Setup Droplet (First Time)
- SSH login to the server:
    ```sh
    ssh bot-250
    ```
- Install `uv` for `python` management (one line command):
    ```sh
    command -v uv >/dev/null && echo "uv already installed!" || curl -LsSf https://astral.sh/uv/install.sh | sh; grep -q "alias uvo=" ~/.bashrc || echo "alias uvo='PYTHONOPTIMIZE=2 uv'" >> ~/.bashrc; source ~/.bashrc
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
- Create folder (say `fall_25`), enter it, `git clone` repo and skip updates for `info.toml`:
    ```sh
    mkdir fall_25 && cd $_ && git clone https://github.com/shs-cse/uv-hikari-bot.git . && git update-index --skip-worktree info.toml
    ```
- If `credentials` in a different folder already exists (may be last semester), copy over to the new folder.
    ```sh
    cp ../creds-folder/*.json ./
    ```
- Use `tmux` to run the bot in a background window.
    ```sh
    tmux new -A
    ```
- Run the bot
    ```sh
    uvo run main.py
    ```
    - Equivalent to `uv run python -OO main.py`
- Detach (minimize) the tmux window by pressing <kbd>Ctrl</kbd>+<kbd>B</kbd> and then <kbd>D</kbd>.

# Add Bot to Discord (New Semester)
- Invite bot to server
    - Discord dev portal > Select bot/application > Installation
        - **Install link** > Select **"Discord Provided Link"**. Installation link looks like this: 
        ```
        https://discord.com/oauth2/authorize?client_id=.......
        ```
    - Give it proper **Scopes**: `application.commands`, `bot` 
    - Give it proper **Permissions**: `Administrator`, `Use Slash Command`
- Go to the installation link, and select which server the bot will be added to.
- After Bot has joined the server, give [`@bot`](.) role to the bot.

---

## Dev Notes
### Inspect Code output
- If your using `tmux` then, navigate using:
    - Either attach or new tmux session
        ```sh
        tmux new -A
        ```
    - <kbd>Ctrl</kbd>+<kbd>B</kbd> and then press: 
        - <kbd>[</kbd> to enter scroll mode (then navigate)
        - <kbd>Q</kbd> to exit scroll mode
        - <kbd>D</kbd> to detach tmux session
### Update [`info.toml`](./info.toml) file template in `git`
- Don't track changes in the file:
    ```sh
    git update-index --skip-worktree info.toml
    ```
- Track changes in the file again:
    ```sh
    git update-index --no-skip-worktree info.toml
    ```
- Ignore all current local chances and fetch the latest github code
    ```sh
    git fetch --all; git reset --hard origin/main
    ```
### Python debugging
- Run in debug mode with no optimization level:
    ```sh
    uv run main.py
    ```
- Add breakpoints in code:
    ```py
    if __debug__: breakpoint()
    ```