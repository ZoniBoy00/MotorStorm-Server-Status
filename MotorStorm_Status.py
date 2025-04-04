import discord
from discord.ext import tasks, commands
import requests
import re  # Regular expressions for parsing player names
from datetime import datetime, timezone
import asyncio
import os

# Replace with your actual bot token and channel ID
TOKEN = 'DISCORD_BOT_TOKEN_HERE'
CHANNEL_ID = CHANNEL_ID_HERE
MESSAGE_ID_FILE = "message_id.txt"  # File to store the last message ID

# Debug setting
DEBUG = False  # Set to False to disable debug messages

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

def parse_player_name(name):
    """
    Parse the player name by removing numeric prefixes and special characters.
    Example: "fffff7fb-ZoniBoy0" -> "ZoniBoy0"
    """
    # Use regex to extract the player name after optional prefix (e.g., numbers and hyphen)
    match = re.search(r'[^0-9\-]+', name)
    if match:
        # Return the full name starting from the matched part
        return name[match.start():].strip()  # Include the rest of the name
    return name.strip()  # Fallback: return the original name if no match is found

def fetch_server_data():
    try:
        # Fetch room data from the rooms API
        rooms_response = requests.get("https://api.psrewired.com/us/api/rooms?applicationId=21624")
        rooms_data = rooms_response.json()

        if DEBUG:
            print("Rooms API Response:", rooms_data)  # Debug print

        # Fetch all players from the universes API
        players_response = requests.get("https://api.psrewired.com/us/api/universes/players?applicationId=21624")
        players_data = players_response.json()
        all_players = [parse_player_name(player['name']) for player in players_data]

        if DEBUG:
            print("Players API Response:", players_data)  # Debug print

        # Extract lobbies information
        lobbies = []
        remaining_players = all_players[:]  # Copy of all players for distribution

        for room in rooms_data:
            room_id = room.get('id')
            room_name = room.get('name', 'Unknown Lobby')  # Default name from /rooms endpoint
            player_count = room.get('playerCount', 0)
            max_players = room.get('maxPlayers', 12)

            # Fetch player data for this specific room
            room_players_response = requests.get(f"https://api.psrewired.com/us/api/rooms/{room_id}")
            room_players_data = room_players_response.json()

            if DEBUG:
                print(f"Room {room_name} Players API Response:", room_players_data)  # Debug print

            # Update room name from /rooms/{roomId} endpoint
            if isinstance(room_players_data, list) and len(room_players_data) > 0:
                room_name = room_players_data[0].get('name', room_name)  # Use the updated name if available
            elif isinstance(room_players_data, dict):
                room_name = room_players_data.get('name', room_name)

            # Handle different response formats (list or dictionary)
            players = []
            if isinstance(room_players_data, list):  # If the response is a list
                for item in room_players_data:
                    if 'players' in item:
                        players.extend([parse_player_name(player['name']) for player in item['players'] if 'name' in player])
            elif isinstance(room_players_data, dict):  # If the response is a dictionary
                players = [parse_player_name(player['name']) for player in room_players_data.get('players', []) if 'name' in player]

            # Remove these players from the remaining_players list
            for player in players:
                if player in remaining_players:
                    remaining_players.remove(player)

            # Adjust playerCount if there's a mismatch
            if not players and player_count > 0:
                if DEBUG:
                    print(f"⚠️ Warning: Lobby '{room_name}' has playerCount={player_count}, but no players found in /rooms/{room_id}. Adjusting playerCount to 0.")
                player_count = 0  # Override incorrect playerCount

            lobby_info = {
                "name": room_name,  # Use the updated room name here
                "player_count": player_count,
                "max_players": max_players,
                "players": players,
                "is_active": player_count > 0
            }

            lobbies.append(lobby_info)

        # General lobby: Pacific Rift US (remaining players)
        total_player_count = sum(room.get('playerCount', 0) for room in rooms_data)
        active_lobbies = sum(1 for room in rooms_data if room.get('playerCount', 0) > 0)

        return {
            "general_lobby": {
                "name": "Pacific Rift US",
                "player_count": total_player_count,
                "players": remaining_players  # Remaining players not in specific lobbies
            },
            "lobbies": lobbies,
            "summary": {
                "active_lobbies": active_lobbies,
                "total_players": total_player_count
            }
        }
    except Exception as e:
        if DEBUG:
            print(f"Error fetching server data: {e}")
        return None

def format_embed(data):
    embed = discord.Embed(
        title="🎮 **MotorStorm Server Status**",
        description="Real-time status of all lobbies and players.",
        color=discord.Color.green(),
        timestamp=datetime.now(timezone.utc)  # Use timezone-aware timestamp
    )

    # Summary Section
    summary = data["summary"]
    embed.add_field(
        name="📊 **Server Summary**",
        value=(
            f"**Active Lobbies:** `{summary['active_lobbies']}`\n"
            f"**Total Players Online:** `{summary['total_players']}`"
        ),
        inline=False
    )

    # Add General Lobby Information (Pacific Rift US)
    general_lobby = data["general_lobby"]
    embed.add_field(
        name=f"🌐 **{general_lobby['name']}**",
        value=(
            f"**Players Online:** `{general_lobby['player_count']}`\n"
            f"**Players:** `{', '.join(general_lobby['players']) if general_lobby['players'] else 'No players online'}`"
        ),
        inline=False
    )

    # Add Match Lobby Information
    for lobby in data["lobbies"]:
        if not lobby["is_active"]:  # Skip inactive lobbies
            continue

        lobby_name = lobby["name"]
        player_count = lobby["player_count"]
        max_players = lobby["max_players"]
        players = lobby["players"]

        # Determine the player status message
        if player_count > 0 and not players:
            player_status = "Player is joining..."
        elif players:
            player_status = ", ".join(players)
        else:
            player_status = "No players online"

        # Add field for each active match lobby
        embed.add_field(
            name=f"🏠 **{lobby_name}**",  # Use the real lobby name here
            value=(
                f"**Players Online:** `{player_count}/{max_players}`\n"
                f"**Players:** `{player_status}`"
            ),
            inline=False
        )

    # Footer with timestamp
    embed.set_footer(text="Last Updated")

    return embed

@bot.event
async def on_ready():
    if DEBUG:
        print(f"Bot is online: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Monitoring MotorStorm server..."))
    check_server_status.start()

async def get_or_create_message(channel):
    """Fetch the last message ID from the file or create a new message."""
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as file:
            try:
                message_id = int(file.read().strip())
                message = await channel.fetch_message(message_id)
                return message
            except (ValueError, discord.NotFound, discord.HTTPException):
                pass  # Ignore invalid or missing message IDs

    # Create a new message if no valid message ID exists
    message = await channel.send(embed=format_embed(fetch_server_data()))
    with open(MESSAGE_ID_FILE, "w") as file:
        file.write(str(message.id))
    return message

@tasks.loop(seconds=10)  # Update status every 10 seconds
async def check_server_status():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        if DEBUG:
            print("Channel not found.")
        return

    data = fetch_server_data()
    if not data:
        return

    message = await get_or_create_message(channel)
    embed = format_embed(data)
    await message.edit(embed=embed)
    print("🔔 Status updated.")

@bot.command()
async def status(ctx):
    """Manually request the server status."""
    data = fetch_server_data()
    if data:
        embed = format_embed(data)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Failed to fetch server status.")

bot.run(TOKEN)