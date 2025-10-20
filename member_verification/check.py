import hikari, re
from bot_environment import state
from bot_environment.config import EnrolmentSprdsht, RegexPattern
from member_verification.faculty.check import try_faculty_verification
from member_verification.response import Response
from member_verification.student.check import try_student_verification


async def try_member_auto_verification(member: hikari.Member) -> Response:
    response = await try_faculty_verification(member)
    if response.kind == Response.Kind.SUCCESSFUL:
        return response
    # try verifying by advising discord server id
    ADVISING_DISCORD_ID_COL = EnrolmentSprdsht.Students.ADVISING_DISCORD_ID_COL
    if str(member.id) in state.students[ADVISING_DISCORD_ID_COL].values:
        student_id = state.students[ADVISING_DISCORD_ID_COL] == str(member.id)
        student_id = state.students.index[student_id][0]
    elif state.student_role == member.get_top_role():
        # already verified before, expects correct nickname pattern
        student_id = int(re.search(RegexPattern.MEMBER_INITIAL, member.display_name).group(1))
    else:
        student_id = 0
    if not student_id:
        log = f"Auto-verification was not possible for {member.mention} {member.display_name}."
        return Response(log)
    return await try_student_verification(member, str(student_id))
