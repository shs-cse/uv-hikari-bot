import hikari, crescent, re
from bot_environment import state
from bot_environment.config import InfoKey, RolePermissions, ClassType
from bot_environment.config import RegexPattern, EnrolmentSprdsht, SpecialChars
from sync_with_state.marks import update_marks_data, fetch_marks, display_marks


plugin = crescent.Plugin[hikari.GatewayBot, None]()


async def exit_if_marks_is_disabled(ctx: crescent.Context) -> crescent.HookResult:
    if not state.info[InfoKey.MARKS_ENABLED]:
        log = "Marks feature is disabled. This command is currently unavailable."
        await ctx.respond(log, ephemeral=True)
        return crescent.HookResult(exit=True)
    return crescent.HookResult()


faculty_marks_group = crescent.Group(
    name="marks",
    default_member_permissions=RolePermissions.FACULTY,
    hooks=[exit_if_marks_is_disabled],
)


async def faculty_marks_section_autocomplete_callback(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, int]]:
    choices = []
    for sec in state.available_secs:
        role = state.sec_roles[sec][ClassType.THEORY]
        if role in ctx.member.get_roles():
            choices.append((f"Theory Section {sec:02d}", sec))
    return choices


@plugin.include
@faculty_marks_group.child
@crescent.command(name="update", description="Update marks data from section marks sheets.")
class UpdateMarks:
    section = crescent.option(
        int,
        name="section",
        description="Whose marks you wish to update. You must be one of the theory faculty of it.",
        autocomplete=faculty_marks_section_autocomplete_callback,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        if state.sec_roles[self.section][ClassType.THEORY] not in ctx.member.get_roles():
            log = f"Can't update marks for section {self.section:02d}"
            log += " beacuase you are not the theory faculty."
        else:
            update_marks_data(self.section)
            log = f"Updated marks data for section {self.section:02d}."
        await ctx.respond(log)


def extract_student_id_and_marks_sec(student: hikari.Member) -> tuple[int, int]:
    student_id = int(re.search(RegexPattern.MEMBER_INITIAL, student.display_name).group(1))
    marks_sec = int(state.students[EnrolmentSprdsht.Students.MARKS_SEC_COL].loc[student_id])
    return student_id, marks_sec


async def marks_assessment_autocomplete_callback(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    try:
        member = state.guild.get_member(int(ctx.options["student"])) # FetchMarks class variable
        if member.get_top_role() != state.student_role:
            return []
        _, marks_sec = extract_student_id_and_marks_sec(member)
        col_list = [
            (subbed, col)
            for col in state.published_marks[marks_sec].columns
            if option.value.lower()
            in (subbed := col.replace(SpecialChars.PARENT_CHILD_CHAR, " > ")).lower()
        ]
        return col_list[:25]
    except Exception:
        return []


@plugin.include
@faculty_marks_group.child
@crescent.command(name="fetch", description="Fetch marks data of student.")
class FetchMarks:
    student: hikari.Member = crescent.option(
        hikari.User,
        name="student",
        description="Whose marks you wish to fetch.",
    )

    assessment = crescent.option(
        str,
        name="assessment",
        description="Choose which assessment's marks you wish to fetch",
        autocomplete=marks_assessment_autocomplete_callback,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        if self.student.get_top_role() != state.student_role:
            log = f"{self.student} is not a verified student. Can't fetch marks."
            await ctx.respond(log, ephemeral=True)
            return
        student_id, marks_sec = extract_student_id_and_marks_sec(self.student)
        marks_df = fetch_marks(student_id, self.assessment, marks_sec)
        if marks_df is None:
            log = "Marks was not found for:"
            log += f" {marks_sec} > {student_id} > {self.assessment}."
            await ctx.respond(log, ephemeral=True)
            return
        # actually display marks
        response = f"{ctx.member.mention} Here is your marks details."
        name = state.students[EnrolmentSprdsht.Students.NAME_COL].loc[student_id]
        dummy_url = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}"
        embed = display_marks(student_id, name, marks_df, dummy_url)
        await ctx.respond(content=response, embed=embed, ephemeral=True)
