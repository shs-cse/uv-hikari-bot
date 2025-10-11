# Immediate Todo
- ~~Faculty nickname update issue (need update cahce)~~
- ~~Change `guild` to server in toml files~~
- ~~Section `0` as discord template instead of `1`~~
- ~~`str(sec)` may cause issue `f"{sec:02d}"`~~
- ~~check and keep updating state at the same time~~
- ~~check and load st sheet~~
- ~~must fix `marks_groups`, may not be json complient~~
- ~~do something about `LAB_A/B` vs `LAB`. may be new toml key?~~
    - ~~current solution is debug dependent... `uv->LAB` & `uvo->LAB_A/B`~~
- ~~instead of `load_marks_section`, do `load_marks`~~
    - ~~use `update_marks` in the process?~~
    - ~~define `update_marks_section`~~
- ~~git add `[marks_buttons]` in `info.toml`~~
- ~~autocomplete fix~~
- add `state.enrolment`
- ~~long running operation loses ~40 sec heartbeat. consider `asyncio`~~

# Replace names at the very end
- ~~Change all `FileName`s to `FilePath` variables~~
- ~~Change `EEEGuild` to `FacultyGuild`~~
- ~~Change `credentials.json` to `google_credentials.json`~~
- ~~Change `InfoField` to `InfoKey`~~
- ~~Change `InfoField.NUM_SECTIONS` to `InfoKey.LAST_SECTION`~~
- ~~Change `update_cells_from_fields`~~
- ~~Change `MarksSprdsht.Meta.CELL_TO_FILED_DICT`~~
- Change `info.toml > last_section` to `info.toml > last_theory_section`
- Change `info.toml > missing_sections` to `info.toml > missing_theory_sections`
- ~~Change `EnrlmentSprdSht.Students.SECTION_COL` to `THEORY_SECTION_COL`~~
- ~~Change `CELL_TO_FIELD_DICT` to `KEYS_AT_CELLS_DICT`~~
- Change `update_routine/student_list` in `sync/sheets` to `fetch_routine/student_list`
- ~~Change `get_generic_error_response_while_verifying` to `get_generic_verification_error_response`~~
- ~~Change `CLASS_TYPE_FACULTY_COL` to `FACULTY_COL`~~

# Long time change
- Change `ClassType` to `StrEnum`. But `ALL` poses an issue.
- Migrate to `gspread` and `gspread-pandas/dataframe` from `pygsheets`
- Do a `mypy` check