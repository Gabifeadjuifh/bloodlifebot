import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import random 
from typing import List
from datetime import datetime

# --- CONFIGURARE SECRETE ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') 

# --- CONFIGURARE ID-URI IMPORTANTE (LOGGING) ---
MEMBER_LOG_CHANNEL_ID = 1445515601945559261
SERVER_LOG_CHANNEL_ID = 1445515628726321263
VOICE_LOG_CHANNEL_ID = 1445515654496260116
MESSAGE_LOG_CHANNEL_ID = 1445515670300397671
JOIN_LEAVE_LOG_CHANNEL_ID = 1445515700906098698

# --- CONFIGURARE ID-URI IMPORTANTE (TICKETING) ---
# ID-urile pentru categoriile de tichete
PROBLEME_CATEGORY_ID = 1444742100708098058 
CERERE_CATEGORY_ID = 1445024980285915136
RECLAMATII_CATEGORY_ID = 1445025023072141362

STAFF_ROLE_ID = 1434121191680905236 
TICKET_CHANNEL_ID = 1433835527702053006
TICKET_LOG_CHANNEL_ID = 1434083287026110614 
TICKET_CLOSE_ROLE_ID = 1381191256281059468 
TICKET_CLAIM_ROLE_ID = 1433835098310049892 

# --- CONFIGURARE ID-URI IMPORTANTE (VERIFICARE) ---
VERIFY_CHANNEL_ID = 1444745553853546680
VERIFIED_ROLE_ID = 1433835204807491635

# --- CONFIGURARE ID-URI IMPORTANTE (APLICAȚII STAFF) ---
# !!! IMPORTANT: Asigură-te că aceste ID-uri sunt corecte !!!
APPLICATION_CHANNEL_ID = 1433946132991574047  # Canalul unde se află mesajul cu butonul "Aplică acum"
APPLICATION_REVIEW_CHANNEL_ID = 1444809791355748474 # Canalul unde Staff-ul va revizui aplicațiile
STAFF_APPLICANT_ROLE_ID = 1433835122045485168 # Gradul care se va da la acceptare

# --- CONFIGURARE ID-URI IMPORTANTE (NUMAR MEMBRI) ---
# IMPORTANT: Asigură-te că acest ID este al unui CANAL DE VOCE acum!
MEMBER_COUNT_CHANNEL_ID = 1445522726423892199

# --- LISTA PENTRU A URMĂRI APLICANȚII ACTIVI ---
pending_applicants = set()

# --- CONFIGURARE INTENȚII ȘI BOT ---
intents = discord.Intents.all() 
bot = commands.Bot(command_prefix='!', intents=intents)

# --- FUNCȚIA PENTRU ACTUALIZAREA NUMĂRULUI DE MEMBRI (VARIANTA VOICE) ---
async def update_member_count(guild: discord.Guild):
    """Actualizează numele unui canal de voce cu numărul total de membri (fără boti)."""
    try:
        channel = guild.get_channel(MEMBER_COUNT_CHANNEL_ID)
        
        if not channel:
            print(f"❌ Eroare: Canalul {MEMBER_COUNT_CHANNEL_ID} nu a fost găsit.")
            return
        
        # Verificăm dacă este canal de voce (VoiceChannel)
        if not isinstance(channel, discord.VoiceChannel):
            print(f"⚠️ Atenție: Canalul {MEMBER_COUNT_CHANNEL_ID} NU este un canal de voce. Te rog să creezi unul de voce!")
            return

        # Numărăm membrii reali
        member_count = sum(1 for member in guild.members if not member.bot)
        new_name = f"📌・ᴍᴇᴍʙʀɪɪ : {member_count}"

        # Edităm numele canalului doar dacă este diferit
        # (Discord limitează schimbarea numelui canalelor la 2 ori / 10 minute)
        if channel.name != new_name:
            await channel.edit(name=new_name)
            print(f"✅ Nume canal actualizat: {new_name}")

    except discord.Forbidden:
        print(f"🚫 Eroare: Bot-ul nu are permisiunea 'Manage Channels' pentru a edita canalul {MEMBER_COUNT_CHANNEL_ID}.")
    except Exception as e:
        print(f"❌ A apărut o eroare la update_member_count: {e}")


# --- LISTA CU TOATE REGULILE TALE ---
ALL_RULES = [
    # ... (lista ta de reguli rămâne neschimbată)
    "1.01 - Termenul 'Roleplay': Simularea vietii reale prin intermediul unui joc.",
    "1.02 - Termenul 'In-Character': Persoana prin care te indentifici in Roleplay.",
    "1.03 - Termenul 'Out-of-Character': Lucrurile care sunt inafara Roleplay-ului.",
    "1.04 - Termenul 'Power-Gaming': Intamplari RP Supranaturale sau cand nu se ofera sanse egale. (Ex: Faci accident și te comporți normal.)",
    "1.05 - Termenul 'MetaGaming': Folosirea unei informații 'OOC' în 'IC' pentru un avantaj. (Ex: Chemi pe cineva pe Discord să te ajute la spital.)",
    "1.06 - Termenul 'Mixing': Transmiterea informațiilor 'IC' pe un canal 'OOC' sau invers. (Ex: Scrii pe chat-ul global să te ia cineva de la un anumit Cod Postal.)",
    "1.07 - Termenul 'Non-Fear Roleplay': Nu se simulează Frica într-un RP. (Ex: Cineva are arma pe tine și tu îl iei la pumni.)",
    "1.08 - Termenul 'Deathmatch': Atacarea/uciderea unei persoane fără un motiv bine intemeiat (Non-RP).",
    "1.09 - Termenul 'Random Deathmatch': Atacarea/uciderea unei persoane fără a fi avut un RP cu persoana respectivă.",
    "1.10 - Termenul 'Vehicle Deathmatch': Lovirea/uciderea unei persoane cu un autovehicul intenționat.",
    "1.11 - Termenul 'Fail Roleplay': Nu te poți adapta la o acțiune RP. (Ex: Fugărit de cineva și te duci în Safezone.)",
    "1.12 - Termenul 'Trolling': Nu ai dispoziția de a lua parte la un Roleplay și vrei să strici dispoziția altor jucători.",
    "1.13 - Termenul 'Cop Fear': Incapacitatea de a simula frica de un organ de poliție, amendă sau pușcărie.",
    "1.14 - Termenul 'Provoking': Provocarea unei persoane cu scopul de a o enerva pentru propriul amuzament.",
    "1.15 - Termenul 'Cop Bait': Provocarea unui polițist pentru a te fugări pentru propriul amuzament. (Ex: Faci burnout-uri în fața lor.)",
    "1.16 - Termenul 'Ninja Jack': Furtul uni autovehicul fără a aștepta min. 30 de secunde și fără a rula acțiunile în /me.",
    "1.17 - Termenul 'Rob & Kill': Uciderea unei persoane după ce ai jefuit-o.",
    "1.18 - Termenul 'Kill & Rob': Jefuirea unei persoane după ce ai omorât-o.",
    "1.19 - Termenul 'Revenge Kill': Căutarea unei persoane care te-a omorât într-un Roleplay în scopul de a te răzbuna.",
    "1.20 - Termenul 'Car Ram': Când doi sau mai mulți jucători își lovesc mașinile reciproc pentru propriul amuzament.",
    "1.21 - Termenul 'Condus Non-Roleplay': Condusul nerealistic. (Ex: Conducerea cu viteze exagerat de mari în oraș.)",
    "1.22 - Termenul 'Ghost Peek': Trasul dintr-o poziție de cover, fără a te arăta.",
    "1.23 - Termenul 'Olympic Swim': Înotatul la nesfârșit fără a obosi.",
    "1.24 - Termenul 'Chicken Run': Alergatul în zig-zag pentru a te feri de gloanțe.",
    "1.25 - Termenul 'Fake Mafia': Gruparea de peste 2 jucători care fac ilegalități (fără a fi mafie oficială).",
    "1.26 - Termenul 'Fake Cop / Medic / Sindicat': Când te dai drept Polițist / Medic / Sindicat.",
    "1.27 - Termenul 'Comportament de Bombardier': Când injuri oamenii fără un motiv bine întemeiat, stricând atmosfera.",
    "1.28 - Termenul 'Refuz Roleplay': Refuzarea de a întreține un Roleplay cu un jucător. (Ex: Nu accepți o percheziție.)",
    "1.29 - Termenul 'Player Kill (PK)': Uciderea unui jucător. Acesta trebuie să uite toate informațiile din ultimul RP.",
    "1.30 - Termenul 'Character Kill (CK)': Uciderea definitivă a personajului. Se pierd toate bunurile și orele. Trebuie să creezi un alt personaj.",
    "1.31 - Termenul 'Roleplay Scârbos': O acțiune greșită și scârboasă (Ex: Abuz Sexual, Canibalism). Interzis fără acordul ambilor jucători.",
    "1.32 - Termenul 'Fake Roleplay': O persoană are genul pe joc opus celui din viața reală.",
    "1.33 - Termenul 'Scam': Nerespectarea unei înțelegeri cu o persoană.",
    "1.34 - Termenul 'Stream Snipe': Când te duci la locația unui Streamer pe server ca să îi strici experiența.",
    "2.01 - Termenul 'Ticket in Roleplay': Crearea unui Ticket într-o situație RP pentru ajutor Staff.",
    "2.02 - Termenul 'Post-Hunt': Reclamațiile, sesizările sau acuzările nefondate.",
    "2.03 - Stricarea Economiei: Când cineva strică economia server-ului prin a da lucruri gratis sau mult mai ieftin (se sancționează cu Ban Permanent).",
    "2.04 - Suferințe OOC: Strict interzise. Limbajul trebuie să fie decent (Injurăturile sunt permise doar IC cu limită).",
    "2.05 - Trading cu Bani Reali: Trading-ul cu Bani Reali pentru iteme, conturi etc. este strict interzis.",
    "3.01 - Mafii: Este complet interzis să faceți mișto de un membru Sindicat sau Hitman.",
    "3.02 - Mafii: Nu aveți voie să vă aliați cu civili.",
    "3.03 - Mafii: Săgețile nu au voie cu arme, să vină la ședințe Sindicat, să se certe cu alți mafioți, etc.",
    "3.04 - Mafii: Ca mafiot nu aveți voie să trageți în Sindicat sau Hitman.",
    "3.05 - Mafii: Nu aveți voie să faceți pact de înțelegere cu jefuitori indiferent de relația OOC.",
    "3.06 - Mafii: Ca mafiot sunteți obligat să faceți task-ul săptămânal.",
    "3.07 - Mafii: Este complet interzis să vă bateți pe turf-ul altei mafii."
]

# --- CLASELE VECHI (VerifyView, TicketClaimCloseView, TicketCreationView) rămân neschimbate ---
class VerifyView(discord.ui.View):
    def __init__(self, bot_instance):
        super().__init__(timeout=None)
        self.verified_role_id = VERIFIED_ROLE_ID
        self.bot = bot_instance
    @discord.ui.button(label="Confirma identitatea", style=discord.ButtonStyle.green, custom_id="verify:confirm", emoji="🛡️")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user; role_id = self.verified_role_id; guild = interaction.guild; role = guild.get_role(role_id)
        if not role: await interaction.response.send_message("❌ Eroare: Rolul de verificare nu a fost găsit.", ephemeral=True); return
        if role in user.roles: await interaction.response.send_message("✅ Ai deja acces.", ephemeral=True); return
        try: await user.add_roles(role, reason="Verificare"); await interaction.response.send_message("✅ Verificare reușită!", ephemeral=True)
        except Exception as e: await interaction.response.send_message(f"❌ Eroare: {e}", ephemeral=True)

class TicketClaimCloseView(discord.ui.View):
    def __init__(self, user_id): super().__init__(timeout=None); self.user_id = user_id; self.close_role_id = TICKET_CLOSE_ROLE_ID; self.claim_role_id = TICKET_CLAIM_ROLE_ID; self.claimed = False
    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.secondary, custom_id="ticket:claim", emoji="📄")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_allowed_role = any(role.id == self.claim_role_id for role in interaction.user.roles)
        if not is_allowed_role: await interaction.response.send_message("❌ Nu ai permisiunea.", ephemeral=True); return
        if self.claimed: await interaction.response.send_message("⚠️ Tichet preluat.", ephemeral=True); return
        self.claimed = True; await interaction.response.send_message(f"✅ Preluat de {interaction.user.mention}.", ephemeral=False)
        button.disabled = True; button.label = f"Preluat de {interaction.user.name}"; button.style = discord.ButtonStyle.green; await interaction.message.edit(view=self)
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="ticket:close", emoji="🔒")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_allowed_role = any(role.id == self.close_role_id for role in interaction.user.roles); is_ticket_creator = interaction.user.id == self.user_id
        if not is_allowed_role and not is_ticket_creator: await interaction.response.send_message("❌ Nu ai permisiunea.", ephemeral=True); return
        await interaction.response.send_message("Se închide...", ephemeral=False); await interaction.channel.delete(reason=f"Închis de {interaction.user.name}")

class TicketCreationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # ID-urile rolurilor și ale canalelor de log rămân
        self.staff_role_id = STAFF_ROLE_ID
        self.ticket_close_role_id = TICKET_CLOSE_ROLE_ID
        self.ticket_log_channel_id = TICKET_LOG_CHANNEL_ID

    async def create_ticket_channel(self, interaction: discord.Interaction, topic_name: str, topic_desc: str, ticket_type: str, category_id: int):
        user = interaction.user
        guild = interaction.guild
        
        # Obținem categoria specifică pentru acest tip de tichet
        category = guild.get_channel(category_id)
        staff_role_to_view = guild.get_role(self.staff_role_id)
        log_channel = guild.get_channel(self.ticket_log_channel_id)

        if not category:
            await interaction.response.send_message("❌ Eroare: Categoria de tichete nu a fost găsită.", ephemeral=True)
            return

        # Verificăm dacă utilizatorul are deja un tichet deschis în oricare dintre categoriile de tichete
        categories_to_check_ids = [PROBLEME_CATEGORY_ID, CERERE_CATEGORY_ID, RECLAMATII_CATEGORY_ID]
        for cat_id in categories_to_check_ids:
            cat = guild.get_channel(cat_id)
            if cat:
                for channel in cat.channels:
                    permissions = channel.permissions_for(user)
                    if permissions.read_messages:
                        await interaction.response.send_message("❌ Ai deja un tichet deschis.", ephemeral=True)
                        return

        # Mapăm tipul de tichet la un prefix pentru numele canalului
        prefix_map = {
            "tehnic": "probleme",
            "unban": "cerere",
            "reclamatii": "reclamatii"
        }
        prefix = prefix_map.get(ticket_type, "ticket") # Folosim un prefix implicit în caz de eroare
        
        # Creăm numele canalului folosind prefixul și numele utilizatorului
        channel_name = f"{prefix}-{user.name}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
            staff_role_to_view: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)
        }
        
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites, topic=topic_desc)
        mention_role = guild.get_role(self.ticket_close_role_id)
        mention_text = mention_role.mention if mention_role else "Staff"
        welcome_message = f"Bine ai venit, **{user.mention}!**\nUn membru al {mention_text} va prelua cererea ta curând.\nSubiect: {topic_name}\n\n**Vă rugăm să copiați formularul de mai jos, să îl completați cu informațiile necesare și să îl trimiteți înapoi în acest canal.**"
        await ticket_channel.send(welcome_message, view=TicketClaimCloseView(user.id))
        templates = {"tehnic": "**Nume:**\n\n**Id:**\n\n**Descrierea problemei:**", "unban": "**Nume:**\n\n**Id:**\n\n**Motiv:**\n\n**Dovada(link):**", "reclamatii": "**Nume:**\n\n**Id:**\n\n**Id reclamat:**\n\n**Motiv:**\n\n**Dovada(link):**"}
        template_text = templates.get(ticket_type, "Template-ul nu a fost găsit."); await ticket_channel.send(template_text)
        if log_channel:
            embed = discord.Embed(title=f"🩸 Ticket nou: {topic_name}", description=f"Un tichet Bloodlife a fost creat cu succes la {ticket_channel.mention}!", color=discord.Color.red())
            embed.add_field(name="✍️ Nume", value=user.display_name, inline=True); embed.add_field(name="🆔 ID", value=user.id, inline=True); embed.add_field(name="💬 Descriere", value=topic_desc, inline=False); embed.set_footer(text=f"Creat de {user.display_name} | {user.id}"); await log_channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Tichetul tău Bloodlife a fost deschis: {ticket_channel.mention}", ephemeral=True)
    
    @discord.ui.button(label="Probleme Tehnice", style=discord.ButtonStyle.secondary, custom_id="ticket:tehnic", emoji="🛠️")
    async def tehnic_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "SUPORT TEHNIC", "Raportează o problemă cu jocul.", "tehnic", category_id=PROBLEME_CATEGORY_ID)

    @discord.ui.button(label="Cereri Unban", style=discord.ButtonStyle.secondary, custom_id="ticket:unban", emoji="🔓")
    async def unban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "CERERE UNBAN", "Solicită unban de pe server.", "unban", category_id=CERERE_CATEGORY_ID)

    @discord.ui.button(label="Reclamații Staff/Jucători", style=discord.ButtonStyle.secondary, custom_id="ticket:reclamatii", emoji="📢")
    async def reclamatii_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket_channel(interaction, "RECLAMAȚII", "Reclamă un jucător sau un membru Staff.", "reclamatii", category_id=RECLAMATII_CATEGORY_ID)

# --- Restul comenzilor rămâne neschimbat ---
@bot.tree.command(name="setup_verify", description="Generează mesajul de verificare/captcha pe canalul specificat.")
@commands.has_permissions(administrator=True)
async def setup_verify_command(interaction: discord.Interaction):
    channel = interaction.guild.get_channel(VERIFY_CHANNEL_ID)
    if not channel: return await interaction.response.send_message(f"❌ Eroare: Canalul {VERIFY_CHANNEL_ID} nu a fost găsit.", ephemeral=True)
    embed = discord.Embed(title="🔑 Deblochează restul canalelor", description="Salut! Pentru a accesa restul canalelor și a te bucura de tot ce oferim în **Bloodlife Roleplay**, apasă butonul de mai jos și confirmă că nu ești robot! 😎", color=discord.Color.dark_red())
    embed.add_field(name="📍 Bloodlife", value="Deblochează toate canalele")
    await channel.send(embed=embed, view=VerifyView(bot))
    await interaction.response.send_message(f"✅ Mesajul de verificare Bloodlife a fost trimis pe canalul {channel.mention}.", ephemeral=True)

@bot.tree.command(name="setup_tickets", description="Generează mesajul cu butoane pentru ticketing.")
@commands.has_permissions(administrator=True)
async def setup_tickets_command(interaction: discord.Interaction):
    channel = interaction.guild.get_channel(TICKET_CHANNEL_ID)
    if not channel: return await interaction.response.send_message(f"❌ Eroare: Canalul {TICKET_CHANNEL_ID} nu a fost găsit.", ephemeral=True)
    embed = discord.Embed(title="💉 BLOODLIFE SUPORT TICHETE 🆘", description="📌 Fa clic pe un buton în funcție de subiectul pe care dorești să îl discuți cu un membru staff.\n📌 Nu deschide un tichet fără motiv, riști să fii sancționat!", color=discord.Color.dark_red())
    await channel.send(embed=embed, view=TicketCreationView())
    await interaction.response.send_message(f"✅ Mesajul de ticketing Bloodlife a fost trimis pe canalul {channel.mention}.", ephemeral=True)
    
@bot.tree.command(name="test_staff", description="Generează un test de 30 de reguli de Roleplay pentru Staff.")
async def test_staff_command(interaction: discord.Interaction, target: discord.Member):
    staff_role = interaction.guild.get_role(STAFF_ROLE_ID); is_admin = interaction.user.guild_permissions.administrator; is_staff = staff_role and staff_role in interaction.user.roles
    if not (is_admin or is_staff): return await interaction.response.send_message("❌ Nu ai permisiunea.", ephemeral=True)
    await interaction.response.defer()
    if len(ALL_RULES) < 30: rules_to_send = ALL_RULES
    else: rules_to_send = random.sample(ALL_RULES, 30)
    output_part1 = f"# TEST STAFF pentru {target.name}\n\n## Partea I: Definiții (15 reguli)\n"
    for i, rule in enumerate(rules_to_send[:15]): output_part1 += f"**{i+1}.** {rule}\n"
    output_part2 = "## Partea a II-a: Definiții (Restul de 15 reguli)\n"
    for i, rule in enumerate(rules_to_send[15:30]): output_part2 += f"**{i+16}.** {rule}\n" 
    output_part3 = "\n---\n## Partea a III-a: Cazuri Practice (Creare & Analiză)\n"
    output_part3 += "**31. ** **Creează 4 scenarii de Roleplay complexe (câte unul pentru Power Gaming, Meta Gaming, Fail RP și Cop Bait) și explică ce greșeală a fost comisă și care este sancțiunea corespunzătoare.**\n"
    output_part3 += "**32. ** **Creează un scenariu în care un jucător poate primi Character Kill (CK) și explică de ce se aplică această regulă.**\n\nSucces la test!\n"
    output_part3 += f"\n{target.mention} <@&{STAFF_ROLE_ID}>\n"
    try:
        await interaction.channel.send(output_part1); await interaction.channel.send(output_part2); await interaction.channel.send(output_part3) 
        await interaction.followup.send("✅ Testul a fost generat.", ephemeral=True)
    except Exception as e: await interaction.followup.send(f"❌ Eroare: {e}", ephemeral=True)

# --- EVENTE PENTRU LOGGING ---

@bot.event
async def on_ready():
    print(f'✅ Bot-ul Bloodlife s-a conectat cu succes la Discord!')
    try: synced = await bot.tree.sync(); print(f"Comenzi Slash sincronizate: {len(synced)} comenzi.")
    except Exception as e: print(f"Eroare la sincronizarea comenzilor: {e}")
    
    # Actualizăm numărul de membri la pornire pentru toate serverele unde bot-ul este prezent
    for guild in bot.guilds:
        await update_member_count(guild)
        
    # Adăugăm view-urile pentru a face butoanele persistente
    bot.add_view(TicketCreationView())
    bot.add_view(VerifyView(bot))
    # Adăugăm o instanță generică a view-ului de revizuire pentru persistență

@bot.event
async def on_member_join(member: discord.Member):
    if member.bot: return 
    verify_channel = member.guild.get_channel(VERIFY_CHANNEL_ID)
    if verify_channel: await verify_channel.send(f"Bine ai venit, {member.mention}! Te rog, apasă butonul **'Confirma identitatea'** de mai sus pentru a debloca accesul.", delete_after=10)
    
    # Log pentru intrarea membrului
    log_channel = member.guild.get_channel(JOIN_LEAVE_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🟢 Membru Nou", description=f"{member.mention} s-a alăturat serverului.", color=discord.Color.green())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID Membru", value=member.id, inline=False)
        embed.set_footer(text=f"Cont creat la: {member.created_at.strftime('%d-%m-%Y %H:%M:%S')}")
        await log_channel.send(embed=embed)
    
    # Actualizăm numărul de membri
    await update_member_count(member.guild)

@bot.event
async def on_member_remove(member: discord.Member):
    # Log pentru ieșirea membrului
    log_channel = member.guild.get_channel(JOIN_LEAVE_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🔴 Membru Plecat", description=f"{member.mention} a părăsit serverul.", color=discord.Color.red())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID Membru", value=member.id, inline=False)
        embed.add_field(name="Nume", value=member.display_name, inline=False)
        await log_channel.send(embed=embed)
    
    # Actualizăm numărul de membri
    await update_member_count(member.guild)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    log_channel = before.guild.get_channel(MEMBER_LOG_CHANNEL_ID)
    if not log_channel:
        return

    # Log pentru actualizări de roluri
    if before.roles != after.roles:
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        
        if added_roles or removed_roles:
            embed = discord.Embed(title="🔄 Actualizare Roluri", description=f"Rolurile lui {after.mention} au fost modificate.", color=discord.Color.gold())
            embed.set_thumbnail(url=after.display_avatar.url)
            
            if added_roles:
                embed.add_field(name="Roluri Adăugate", value=", ".join([role.mention for role in added_roles]), inline=False)
            if removed_roles:
                embed.add_field(name="Roluri Eliminate", value=", ".join([role.mention for role in removed_roles]), inline=False)
            
            await log_channel.send(embed=embed)

    # Log pentru timeout
    if before.timed_out != after.timed_out:
        if after.timed_out:
            embed = discord.Embed(title="⏳ Membru Timeout", description=f"{after.mention} a primit timeout.", color=discord.Color.orange())
            embed.add_field(name="Până la", value=after.timed_out_until.strftime('%d-%m-%Y %H:%M:%S'), inline=False)
        else:
            embed = discord.Embed(title="✅ Timeout Eliminat", description=f"Timeout-ul lui {after.mention} a fost eliminat.", color=discord.Color.green())
        
        embed.set_thumbnail(url=after.display_avatar.url)
        await log_channel.send(embed=embed)

@bot.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    log_channel = guild.get_channel(MEMBER_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🚫 Membru Banat", description=f"{user.mention} a primit ban.", color=discord.Color.dark_red())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID Utilizator", value=user.id, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_member_unban(guild: discord.Guild, user: discord.User):
    log_channel = guild.get_channel(MEMBER_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="✅ Ban Eliminat", description=f"Ban-ul lui {user.mention} a fost eliminat.", color=discord.Color.green())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID Utilizator", value=user.id, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel: discord.abc.GuildChannel):
    log_channel = channel.guild.get_channel(SERVER_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="➕ Canal Creat", description=f"Canalul {channel.mention} a fost creat.", color=discord.Color.green())
        embed.add_field(name="Tip Canal", value=channel.type, inline=True)
        embed.add_field(name="ID Canal", value=channel.id, inline=True)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
    log_channel = channel.guild.get_channel(SERVER_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="➖ Canal Șters", description=f"Canalul `#{channel.name}` a fost șters.", color=discord.Color.red())
        embed.add_field(name="Tip Canal", value=channel.type, inline=True)
        embed.add_field(name="ID Canal", value=channel.id, inline=True)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_channel_update(before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
    log_channel = before.guild.get_channel(SERVER_LOG_CHANNEL_ID)
    if not log_channel:
        return

    changes = []
    # Verificarea numelui este validă pentru toate tipurile de canale
    if before.name != after.name:
        changes.append(f"Nume: `{before.name}` → `{after.name}`")
    
    # Verificarea topicului este validă DOAR pentru canalele de text
    if isinstance(before, discord.TextChannel) and before.topic != after.topic:
        changes.append(f"Topic: `{before.topic}` → `{after.topic}`")
    
    if changes:
        embed = discord.Embed(title="🔄 Canal Actualizat", description=f"Canalul {after.mention} a fost modificat.", color=discord.Color.gold())
        embed.set_thumbnail(url=after.guild.icon.url if after.guild.icon else None)
        for change in changes:
            embed.add_field(name="Modificare", value=change, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_create(role: discord.Role):
    log_channel = role.guild.get_channel(SERVER_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="➕ Rol Creat", description=f"Rolul {role.mention} a fost creat.", color=discord.Color.green())
        embed.add_field(name="ID Rol", value=role.id, inline=True)
        embed.add_field(name="Culoare", value=role.color, inline=True)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_delete(role: discord.Role):
    log_channel = role.guild.get_channel(SERVER_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="➖ Rol Șters", description=f"Rolul `@{role.name}` a fost șters.", color=discord.Color.red())
        embed.add_field(name="ID Rol", value=role.id, inline=True)
        embed.add_field(name="Culoare", value=role.color, inline=True)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_role_update(before: discord.Role, after: discord.Role):
    log_channel = before.guild.get_channel(SERVER_LOG_CHANNEL_ID)
    if not log_channel:
        return

    changes = []
    if before.name != after.name:
        changes.append(f"Nume: `{before.name}` → `{after.name}`")
    if before.color != after.color:
        changes.append(f"Culoare: `{before.color}` → `{after.color}`")
    if before.permissions.value != after.permissions.value:
        changes.append("Permisiuni modificate")
    
    if changes:
        embed = discord.Embed(title="🔄 Rol Actualizat", description=f"Rolul {after.mention} a fost modificat.", color=discord.Color.gold())
        for change in changes:
            embed.add_field(name="Modificare", value=change, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_update(before: discord.Guild, after: discord.Guild):
    log_channel = after.get_channel(SERVER_LOG_CHANNEL_ID)
    if not log_channel:
        return
    
    changes = []
    if before.name != after.name:
        changes.append(f"Nume Server: `{before.name}` → `{after.name}`")
    if before.icon != after.icon:
        changes.append("Iconița serverului a fost schimbată.")
    
    if changes:
        embed = discord.Embed(title="🔄 Server Actualizat", description=f"Serverul a fost modificat.", color=discord.Color.gold())
        embed.set_thumbnail(url=after.icon.url if after.icon else None)
        for change in changes:
            embed.add_field(name="Modificare", value=change, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_guild_emojis_update(guild: discord.Guild, before: list[discord.Emoji], after: list[discord.Emoji]):
    log_channel = guild.get_channel(SERVER_LOG_CHANNEL_ID)
    if not log_channel:
        return

    before_names = {emoji.name for emoji in before}
    after_names = {emoji.name for emoji in after}

    added_emojis = [emoji for emoji in after if emoji.name not in before_names]
    removed_emojis = [emoji for emoji in before if emoji.name not in after_names]

    if added_emojis or removed_emojis:
        embed = discord.Embed(title="🔄 Emoji-uri Actualizate", description="Lista de emoji-uri a serverului a fost modificată.", color=discord.Color.gold())
        if added_emojis:
            embed.add_field(name="Emoji-uri Adăugate", value=" ".join([str(emoji) for emoji in added_emojis]), inline=False)
        if removed_emojis:
            embed.add_field(name="Emoji-uri Eliminate", value=" ".join([f"`:{emoji.name}:`" for emoji in removed_emojis]), inline=False)
        
        await log_channel.send(embed=embed)

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    log_channel = member.guild.get_channel(VOICE_LOG_CHANNEL_ID)
    if not log_channel:
        return

    # Verificăm dacă membrul s-a mutat între canale (nu a intrat sau a ieșit)
    if before.channel and after.channel and before.channel != after.channel:
        embed = discord.Embed(title="🔊 Mutare Canal Vocal", description=f"{member.mention} s-a mutat.", color=discord.Color.blue())
        embed.add_field(name="De la", value=before.channel.mention, inline=True)
        embed.add_field(name="La", value=after.channel.mention, inline=True)
        await log_channel.send(embed=embed)

@bot.event
async def on_message_delete(message: discord.Message):
    # Ignorăm mesajele bot-urilor
    if message.author.bot:
        return

    log_channel = message.guild.get_channel(MESSAGE_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🗑️ Mesaj Șters", description=f"Un mesaj în {message.channel.mention} a fost șters.", color=discord.Color.red())
        embed.add_field(name="Autor", value=message.author.mention, inline=True)
        embed.add_field(name="ID Mesaj", value=message.id, inline=True)
        
        content = message.content
        if not content:
            if message.attachments:
                content = "Mesajul conținea un fișier/imagini."
            elif message.embeds:
                content = "Mesajul conținea un embed."
            else:
                content = "Mesajul nu avea conținut text."

        embed.add_field(name="Conținut", value=content[:1024] + "..." if len(content) > 1024 else content, inline=False)
        await log_channel.send(embed=embed)

@bot.event
async def on_bulk_message_delete(messages: list[discord.Message]):
    if not messages:
        return

    log_channel = messages[0].guild.get_channel(MESSAGE_LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(title="🗑️ Mesaje Șterse în Masă", description=f"**{len(messages)}** mesaje au fost șterse în {messages[0].channel.mention}.", color=discord.Color.dark_red())
        await log_channel.send(embed=embed)


if TOKEN:
    try: print("Încercarea de a rula bot-ul..."); bot.run(TOKEN)
    except Exception as e: print(f"\n--- EROARE CRITICĂ ---\nBot-ul nu a putut rula. Eroare: {e}\nVerifică intențiile privilegiate în Developer Portal.")
else: print("EROARE: Token-ul Discord nu a fost găsit.")