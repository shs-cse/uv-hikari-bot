import crescent
import hikari

bot = hikari.GatewayBot("YOUR_TOKEN")
client = crescent.Client(bot)

# Include the command in your client - don't forget this
@client.include
# Create a slash command
@crescent.command(name="say")
class Say:
    word = crescent.option(str, "The word to say")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(self.word)

bot.run()