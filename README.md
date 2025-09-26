# Setup Local PC (First Time)



# Setup Server (First Time)
- SSH login to the server:
  ```sh
  ssh bot-250
  ```
- Install `uv` for `python` management:
  ```sh
  command -v uv >/dev/null && echo "uv already installed!" || { curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc; }
  ```
  <!-- or
  ```sh
  command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc; }
  ``` -->

# Setup Server (New Semester)
- Create folder (say `fall25`), enter it, `git clone` repo and skip updates for `info.toml`:
  ```sh
  mkdir fall25 && cd $_ && git clone https://github.com/shs-cse/uv-hikari-bot.git . && git update-index --skip-worktree info.toml
  ```
- If `credentials` in a different folder already exists (may be last semester), copy over to the new folder.
  ```sh
  cp ../creds-folder/*.json ./
  ```

# Setup Bot
- Invite bot to server
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