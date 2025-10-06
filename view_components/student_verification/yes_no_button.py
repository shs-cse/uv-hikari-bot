import hikari, miru
from member_verification.response import Response
from member_verification.student.success import verify_student
from wrappers.utils import FormatText


class YesNoButtonsView(miru.View):
    def __init__(self, member: hikari.Member, student_id: int) -> None:
        self.member = member
        self.student_id = student_id
        super().__init__(timeout=None)
    
    @miru.button(label="YES, Use This Alt Account!", style=hikari.ButtonStyle.DANGER)
    async def yes_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        self.stop()
        try:
            response = await verify_student(self.member, self.student_id)
        except Exception as error:
            log = f"Student Verification: {self.member.mention} tried to take"
            log += f" {self.student_id} with alt account; but raised error."
            print(FormatText.error(log))
            response = get_response_for_error(error, 'verify_student')
        await ctx.edit_response(**response)
        
    @miru.button(label="NO, I'll Use Advising Server Account.", style=hikari.ButtonStyle.PRIMARY)
    async def no_button(self, ctx: miru.ViewContext, button: miru.Button) -> None:
        self.stop()
        log = f"Student Verification: {self.member.mention} chose to"
        log += f" take {self.student_id} with advising server account."
        print(FormatText.success(FormatText.dim(log)))
        comment = "You selected **\"NO\"**. Please try again with your **advising server account**."
        response = Response(comment)
        await ctx.edit_response(**response)
        
        
def get_response_for_error(error: Exception, function_name: str) -> Response:
    comment = "Something went wrong while verifying you." 
    comment += " Please show this message to admins."
    comment += f"\nEncountered error while calling `{function_name}(...)`:"
    comment += f"\n```py\n{type(error).__name__}\n{error}```"
    return Response(comment)
    