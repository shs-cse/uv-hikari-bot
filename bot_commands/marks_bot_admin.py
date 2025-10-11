import hikari, crescent, asyncio
from bot_environment import state
from bot_environment.config import InfoKey, RolePermissions
from setup_validation.marks import check_marks_groups_and_sheets
from sync_with_state.marks import load_marks_data
from wrappers.utils import update_info_key

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
        await plugin.app.update_presence(status=hikari.Status.IDLE)
        await asyncio.to_thread(check_marks_groups_and_sheets)
        await asyncio.to_thread(load_marks_data)
        await plugin.app.update_presence(status=hikari.Status.ONLINE)
        log = "Marks feature has been enabled."
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
        for sec in state.available_secs:
            state.published_marks[sec] = None
        log = "Marks feature has been disabled."
    await ctx.respond(log)