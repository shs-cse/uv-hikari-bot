import hikari, crescent
from bot_environment.config import RolePermissions
from member_verification.student.check import try_student_verification
from member_verification.response import get_generic_error_response_while_verifying
from wrappers.utils import FormatText


plugin = crescent.Plugin[hikari.GatewayBot, None]()


verify_group = crescent.Group("verify", default_member_permissions=RolePermissions.BOT_ADMIN)
verify_member_sub_group = verify_group.sub_group("member")


@plugin.include
@verify_member_sub_group.child
@crescent.command(name="with-student-id")
class VerifyMemberWithStudentId:
    member: hikari.Member = crescent.option(
        hikari.User, description="Server member you want to verify."
    )
    student_id = crescent.option(
        str, name="student-id", description="Verify member with this student id."
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(True)
        try:
            response = await try_student_verification(self.member, input_text=self.student_id)
        except Exception as error:
            response = get_generic_error_response_while_verifying(error, try_student_verification)
            log = "Student Verification: raised an error while trying to verify"
            log += f" {self.member.mention} {self.member.display_name} for with {self.student_id}."
            print(FormatText.error(log))
        await ctx.respond(**response)
