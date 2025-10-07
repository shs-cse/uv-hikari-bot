import hikari, crescent
from bot_environment import state
from bot_environment.config import InfoField, RolePermissions
from wrappers.utils import update_info_key
from setup_validation.marks import check_marks_groups_and_sheets

plugin = crescent.Plugin[hikari.GatewayBot, None]()

bot_admin_marks_group = crescent.Group(
    "marks", default_member_permissions=RolePermissions.BOT_ADMIN
)


# @admin enable marks -> check and be ready to load marks.
@plugin.include
@bot_admin_marks_group.child
@crescent.command(name="enable")
async def marks_enable(ctx: crescent.Context) -> None:
    await ctx.defer(ephemeral=True)
    if state.info[InfoField.MARKS_ENABLED]:
        log = "Marks feature is already enabled."
    else:
        update_info_key(InfoField.MARKS_ENABLED, True)
        check_marks_groups_and_sheets()
        log = "Marks feature has been enabled."
        log += " All previously published marks has to be republished by faculties."
    await ctx.respond(log)


# @admin disable marks -> turn off all button, clear variables to save memory.
@plugin.include
@bot_admin_marks_group.child
@crescent.command(name="disable")
async def marks_disable(ctx: crescent.Context) -> None:
    await ctx.defer(ephemeral=True)
    if not state.info[InfoField.MARKS_ENABLED]:
        log = "Marks feature is already disabled."
    else:
        update_info_key(InfoField.MARKS_ENABLED, False)
        ...  # TODO: delete variables to save memory
        log = "Marks feature has been disabled."
    await ctx.respond(log)