import hikari, miru
from enum import Enum
from bot_environment import state


class Response:
    class Kind(Enum):
        SUCCESSFUL = 1
        WAITING = 0.5
        FAILURE = 0

    def __init__(
        self,
        comment: str,
        kind: Kind = Kind.FAILURE,
        inline_embed_fields: list[hikari.EmbedField] | None = None,
        components: miru.View | None = None,
    ) -> None:
        if kind == Response.Kind.SUCCESSFUL:
            embed = hikari.Embed(
                title=":white_check_mark: Your account has been verified",
                description=comment,
                color=0x43B581,
            )
        elif kind == Response.Kind.FAILURE:
            embed = hikari.Embed(
                title=":x: Your account could not be verified", description=comment, color=0xF04747
            )
        else:
            embed = hikari.Embed(
                title=":warning: Waiting for your Yes/No response",
                description=comment,
                color=0xFFC72B,
            )
        if inline_embed_fields:
            for field in inline_embed_fields:
                embed.add_field(field.name, field.value, inline=True)
        if components:
            state.miru_client.start_view(components)

        self.kind = kind
        self.dictionary = {
            "embed": embed,
            "components": components,
            "flags": hikari.MessageFlag.EPHEMERAL,
        }

    def keys(self):  # noqa
        return self.dictionary.keys()

    def __getitem__(self, key):  # noqa
        return self.dictionary[key]


# Raise this error after building a response if a check fails.
# As a result, following checks are not performed and immediately responded.
class VerificationFailure(Exception):
    def __init__(self, response: Response) -> None:
        self.response = response


def get_generic_verification_error_response(error: Exception, func) -> Response:  # noqa
    comment = "Something went wrong while verifying you."
    comment += " Please show this message to admins."
    comment += f"\nEncountered error while calling `{func.__name__}(...)`:"
    comment += f"\n```py\n{type(error).__name__}\n{error}```"
    return Response(comment)
