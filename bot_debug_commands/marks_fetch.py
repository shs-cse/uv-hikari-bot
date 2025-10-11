import hikari, crescent
import pandas as pd
from bot_commands.marks_faculty import marks_assessment_choices
from bot_environment import state
from bot_environment.config import RolePermissions, EnrolmentSprdsht
from sync_with_state.marks import fetch_marks
from view_components.marks.embed_and_nav import create_marks_embed

plugin = crescent.Plugin[hikari.GatewayBot, None]()


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