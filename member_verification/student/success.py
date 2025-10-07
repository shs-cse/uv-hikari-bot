import hikari
from bot_environment import state
from bot_environment.config import EnrolmentSprdsht, ClassType, DisplayName
from member_verification.response import Response
from wrappers.utils import FormatText


async def update_student_nickname(
    student: hikari.Member, student_id: int, student_name: str
) -> hikari.Member:
    return await student.edit(
        nickname=DisplayName.fmt(DisplayName.STUDENT, student_id, student_name)
    )


async def assign_student_section_roles(
    student: hikari.Member, section: int, class_type: ClassType
) -> set[hikari.Role]:
    roles_to_assign = {
        state.sec_roles[section][ClassType.THEORY],
        state.sec_roles[section][class_type],
    }
    # add @student role
    if student.get_top_role() != state.student_role:
        roles_to_assign.add(state.student_role)
    # handle section role
    existing_sec_roles = state.all_sec_roles & set(student.get_roles())
    if not existing_sec_roles:
        for role in roles_to_assign:
            await student.add_role(role)
    elif (
        len(existing_sec_roles) != 2  # may have manually assigned roles
        or state.sec_roles[section][ClassType.THEORY] not in existing_sec_roles
    ):
        for role in existing_sec_roles:
            await student.remove_role(role)
        for role in roles_to_assign:
            await student.add_role(role)
    return roles_to_assign


# passed all checks, should verify member
async def verify_student(student: hikari.Member, student_id: int) -> Response:
    student_name = state.students.loc[student_id, EnrolmentSprdsht.Students.NAME_COL]
    student_name = student_name.title()
    theory_sec = int(state.students.loc[student_id, EnrolmentSprdsht.Students.SECTION_COL])
    lab_sec = state.students.loc[student_id, EnrolmentSprdsht.Students.LAB_SECTION_COL]
    class_type = ClassType.from_lab_suffix(lab_sec)

    student = await update_student_nickname(student, student_id, student_name)
    student_roles_new = await assign_student_section_roles(student, theory_sec, class_type)
    student_roles = sorted(student_roles_new, key=lambda r: r.position, reverse=True)

    # print information about the change
    log = f"Student Verification: {student.mention} was verified"
    log += f" with id ({student_id}) and roles for section {theory_sec}"
    log += ": " + ", ".join("@" + role.name for role in student_roles)
    print(FormatText.success(log))
    comment = f"### You have been successfully verified as {student_name}"
    comment += f" (ID: {student_id}) from section {theory_sec}."
    comment += " If this is not you, you may leave the server and try again."
    response = Response(
        comment,
        kind=Response.Kind.SUCCESSFUL,
        inline_embed_fields=[
            hikari.EmbedField(name="Student ID", value=f"{student_id}"),
            hikari.EmbedField(name="Student Name", value=student_name),
            hikari.EmbedField(name="Section", value=f"{theory_sec:02d}"),
            hikari.EmbedField(
                name="New Roles",
                value=", ".join(role.mention for role in student_roles if role.position > 0),
            ),
        ],
    )
    return response
