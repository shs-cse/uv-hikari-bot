import hikari, crescent
from member_verification.response import get_generic_verification_error_response
from member_verification.check import try_member_auto_verification
from bot_environment.config import RolePermissions
from wrappers.utils import FormatText

plugin = crescent.Plugin[hikari.GatewayBot, None]()


@plugin.include
@crescent.user_command(
    name="Try to Auto-Verify Member", default_member_permissions=RolePermissions.BOT_ADMIN
)
async def check_member(ctx: crescent.Context, member: hikari.Member) -> None:
    await ctx.defer(True)
    try:
        response = await try_member_auto_verification(member)
    except Exception as error:
        response = get_generic_verification_error_response(error, try_member_auto_verification)
        log = "Member Verification: raised an error while trying to"
        log += f" verify member automatically: {member.mention} {member.display_name}."
        print(FormatText.error(log))
    await ctx.respond(**response)
