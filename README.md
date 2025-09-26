# Setup Local PC (First Time)



# Setup Server (First Time)
- SSH login to the server:
  ```sh
  ssh bot-250
  ```
- Install `uv` for `python` management:
  ```sh
  curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc
  ```
  <!-- or
  ```sh
  command -v uv >/dev/null || { curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc; }
  ``` -->

# Setup Server (New Semester)
- Create and enter folder: