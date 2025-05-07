from discord import ButtonStyle, Interaction
from discord.ui import Button, View


class PrevButton(Button):
    def __init__(self, paginator):
        super().__init__(label="◀️ Prev", style=ButtonStyle.secondary)
        self.paginator = paginator

    async def callback(self, interaction: Interaction):
        if self.paginator.page > 0:
            self.paginator.page -= 1
            await self.paginator.update(interaction)
        else:
            await interaction.response.defer()


class NextButton(Button):
    def __init__(self, paginator):
        super().__init__(label="▶️ Next", style=ButtonStyle.secondary)
        self.paginator = paginator

    async def callback(self, interaction: Interaction):
        if self.paginator.page < self.paginator.max_page() - 1:
            self.paginator.page += 1
            await self.paginator.update(interaction)
        else:
            await interaction.response.defer()


class QuotePaginator(View):
    def __init__(self, quotes, per_page=10):
        super().__init__(timeout=180)
        self.quotes = quotes
        self.per_page = per_page
        self.page = 0

        # Add buttons only if we need more than 1 page
        if self.max_page() > 1:
            self.add_item(PrevButton(self))
            self.add_item(NextButton(self))

    def format_page(self):
        start = self.page * self.per_page
        end = start + self.per_page
        items = self.quotes[start:end]
        lines = [f"[#{q['id']}] {q['text']}" for q in items]
        return f"**Quotes Page {self.page + 1}/{self.max_page()}**\n" + "\n".join(lines)

    def max_page(self):
        return (len(self.quotes) - 1) // self.per_page + 1

    async def update(self, interaction: Interaction):
        content = self.format_page()
        await interaction.response.edit_message(content=content, view=self)