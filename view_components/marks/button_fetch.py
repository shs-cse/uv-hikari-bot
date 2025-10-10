import hikari, miru
from bot_environment import state
from bot_environment.config import SpecialChars, InfoKey, ClassType
from wrappers.utils import FormatText, update_info_key
from view_components.marks.embed_and_nav import create_marks_navigator


def get_custom_id(section: int, assessment: str) -> str:
    # NOTE: be careful, custom id can be a max of 100 chars/bytes
    return f"{section}{SpecialChars.MARKS_BUTTON_ID_SEP}{assessment}"


class ShowMarksView(miru.View):
    def __init__(self, sec: int, assessment: str, faculty_text: str = "") -> None:
        super().__init__(timeout=None)
        # post content
        sec_role = state.sec_roles[sec][ClassType.THEORY]
        assessment_title = assessment.split(SpecialChars.PARENT_CHILD_CHAR)[-1]
        self.post_content = f"# {assessment_title.title()} Marks"
        self.post_content += f"\n{sec_role.mention} Click the button below to show your marks."
        self.post_content += f"\n{faculty_text}\n" if faculty_text else "\n"
        self.post_content += "\n-# New buttons will show up for you to see"
        self.post_content += " further breakdown of your marks."
        # update toml info if needed
        if assessment not in state.info[InfoKey.MARKS_BUTTONS][str(sec)]:
            all_custom_ids = state.info[InfoKey.MARKS_BUTTONS].copy()  # for comparison
            all_custom_ids[str(sec)] = [*all_custom_ids[str(sec)], assessment]  # NOTE: don't append
            update_info_key(InfoKey.MARKS_BUTTONS, all_custom_ids)
        # create and add button to view
        self.button = miru.Button(
            label="Show Marks",
            emoji="📝",
            custom_id=get_custom_id(sec, assessment),
            style=hikari.ButtonStyle.DANGER,
        )
        self.button.callback = self.show_marks_button
        self.add_item(self.button)

    async def show_marks_button(self, ctx: miru.ViewContext) -> None:
        await ctx.defer(flags=hikari.MessageFlag.EPHEMERAL)
        if ctx.member.get_top_role() != state.student_role:
            log = "Can't show marks because you are not a verified student."
            await ctx.respond(log, flags=hikari.MessageFlag.EPHEMERAL)
            return
        try:  # to actually show marks
            section, assessment = self.button.custom_id.split(SpecialChars.MARKS_BUTTON_ID_SEP, 1)
            section = int(section)
            navigator = create_marks_navigator(ctx.member, assessment)
            builder = await navigator.build_response_async(state.miru_client)
            await builder.send_to_channel(ctx.channel_id)
            state.miru_client.start_view(navigator)
        except Exception as err:
            log = "Something went wrong, can't fetch marks:"
            log += f"\n```\n{err}```"
            print(FormatText.error(err))
            await ctx.respond(log, flags=hikari.MessageFlag.EPHEMERAL)
