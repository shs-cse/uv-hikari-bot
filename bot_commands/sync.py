import hikari, crescent
from sync_with_state.sheets import update_routine, pull_from_enrolment, push_to_enrolment
from bot_environment import state
from bot_environment.config import InfoField, RolePermissions
from wrappers.pygs import get_link_from_sheet_id

plugin = crescent.Plugin[hikari.GatewayBot, None]()

bot_admin_sync_group = crescent.Group("sync", default_member_permissions=RolePermissions.BOT_ADMIN)


@plugin.include
@bot_admin_sync_group.child
@crescent.command(name="enrolment")
async def sync_enrolment(ctx: crescent.Context) -> None:
    await ctx.defer(ephemeral=True)
    pull_from_enrolment()
    push_to_enrolment()
    enrolment_link = get_link_from_sheet_id(state.info[InfoField.ENROLMENT_SHEET_ID])
    log = f"Synced [Enrolment sheet]({enrolment_link})."
    log += " Updated student list, routine and discord list."
    await ctx.respond(log)


@plugin.include
@bot_admin_sync_group.child
@crescent.command(name="routine")
async def sync_routine(ctx: crescent.Context) -> None:
    await ctx.defer(ephemeral=True)
    update_routine()
    enrolment_link = get_link_from_sheet_id(state.info[InfoField.ENROLMENT_SHEET_ID])
    log = f"Updated routine from [Enrolment sheet]({enrolment_link})."
    await ctx.respond(log)
