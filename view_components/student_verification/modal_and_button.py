import hikari, miru
from bot_environment import state
from bot_environment.config import ChannelName
from member_verification.response import get_generic_verification_error_response
from member_verification.student.check import try_student_verification
from wrappers.discord import get_channel_by_name
from wrappers.utils import FormatText


class VerificationButtonView(miru.View):
    def __init__(self) -> None:
        admin_help_channel = get_channel_by_name(ChannelName.ADMIN_HELP)
        self.post_content = "## Please Enter Your Student ID!!\n"
        self.post_content += "Otherwise you **__will not__** be able to see the whole server,"
        self.post_content += " including your own *section announcements* and *study-materials*."
        self.post_content += "\n\nIf you are facing trouble,"
        self.post_content += f" please contact {state.admin_role.mention}s"
        self.post_content += f" by posting on the {admin_help_channel.mention} channel.\n"
        super().__init__(timeout=None)

    @miru.button(
        label="Enter Student ID",
        emoji="🪪",
        custom_id="student_verification_button",
        style=hikari.ButtonStyle.SUCCESS,
    )
    async def student_verification_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        await ctx.respond_with_modal(StudentIdModalView())


class StudentIdModalView(miru.Modal):
    student_id = miru.TextInput(
        label="What's your ***Student ID***?",
        custom_id="student_verification_modal_textinput_1",
        placeholder="12345678",
        min_length=8,
        max_length=10,
        required=True,
    )

    retyped_id = miru.TextInput(
        label="Retype your ***Student ID***.",
        custom_id="student_verification_modal_textinput_2",
        placeholder="12345678",
        min_length=8,
        max_length=10,
        required=True,
    )

    def __init__(self) -> None:
        super().__init__(
            title="Student Identification Form",
            timeout=None,
            custom_id="student_verification_modal",
        )

    async def callback(self, ctx: miru.ModalContext) -> None:
        await ctx.defer(
            response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE,
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        try:
            response = await try_student_verification(
                member=ctx.member,
                input_text=self.student_id.value,
                reinput_text=self.retyped_id.value,
            )
        except Exception as error:
            response = get_generic_verification_error_response(error, try_student_verification)
            log = "Student Verification: raised an error while trying to submit a modal for"
            log += f" {self.student_id.value}/{self.retyped_id.value}."
            print(FormatText.error(log))
        await ctx.respond(**response)
