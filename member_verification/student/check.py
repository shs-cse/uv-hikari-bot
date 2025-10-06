import hikari, re
from bot_environment.config import RegexPattern
from member_verification.response import Response, VerificationFailure
from member_verification.student.success import verify_student
from member_verification.student.failure import (check_retyped_user_input, 
                                                 check_if_input_is_a_valid_id, 
                                                 check_if_student_id_is_in_database,
                                                 check_if_student_id_is_already_taken,
                                                 check_if_matches_advising_server)
from member_verification.student_tutor.check import check_if_student_is_st
from member_verification.student_tutor.success import verify_student_tutor



# check if a member can be verified with a student id
async def try_student_verification(
    member: hikari.Member, input_text: str, reinput_text: str = None
) -> Response:
    try:  # possible cases of VerificationFailure:
        # 0. retyped input does not match
        if reinput_text:
            check_retyped_user_input(input_text, reinput_text)
        # 1. id is not a valid student id
        extracted_id_ish = re.search(RegexPattern.STUDENT_ID, input_text)
        check_if_input_is_a_valid_id(input_text, extracted_id_ish)
        # 2. id is valid but not in the sheet
        student_id = int(extracted_id_ish.group())
        # 2.5. first check if student is an st
        st_initial = check_if_student_is_st(student_id)
        if st_initial:
            return await verify_student_tutor(member, st_initial)
        check_if_student_id_is_in_database(student_id)
        # 3. id is valid and in the sheet, but already taken (by another student/their old id)
        #       a. taken by another -> contact admin.
        #       b. taken by their old id -> remove old id from sheet
        check_if_student_id_is_already_taken(member, student_id)
        # 4. id is valid and in the sheet, but discord does not match with advising server id
        #       response with buttons (you sure?)
        await check_if_matches_advising_server(member, student_id)
        # 5. (success) id is valid and in the sheet, 
        #       but no discord id in advising server/matches with advising id
        return await verify_student(member, student_id)
    except VerificationFailure as failure:
        return failure.response
