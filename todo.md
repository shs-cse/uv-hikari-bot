- Get rid of `st_sheet_id` and encorporate with enrolment sheet
- Faculty nickname update issue
- Change `guild` to server in toml files
- Section `0` as discord template instead of `1`
- `str(sec)` may cause issue `f"{sec:02d}"`
- check and keep updating state at the same time
- add `state.enrolment`

# Replace names at the very end
- Change all `FileName`s to `FilePath` variables
- Change `EEEGuild` to `FacultyGuild`
- Change `credentials.json` to `google_credentials.json`
- Change `InfoField` to `InfoKey`
- Change `InfoField.NUM_SECTIONS` to `InfoKey.LAST_SECTION`
- Change `update_cells_from_fields`
- Change `MarksSprdsht.Meta.CELL_TO_FILED_DICT`
- Change `info.toml > last_section` to `info.toml > last_theory_section`
- Change `info.toml > missing_sections` to `info.toml > missing_theory_sections`
- Change `EnrlmentSprdSht.Students.SECTION_COL` to `THEORY_SECTION_COL`
- Change `CELL_TO_FIELD_DICT` to `KEYS_AT_CELLS`
- Change `update_routine/student_list` in `sync/sheets` to `fetch_routine/student_list`

# Long tome change
- Change `ClassType` to `StrEnum`. But `ALL` poses an issue.
- Migrate to `gspread` and `gspread-pandas/dataframe` from `pygsheets`