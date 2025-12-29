import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from flask import Flask
from threading import Thread
import os, time, re, traceback

# ========================= AYARLAR =========================
TOKEN = os.getenv("TOKEN")  # Replit Secrets kullan: TOKEN=MTQ1NTE5NTExMjYyNjg1MTk4Mw.GESajs.1Ok1Qn0L8xHrJKFXyLsJtqkM6fwxrO_Rl6FG9w

SUNUCU_ID = 1443324563919474802
DUYURU_KANAL_ID = 1443325887671173335

TICKET_KATEGORI_ID = 1443325887671173335
YETKILI_ROL_ID = 1448250971862859868

# Küfür listesi ve link regex
kufurler = ["orospu cocugu","piç","yarrak","sik","ananı","bacını","ibne"]
link_regex = re.compile(r"(https?://|www\.)")
# ============================================================

# ---------- Flask ile uptime ping ----------
app = Flask("")
@app.route("/")
def home():
    return "Bot aktif"
def run():
    app.run(host="0.0.0.0", port=8080)
Thread(target=run).start()
# -------------------------------------------

# ---------- BOT TANIMI ----------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

START_TIME = time.time()  # uptime için
# --------------------------------

# ---------- READY ----------
@bot.event
async def on_ready():
    try:
        for g in bot.guilds:
            if g.id != SUNUCU_ID:
                await g.leave()
        await tree.sync()
        print(f"[READY] {bot.user}")
    except Exception as e:
        print("[READY ERROR]", e)
# -----------------------------

# ---------- GLOBAL ERROR ----------
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"[ERROR] {event}")
    traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    print("[COMMAND ERROR]", error)
# ---------------------------------

# ---------- MESAJ İŞLEME ----------
@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        msg = message.content.lower()

        # Selamlaşma
        if msg in ["sa","slm","selam","selamın aleyküm","selamin aleykum"]:
            await message.channel.send("Aleyküm selam 👋")

        # Link sil
        if link_regex.search(msg):
            await message.delete()
            return

        # Küfür sil (istisnalar olabilir)
        for k in kufurler:
            if k in msg:
                await message.delete()
                return

        await bot.process_commands(message)
    except Exception as e:
        print("[MESSAGE ERROR]", e)
# ---------------------------------

# ---------- ÜYE GİRİŞİ ----------
@bot.event
async def on_member_join(member):
    try:
        if member.guild.system_channel:
            await member.guild.system_channel.send(
                f"🎉 Ailemize hoşgeldin {member.mention}"
            )
    except:
        pass
# ---------------------------------

# ---------- YAYIN KOMUTU ----------
@tree.command(name="yayinbasla")
async def yayinbasla(interaction: discord.Interaction):
    try:
        kanal = bot.get_channel(1443325887671173335)
        if kanal:
            await kanal.send("@everyone 🔴 Yayın başladı!")
        await interaction.response.send_message("Duyuru atıldı", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message("Hata oluştu", ephemeral=True)
        print("[YAYIN ERROR]", e)
# ---------------------------------

# ---------- TEMİZLE KOMUTU ----------
@tree.command(name="sil")
async def sil(interaction: discord.Interaction, miktar: int):
    try:
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("Yetkin yok", ephemeral=True)
        if 1 <= miktar <= 100:
            await interaction.channel.purge(limit=miktar)
            await interaction.response.send_message("Silindi", ephemeral=True)
    except Exception as e:
        print("[SIL ERROR]", e)
# ---------------------------------

# ---------- TICKET SISTEMI ----------
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ticket Aç", style=discord.ButtonStyle.green)
    async def open(self, interaction: discord.Interaction, button: Button):
        try:
            guild = interaction.guild
            user = interaction.user
            kategori = guild.get_channel(TICKET_KATEGORI_ID)
            yetkili = guild.get_role(YETKILI_ROL_ID)

            kanal = await guild.create_text_channel(
                f"ticket-{user.name}",
                category=kategori,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    user: discord.PermissionOverwrite(view_channel=True),
                    yetkili: discord.PermissionOverwrite(view_channel=True)
                }
            )

            await kanal.send(f"{user.mention} ticket açıldı")

            close = Button(label="❌ Kapat", style=discord.ButtonStyle.red)

            async def close_cb(i):
                if i.user == user or yetkili in i.user.roles:
                    await kanal.delete()

            close.callback = close_cb
            v = View()
            v.add_item(close)
            await kanal.send("Ticketi kapat:", view=v)

            await interaction.response.send_message(
                f"Ticket açıldı: {kanal.mention}", ephemeral=True
            )
        except Exception as e:
            print("[TICKET ERROR]", e)

@bot.command()
async def ticketpanel(ctx):
    try:
        await ctx.send("🎫 Ticket Sistemi", view=TicketView())
    except:
        pass
# ---------------------------------

# ---------- UPTIME KOMUTU ----------
@tree.command(name="uptime", description="Bot ne kadar süredir açık")
async def uptime(interaction: discord.Interaction):
    sure = int(time.time() - START_TIME)
    gun = sure // 86400
    saat = (sure % 86400) // 3600
    dk = (sure % 3600) // 60
    await interaction.response.send_message(
        f"⏱ Bot açık süresi: {gun} gün {saat} saat {dk} dakika",
        ephemeral=True
    )
# ---------------------------------

# ---------- BOTU BAŞLAT ----------
try:
    bot.run(MTQ1NTE5NTExMjYyNjg1MTk4Mw.GESajs.1Ok1Qn0L8xHrJKFXyLsJtqkM6fwxrO_Rl6FG9w)
except Exception as e:
    print("[BOT CRASH]", e)
