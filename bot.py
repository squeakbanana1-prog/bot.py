import os
import re
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GITBOOK_BASE = os.getenv("GITBOOK_BASE", "").rstrip("/") + "/"

if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in .env")
if not GITBOOK_BASE.startswith("http"):
    raise RuntimeError("Missing/invalid GITBOOK_BASE in .env (must start with https://...)")

import threading
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def start_web_server():
    # Render provides PORT; locally you can default to 10000
    port = int(os.getenv("PORT", "10000"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            # simple health endpoint
            if self.path in ("/", "/healthz"):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"ok")
            else:
                self.send_response(404)
                self.end_headers()

        # keep logs quiet
        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
import time

BUY_URL = "https://zoomcheats.mysellauth.com/"
FAQ_URL = "https://zoomcheats.gitbook.io/zoomcheats"  # optional; can be your GitBook FAQ page or a Discord message link
BOT_VERSION = "1.0.0"  # bump this when you deploy changes

START_TIME = time.time()



DOCS = {
    # Rainbow Six Siege
    "lethal": "rainbow-six-siege./lethal-lite-and-full-r6s",
    "lethal lite": "rainbow-six-siege./lethal-lite-and-full-r6s",
    "lethal full": "rainbow-six-siege./lethal-lite-and-full-r6s",
    "lethal-lite-and-full-r6s": "rainbow-six-siege./lethal-lite-and-full-r6s",

    "crusader": "rainbow-six-siege./cursader-r6s",
    "cursader-r6s": "rainbow-six-siege./cursader-r6s",

    "aptitude": "rainbow-six-siege./aptitude-recoil-r6s",
    "aptitude recoil": "rainbow-six-siege./aptitude-recoil-r6s",
    "aptitude-recoil-r6s": "rainbow-six-siege./aptitude-recoil-r6s",

    "vega": "/rainbow-six-siege./vega-r6",

    "zeroday": "rainbow-six-siege./zeroday-r6s",
    "zero day": "rainbow-six-siege./zeroday-r6s",
    "zeroday-r6s": "rainbow-six-siege./zeroday-r6s",

    "calamari": "rainbow-six-siege./calamari-r6s",
    "calamari-r6s": "rainbow-six-siege./calamari-r6s",

    "ring 1": "rainbow-six-siege./ring-1-basic-and-full-r6s",
    "ring1": "rainbow-six-siege./ring-1-basic-and-full-r6s",
    "ring 1 basic": "rainbow-six-siege./ring-1-basic-and-full-r6s",
    "ring 1 full": "rainbow-six-siege./ring-1-basic-and-full-r6s",
    "ring-1-basic-and-full-r6s": "rainbow-six-siege./ring-1-basic-and-full-r6s",

    # FiveM
    "susano": "fivem/susano-fivem",
    "susano fivem": "fivem/susano-fivem",
    "susano-fivem": "fivem/susano-fivem",

    # Rust
    "disconnect": "rust/disconnect-rust-or",
    "disconnect rust": "rust/disconnect-rust-or",
    "disconnect-rust-or": "rust/disconnect-rust-or",

    # General
    "troubleshooting": "troubleshooting",
    "qb": "troubleshooting/sharing-qbs",
}

MAX_SUGGESTIONS = 25

async def product_autocomplete(interaction: discord.Interaction, current: str):
    current_lower = current.lower().strip()

    # show everything if they haven't typed yet (limited to 25)
    keys = list(DOCS.keys())

    if current_lower:
        keys = [k for k in keys if current_lower in k.lower()]

    keys.sort(key=lambda s: (len(s), s.lower()))
    keys = keys[:MAX_SUGGESTIONS]

    return [app_commands.Choice(name=k, value=k) for k in keys]


# Create a client + command tree (this is how slash commands work)
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=1427813707718590619)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


client = MyClient()

@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="/doc")
    )
    print(f"Logged in as {client.user}")

def slugify(text: str) -> str:
    """
    Turn "Widget Pro" into "widget-pro" for a clean URL.
    """
    t = text.strip().lower().replace("_", " ")
    t = re.sub(r"\s+", "-", t)          # spaces -> hyphen
    t = re.sub(r"[^a-z0-9\-]", "", t)   # remove unsafe chars
    return t

@client.tree.command(name="status", description="Show bot and service status.")
async def status(interaction: discord.Interaction):
    message = (
        "**✅ Service Status: Online**\n\n"
        "📘 Documentation: use `/doc <product>`\n"
        "🛒 Purchases & delivery are handled via Sellhub\n"
        "🆘 For help, open a support ticket or check the docs\n\n"
        "Bot is running normally."
    )

    await interaction.response.send_message(message)

REFUND_POLICY_URL = "https://zoomcheats.mysellauth.com/refund-policy"

@client.tree.command(name="refund", description="Get the refund policy link.")
async def refund(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Refund Policy: {REFUND_POLICY_URL}"
    )

def format_uptime(seconds: int) -> str:
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours}h {minutes}m {secs}s"
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


@client.tree.command(name="buy", description="Get the purchase link.")
async def buy(interaction: discord.Interaction):
    await interaction.response.send_message(f"🛒 Buy here: {BUY_URL}")


@client.tree.command(name="version", description="Show the bot version.")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(f"Bot version: **{BOT_VERSION}**")


@client.tree.command(name="uptime", description="Show how long the bot has been running.")
async def uptime(interaction: discord.Interaction):
    seconds = int(time.time() - START_TIME)
    await interaction.response.send_message(f"Uptime: **{format_uptime(seconds)}**")


@client.tree.command(name="faq", description="Frequently asked questions.")
async def faq(interaction: discord.Interaction):
    lines = [
        "**FAQ**",
        "",
        "• **How do I buy?** Use `/buy` (delivery is handled automatically after purchase).",
        "• **Where are the docs?** Use `/doc <product>`.",
        "• **Refunds?** Use `/refund`.",
        "• **Need help?** Ask in the support channel or open a ticket (if available).",
    ]
    if FAQ_URL:
        lines.append(f"\nMore: {FAQ_URL}")

    await interaction.response.send_message("\n".join(lines))


@client.tree.command(name="help", description="Show all available commands and links.")
async def help_cmd(interaction: discord.Interaction):
    lines = [
        "**Help / Commands**",
        "",
        "📘 `/doc <product>` — Get documentation link",
        "🛒 `/buy` — Purchase link",
        "🧾 `/refund` — Refund policy",
        "✅ `/status` — Service status",
        "⏱️ `/uptime` — Bot uptime",
        "🔖 `/version` — Bot version",
        "❓ `/faq` — Common questions",
    ]
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


@client.tree.command(name="doc", description="Get the GitBook doc link for a product.")
@app_commands.describe(productname="Pick a product")
@app_commands.autocomplete(productname=product_autocomplete)
async def doc(interaction: discord.Interaction, productname: str):
    key = productname.strip().lower()

    # Use exact mapping when available; otherwise fallback to slugify
    path = DOCS.get(key) or slugify(productname)

    url = f"{GITBOOK_BASE}{path.lstrip('/')}"
    await interaction.response.send_message(url)

threading.Thread(target=start_web_server, daemon=True).start()
client.run(TOKEN)
