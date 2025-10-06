import hikari, crescent
from member_verification.check import try_member_auto_verification
from wrappers.utils import FormatText

plugin = crescent.Plugin[hikari.GatewayBot, None]()


@plugin.include
@crescent.event  # after connecting to discord
async def on_member_join(event: hikari.MemberCreateEvent) -> None:
    try:
        await try_member_auto_verification(event.member)
    except Exception:
        log = "Member Verification: raised an error while trying to verify member on join:"
        log += f" {event.member.mention} {event.member.display_name}."
        print(FormatText.error(log))


@plugin.include
@crescent.event  # after connecting to discord
async def on_this_bot_join(event: hikari.GuildJoinEvent) -> None:
    new_guild = await event.fetch_guild()
    log = f"Bot has joined the {FormatText.bold(new_guild.name)} server."
    print(FormatText.success(FormatText.bold(log)))
