import hikari, crescent, re
from bot_environment import state
from bot_environment.config import InfoKey, RolePermissions, ClassType
from bot_environment.config import RegexPattern, EnrolmentSprdsht, SpecialChars
from sync_with_state.marks import update_marks_data
from wrappers.utils import FormatText
from view_components.marks.button_fetch import ShowMarksView
from view_components.marks.embed_and_nav import create_marks_navigator


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
        description="Section whose marks you wish to update. You must be its theory faculty.",
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


def marks_assessment_choices(section: int, search_text: str) -> list[tuple[str, str]]:
    col_list = [
        (subbed, col)
        for col in state.published_marks[section].columns
        if search_text.lower()
        in (subbed := col.replace(SpecialChars.PARENT_CHILD_CHAR, " > ")).lower()
    ]
    return col_list[:25]


async def marks_assessment_by_student_autocomplete_callback(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    try:
        member = state.guild.get_member(
            int(ctx.options["student"])
        )  # TODO: generalize this FetchMarks class variable
        if member.get_top_role() != state.student_role:
            return []
        _, marks_sec = extract_student_id_and_marks_sec(member)
        return marks_assessment_choices(marks_sec, option.value)
    except Exception:
        return []


@plugin.include
@faculty_marks_group.child
@crescent.command(name="fetch", description="Fetch marks data of student.")
class FetchMarks:
    student: hikari.Member = crescent.option(
        hikari.User,
        name="student",
        description="Student whose marks you wish to fetch.",
    )

    assessment = crescent.option(
        str,
        name="assessment",
        description="Choose which assessment's marks you wish to fetch.",
        autocomplete=marks_assessment_by_student_autocomplete_callback,
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        try:
            navigator = create_marks_navigator(self.student, self.assessment)
            bldr = await navigator.build_response_async(state.miru_client)
            await ctx.edit(content=bldr.content, components=bldr.components, embeds=bldr.embeds)
            state.miru_client.start_view(navigator)
        except Exception as log:
            print(FormatText.error(log))
            await ctx.respond("Something went wrong, can't fetch marks.")
            
            


async def marks_assessment_by_section_autocomplete_callback(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    try:
        section = int(ctx.options["section"])
        if section not in state.available_secs:
            return []
        return marks_assessment_choices(section, option.value)
    except Exception:
        return []


@plugin.include
@faculty_marks_group.child
@crescent.command(name="post", description="Post Button for showing marks.")
class PostMarksButton:
    section = crescent.option(
        int,
        name="section",
        description="Section whose marks you wish students to see. You must be its theory faculty.",
        autocomplete=faculty_marks_section_autocomplete_callback,
    )

    assessment = crescent.option(
        str,
        name="assessment",
        description="Choose which assessment's marks you wish to show.",
        autocomplete=marks_assessment_by_section_autocomplete_callback,
    )

    faculty_text = crescent.option(
        str,
        name="text",
        description="Bot will auto add main text. But if you want to add more, input here.",
        default="",
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(True)
        sec_role = state.sec_roles[self.section][ClassType.THEORY]
        if sec_role not in ctx.member.get_roles():
            log = f"Can't post marks for section {self.section:02d}"
            log += " beacuase you are not the theory faculty."
        elif self.assessment not in state.published_marks[self.section].columns:
            log = "Can't post marks for assessment because it is not published (locally)."
            log += " Either the assessment was not published, or"
            log += " marks was not updated afterwards."
        else:
            # add button
            view = ShowMarksView(self.section, self.assessment, self.faculty_text)
            await ctx.channel.send(content=view.post_content, components=view)
            state.miru_client.start_view(view, bind_to=None)
            log = "Marks button has been created."
        await ctx.respond(log)
