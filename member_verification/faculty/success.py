import hikari
from bot_environment import state
from wrappers.utils import FormatText

from bot_environment.config import ClassType, EnrolmentSprdsht
from member_verification.response import Response


def extract_section_and_class_type(load: str, is_theory: bool) -> tuple:
    lab_type = ClassType.from_lab_suffix(load[-1])
    if lab_type != ClassType.LAB:
        load = load[:-1]
    theory_sec = int(load)
    class_type = ClassType.THEORY if is_theory else lab_type
    # match load[-1]:
    #     case "A":
    #         theory_sec = int(load[:-1])
    #         class_type = ClassType.THEORY if is_theory else ClassType.LAB_A
    #     case "B":
    #         theory_sec = int(load[:-1])
    #         class_type = ClassType.THEORY if is_theory else ClassType.LAB_B
    #     case _:
    #         theory_sec = int(load)
    #         class_type = ClassType.THEORY if is_theory else ClassType.LAB
    return theory_sec, class_type


# assign theory/lab roles and section roles to faculty
async def assign_faculty_section_roles(faculty: hikari.Member, initial: str) -> Response:
    # remove all old roles
    for old_role in faculty.get_roles():
        if 0 < old_role.position <= state.faculty_role.position:
            await faculty.remove_role(old_role)
    # add new roles
    roles_to_assign = {state.faculty_role}
    for faculty_load_type, faculty_col in EnrolmentSprdsht.Routine.FACULTY_COL.items():
        faculty_list = state.routine[faculty_col]
        is_faculty_load = faculty_list.str.contains(initial)
        faculty_load = state.routine.index[is_faculty_load].tolist()
        for load in faculty_load:
            roles_to_assign.add(state.faculty_sub_roles[faculty_load_type])
            theory_sec, class_type = extract_section_and_class_type(
                str(load), faculty_load_type == ClassType.THEORY
            )
            roles_to_assign.add(state.sec_roles[theory_sec][class_type])
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
