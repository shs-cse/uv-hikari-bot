import hikari
from bot_environment import state
from wrappers.utils import FormatText

from bot_environment.config import ClassType, EnrolmentSprdsht
from member_verification.response import Response


# assign theory/lab roles and section roles to faculty
async def assign_faculty_section_roles(faculty: hikari.Member, initial: str) -> Response:
    # remove all old roles
    for old_role in faculty.get_roles():
        if 0 < old_role.position <= state.faculty_role.position:
            await faculty.remove_role(old_role)
    # gather all relevant roles
    roles_to_assign = {state.faculty_role}
    for faculty_load_type, faculty_col in EnrolmentSprdsht.Routine.FACULTY_COL.items():
        # find all loads
        faculty_list = state.routine[faculty_col].astype(str) + ","
        is_faculty_load = faculty_list.str.contains(initial + ",")
        faculty_loads = state.routine.loc[
            is_faculty_load,
            [
                EnrolmentSprdsht.Routine.THEORY_SECTION_COL,
                EnrolmentSprdsht.Routine.LAB_SECTION_COL,
            ],
        ]
        # faculty subrole
        if any(is_faculty_load):
            roles_to_assign.add(state.faculty_sub_roles[faculty_load_type])
        # section roles
        for _, theory_sec, lab_sec_suffix in faculty_loads.itertuples():
            if faculty_load_type == ClassType.THEORY:
                class_type = ClassType.THEORY
            else:
                class_type = ClassType.from_lab_suffix(lab_sec_suffix)
            roles_to_assign.add(state.sec_roles[theory_sec][class_type])
    # assign all roles
    for new_role in roles_to_assign:
        print(FormatText.status(f"Assigning Role: @{new_role.name}"))
        await faculty.add_role(new_role)
    # discord response
    all_roles_mentioned = sorted(roles_to_assign, key=lambda r: r.position, reverse=True)
    all_roles_mentioned = ", ".join(role.mention for role in all_roles_mentioned)
    return Response(
        comment="You have been assigned the following roles.",
        kind=Response.Kind.SUCCESSFUL,
        inline_embed_fields=[hikari.EmbedField(name="Roles", value=all_roles_mentioned)],
    )
