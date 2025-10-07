import hikari, crescent
from bot_environment import state
from bot_environment.config import RolePermissions, ChannelName
from wrappers.discord import get_channel_by_name

plugin = crescent.Plugin[hikari.GatewayBot, None]()


@plugin.include
@crescent.message_command(
    name="Post to General Announcement", default_member_permissions=RolePermissions.BOT_ADMIN
)
async def post_to_general_announcement(ctx: crescent.Context, from_message: hikari.Message) -> None:
    await ctx.defer(True)
    general_announcement_channel = get_channel_by_name(ChannelName.GENERAL_ANNOUNCEMENT)
    new_message = await plugin.app.rest.create_message(
        channel=general_announcement_channel,
        content=from_message.content,
        attachments=from_message.attachments,
        # components=from_message.components, # raises error
        embeds=from_message.embeds,
        stickers=from_message.stickers,
        tts=from_message.is_tts,
        mentions_everyone=from_message.mentions_everyone,
        user_mentions=from_message.user_mentions_ids,
        role_mentions=from_message.role_mention_ids,
    )
    response = f"Your message has been posted to {general_announcement_channel.mention}:"
    response += f" {new_message.make_link(state.guild)}"
    await ctx.respond(response)
