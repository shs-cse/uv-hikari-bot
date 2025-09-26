import miru, tomlkit
import pandas as pd

miru_client: miru.Client | None = None
is_debug: bool = False
info: tomlkit.TOMLDocument = {}

students: pd.DataFrame = pd.DataFrame()