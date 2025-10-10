import hikari, crescent
from bot_environment import state
from bot_environment.config import RolePermissions
from view_components.student_verification.modal_and_button import VerificationButtonView
from view_components.faculty_verification.assign_sec_button import AssignSectionsButtonView


plugin = crescent.Plugin[hikari.GatewayBot, None]()


bot_admin_post_group = crescent.Group("post", default_member_permissions=RolePermissions.BOT_ADMIN)
bot_admin_post_button_sub_group = bot_admin_post_group.sub_group("button")
bot_admin_post_message_as_bot_sub_group = bot_admin_post_group.sub_group("message-as-bot")


@plugin.include
@bot_admin_post_button_sub_group.child
@crescent.command(name="student-verification")
async def post_student_verification_button(ctx: crescent.Context) -> None:
    await ctx.defer()
    view = VerificationButtonView()
    await ctx.respond(view.post_content, components=view)


@plugin.include
@bot_admin_post_button_sub_group.child
@crescent.command(name="faculty-assign-sections")
async def post_faculty_section_assignment_button(ctx: crescent.Context) -> None:
    await ctx.defer()
    view = AssignSectionsButtonView()
    await ctx.respond(view.post_content, components=view)


@plugin.include
@bot_admin_post_message_as_bot_sub_group.child
@crescent.command(name="new-post")
class PostAsBotFromText:
    to_channel: hikari.GuildTextChannel = crescent.option(
        hikari.PartialChannel,
        name="channel-to-post-in",
        description="Channel to post your message in.",
    )
    message_content = crescent.option(
        str, name="content", description="Link to message to copy post from."
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(True)
        new_message = await plugin.app.rest.create_message(
            channel=self.to_channel, content=self.message_content
        )
        response = f"Your message has been posted to {self.to_channel.mention}:"
        response += f" {new_message.make_link(state.guild)}"
        await ctx.respond(response, ephemeral=True)


@plugin.include
@bot_admin_post_message_as_bot_sub_group.child
@crescent.command(name="copy-from-message-link")
class PostAsBotFromMessageLink:
    to_channel = crescent.option(
        hikari.PartialChannel,
        name="channel-to-post-in",
        description="Channel to post your message in.",
    )
    from_message_link = crescent.option(
        str, name="message-link", description="Link to message to copy post from."
    )

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.defer(ephemeral=True)
        snowflake_ids = self.from_message_link.split("/")
        from_message_id = snowflake_ids[-1]
        from_channel_id = snowflake_ids[-2]
        from_message = await plugin.app.rest.fetch_message(from_channel_id, from_message_id)
        new_message = await plugin.app.rest.create_message(
            channel=self.to_channel,
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
        response = f"Your message has been posted to {self.to_channel.mention}:"
        response += f" {new_message.make_link(state.guild)}"
        await ctx.respond(response, ephemeral=True)
