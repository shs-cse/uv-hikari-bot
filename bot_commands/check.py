import hikari, crescent
from bot_environment import state
from bot_environment.config import RolePermissions, RoleName, DisplayName
from sync_with_state.sheets import update_routine, update_student_list
from member_verification.response import get_generic_error_response_while_verifying
from member_verification.faculty.check import try_faculty_verification
from member_verification.student.check import try_student_verification
from member_verification.check import try_member_auto_verification
from wrappers.utils import FormatText

plugin = crescent.Plugin[hikari.GatewayBot, None]()

reassign_group = crescent.Group("reassign", default_member_permissions=RolePermissions.BOT_ADMIN)
reassign_sections_sub_group = reassign_group.sub_group("sections")


@plugin.include
@reassign_sections_sub_group.child
@crescent.command(name="to")
class CheckFacultySections:
    faculty: hikari.Member = crescent.option(
        hikari.User, name="faculty", description="Must have faculty role."
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(True)
        try:
            response = await try_faculty_verification(self.faculty)
        except Exception as error:
            response = get_generic_error_response_while_verifying(error, try_faculty_verification)
            log = "Faculty Verification: raised an error while trying to assgin sections to"
            log += f" {self.faculty.display_name} {self.faculty.mention}."
            print(FormatText.error(log))
        await ctx.respond(**response)


@plugin.include
@reassign_sections_sub_group.child
@crescent.command(name="to-all-faculties")
async def check_section_for_all_faculties(ctx: crescent.Context) -> None:
    await ctx.defer(True)
    update_routine()
    for member in state.guild.get_members().values():
        if member.get_top_role() != state.faculty_role:
            continue
        try:
            await try_faculty_verification(member)
        except Exception:
            log = "Faculty Verification: raised an error while trying to assgin sections to"
            log += f" {member.display_name} {member.mention}."
            print(FormatText.error(log))
    await ctx.respond("Updated all faculty section roles from routine.")


verify_group = crescent.Group("verify", default_member_permissions=RolePermissions.BOT_ADMIN)
verify_member_sub_group = verify_group.sub_group("member")


async def student_id_autocomplete_callback(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, int]]:
    suggestions = state.students.index.astype(str).str.startswith(option.value)
    suggestions = state.students.index[suggestions][:25]
    choices = []
    for student_id, name in state.students.loc[suggestions, 'Name'].items():
        name = DisplayName.STUDENT.format(student_id, name)
        choices.append((name, student_id))
    return choices


@plugin.include
@verify_member_sub_group.child
@crescent.command(name="with-student-id")
class VerifyMemberWithStudentId:
    member: hikari.Member = crescent.option(
        hikari.User, description="Server member you want to verify."
    )
    student_id = crescent.option(
        int, name="student-id", description="Verify member with this student id.",
        autocomplete=student_id_autocomplete_callback
    )  # TODO: autocomplete

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(True)
        try:
            response = await try_student_verification(self.member, str(self.student_id))
        except Exception as error:
            response = get_generic_error_response_while_verifying(error, try_student_verification)
            log = "Student Verification: raised an error while trying to verify"
            log += f" {self.member.mention} {self.member.display_name} for with {self.student_id}."
            print(FormatText.error(log))
        await ctx.respond(**response)


# same as user command for auto verification
@plugin.include
@verify_member_sub_group.child
@crescent.command(name="with-advising-server")
class VerifyMemberWithAdvisingServer:
    member: hikari.Member = crescent.option(
        hikari.User, description="Server member you want to verify."
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(True)
        try:
            response = await try_member_auto_verification(self.member)
        except Exception as error:
            response = get_generic_error_response_while_verifying(
                error, try_member_auto_verification
            )
            log = "Member Verification: raised an error while trying to verify member on join:"
            log += f" {self.member.mention} {self.member.display_name}."
            print(FormatText.error(log))
        await ctx.respond(**response)


@plugin.include
@verify_group.child
@crescent.command(name="all-members")
async def auto_verify_all_members(ctx: crescent.Context) -> None:
    await ctx.defer(True)
    update_student_list()
    for member in state.guild.get_members().values():
        if member.get_top_role().name in [RoleName.BOT, RoleName.BOT_ADMIN, RoleName.ADMIN]:
            continue
        try:
            await try_member_auto_verification(member)
        except Exception:
            log = "Member Verification: raised an error while trying to verify member on join:"
            log += f" {member.mention} {member.display_name}."
            print(FormatText.error(log))
    await ctx.respond("Verified as many members as possible.")
