import hikari
from bot_environment import state
from bot_environment.config import EnrolmentSprdsht
from member_verification.faculty.check import try_faculty_verification
from member_verification.response import Response, VerificationFailure
from member_verification.student.failure import check_if_student_id_is_already_taken
from member_verification.student.success import verify_student
from wrappers.utils import FormatText


async def try_member_auto_verification(member: hikari.Member) -> Response:
    response = await try_faculty_verification(member)
    if response.kind == Response.Kind.SUCCESSFUL:
        return response
    # try verifying by advising discord server id
    ADVISING_DISCORD_ID_COL = EnrolmentSprdsht.Students.ADVISING_DISCORD_ID_COL
    if str(member.id) in state.students[ADVISING_DISCORD_ID_COL].values:
        student_id = state.students[ADVISING_DISCORD_ID_COL] == str(member.id)
        student_id = state.students.index[student_id][0]
        try:
            check_if_student_id_is_already_taken(member, student_id)
            return await verify_student(member, student_id)
        except VerificationFailure as failure:
            log = f"Advising Server Verified Member {member.mention} {member.display_name}"
            log += f" joined course server; but student id {student_id} already taken someone else."
            print(FormatText.warning(log))
            return failure.response
    return Response(
        f"Auto-verification was not possible for {member.mention} {member.display_name}."
    )
