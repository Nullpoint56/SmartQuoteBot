from discord import Message


def clean_message_from_mentions(message: Message) -> str:
    content = message.content
    for mention in message.mentions + message.role_mentions:
        content = content.replace(mention.mention, "")
    return content.strip()