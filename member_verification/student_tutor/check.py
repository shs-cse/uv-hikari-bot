from bot_environment import state
from bot_environment.config import EnrolmentSprdsht

# Case 1.5: student id is student tutor
def check_if_student_is_st(student_id:int) -> str | None:
    is_st = state.routine[EnrolmentSprdsht.Routine.ST_ID_COL] == student_id
    if any(is_st):
        return state.routine[EnrolmentSprdsht.Routine.ST_INITIAL_COL][is_st].iloc[0]