import hikari, crescent
import pandas as pd
from bot_commands.marks_faculty import marks_assessment_choices
from bot_environment import state
from bot_environment.config import InfoKey, RolePermissions, PluginPathName, EnrolmentSprdsht
from setup_validation.marks import check_marks_groups_and_sheets
from sync_with_state.marks import fetch_marks
from wrappers.utils import update_info_key
from view_components.marks.embed_and_nav import create_marks_embed

plugin = crescent.Plugin[hikari.GatewayBot, None]()

bot_admin_enable_group = crescent.Group(
    "enable", default_member_permissions=RolePermissions.BOT_ADMIN
)


# @admin enable marks -> check and be ready to load marks.
@plugin.include
@bot_admin_enable_group.child
@crescent.command(name="marks-features")
async def marks_enable(ctx: crescent.Context) -> None:
    await ctx.defer(ephemeral=True)
    if state.info[InfoKey.MARKS_ENABLED]:
        log = "Marks feature is already enabled."
    else:
        update_info_key(InfoKey.MARKS_ENABLED, True)
        check_marks_groups_and_sheets()
        ...  # TODO: load marks sections
        ...  # TODO: load actual marks data
        log = "Marks feature has been enabled."
        log += " All previously published marks has to be republished by faculties."
    await ctx.respond(log)


bot_admin_disable_group = crescent.Group(
    "disable", default_member_permissions=RolePermissions.BOT_ADMIN
)


# @admin disable marks -> turn off all button, clear variables to save memory.
@plugin.include
@bot_admin_disable_group.child
@crescent.command(name="marks-features")
async def marks_disable(ctx: crescent.Context) -> None:
    await ctx.defer(ephemeral=True)
    if not state.info[InfoKey.MARKS_ENABLED]:
        log = "Marks feature is already disabled."
    else:
        update_info_key(InfoKey.MARKS_ENABLED, False)
        ...  # TODO: delete variables to save memory
        ...  # TODO: unload faculty marks commands
        plugin.client.plugins.unload(PluginPathName.MARKS_FACULTY)
        log = "Marks feature has been disabled."
    await ctx.respond(log)


bot_admin_fetch_group = crescent.Group(
    "fetch", default_member_permissions=RolePermissions.BOT_ADMIN
)


async def marks_assessment_by_student_autocomplete_callback(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    student_id = ctx.options["student-id"]
    section = state.students[EnrolmentSprdsht.Students.MARKS_SEC_COL].loc[student_id]
    return marks_assessment_choices(section, option.value)


@plugin.include
@bot_admin_fetch_group.child
@crescent.command(name="raw-marks", description="Fetch marks data of student.")
class FetchRawMarks:
    student_id: hikari.Member = crescent.option(
        int,
        name="student-id",
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
        marks_df = fetch_marks(self.student_id, self.assessment)
        log = "```\n"
        if isinstance(marks_df, pd.DataFrame):
            log += f"{marks_df.to_string(line_width=95)}"
        else:
            log += f"{marks_df}"
        log += "\n```"
        await ctx.respond(log)


@plugin.include
@bot_admin_fetch_group.child
@crescent.command(name="embed-marks", description="Fetch marks data of student.")
class FetchEmbedMarks:
    student_id: hikari.Member = crescent.option(
        int,
        name="student-id",
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
        marks_df = fetch_marks(self.student_id, self.assessment)
        name = state.students[EnrolmentSprdsht.Students.NAME_COL].loc[self.student_id]
        embed = create_marks_embed(self.student_id, name, marks_df)
        await ctx.respond(embed=embed)