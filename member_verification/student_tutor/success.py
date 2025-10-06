import hikari
from bot_environment import state
from bot_environment.config import ClassType, DisplayName, EnrolmentSprdsht
from member_verification.response import Response
from wrappers.utils import FormatText


async def verify_student_tutor(member: hikari.Member, st_initial: str) -> Response:
    # extract st information
    st_routine = state.routine[[EnrolmentSprdsht.Routine.THEORY_SECTION_COL, 
                                EnrolmentSprdsht.Routine.ST_INITIAL_COL, 
                                EnrolmentSprdsht.Routine.ST_NAME_COL]]
    st_routine.set_index(EnrolmentSprdsht.Routine.THEORY_SECTION_COL, inplace=True)
    st_routine = st_routine[st_initial == st_routine[EnrolmentSprdsht.Routine.ST_INITIAL_COL]]
    st_name = st_routine[EnrolmentSprdsht.Routine.ST_NAME_COL].iloc[0]
    st_display_name = DisplayName.STUDENT_TUTOR.format(st_initial, st_name)
    st_display_name = st_display_name[:32]
    member = await member.edit(nickname=st_display_name)
    # assign theory section roles and st role
    roles_to_assign = [state.st_role]
    for theory_sec in st_routine.index.tolist():
        roles_to_assign.append(state.sec_roles[theory_sec][ClassType.THEORY])
    for role in roles_to_assign:
        await member.add_role(role)
    log = f"Student Verification: {member.mention} was verified as an ST"
    log += f" with initial {st_initial} and roles: "
    log += ', '.join('@'+role.name for role in roles_to_assign)
    print(FormatText.warning(log))
    comment = f"You have been verified as {st_name} (ST initial: {st_initial})."
    comment += f" If this is wrong, contact {state.admin_role.mention}"
    return Response(
        comment,
        Response.Kind.SUCCESSFUL,
        inline_embed_fields=[
            hikari.EmbedField(name="Student Tutor", value=member.mention),
            hikari.EmbedField(
                name="Roles", value=", ".join(role.mention for role in roles_to_assign)
            )
        ],
    )
