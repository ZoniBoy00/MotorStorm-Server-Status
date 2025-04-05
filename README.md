# 🎮 MotorStorm Server Status Bot

A Discord bot that monitors the status of the **MotorStorm** server and provides **real-time updates** about active lobbies, players, and general server information using data from the **PS Rewired API**.

---

## 🚀 Features

- 🔄 **Real-Time Updates**: Automatically updates server status every 10 seconds.
- 👥 **Active Lobbies**: Displays info about active lobbies, including player count and names.
- 🌐 **General Lobby Support**: Shows players not assigned to specific lobbies.
- 💬 **Command Support**: Use `!status` to manually request the latest status.
- 📌 **Persistent Message**: Edits a single message in a channel instead of spamming new ones.

---

## 🖼️ Screenshots

![Status](https://github.com/ZoniBoy00/MotorStorm-Server-Status/blob/main/screenshot/status.png)

---

## 📋 Prerequisites

Make sure you have the following before running the bot:

- 🐍 **Python 3.8 or higher**
- 🤖 **Discord Bot Token** (from [Discord Developer Portal](https://discord.com/developers/applications))
- 🔢 **Channel ID** (Discord channel where the bot posts updates)
- 🔌 **Access to PS Rewired API**

---

## 🛠 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/ZoniBoy00/MotorStorm-Server-Status.git
cd MotorStorm-Server-Status
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Open MotorStorm_Status.py** in the project and add your token and channel ID:

```
TOKEN=DISCORD_BOT_TOKEN_HERE
CHANNEL_ID=YOUR_CHANNEL_ID_HERE
```

4. **Run the bot:**

```bash
python MotorStorm_Status.py
```

---

## ⚙️ Configuration

### Environment Variables

| Variable   | Description                              |
|------------|------------------------------------------|
| `TOKEN`    | Your Discord bot token                   |
| `CHANNEL_ID` | Discord channel ID to post updates in |

### Debug Mode

Enable debug logs by setting the following in the script:

```python
DEBUG = True
```

This will output API responses and other debug info to the console.

---

## 💡 Usage

### 🔁 Automatic Updates

Once running, the bot will update the server status every 10 seconds and keep **one persistent message** updated in the configured Discord channel.

### 🧾 Manual Status Check

Type `!status` in any channel where the bot has permission:

```plaintext
!status
```

It will reply with the current server status in an embed format.

---

## 📊 Example Output

**Embed Title:**
> 🎮 MotorStorm Server Status

**Description:**
> Real-time status of all lobbies and players.

**Embed Fields Example:**
```
📊 Server Summary  
Active Lobbies: 2  
Total Players Online: 3

🌐 Pacific Rift US  
Players Online: 3  
Players: Player1, Player2, Player3

🏠 Lobby1  
Players Online: 2/12  
Players: Player1, Player2

🏠 Lobby2  
Players Online: 1/12  
Players: Player3

🏠 Lobby3  
Players Online: 0/12  
Players: No players online
```

**Footer:**
> Last Updated: [timestamp]

---

## 🛠 Troubleshooting

- ❌ **Bot Not Responding**: Make sure it has permission to read/send messages.
- 🧱 **Missing Data**: Check the API endpoint responses.
- 🐞 **Error Logs**: Enable `DEBUG = True` to see logs in the terminal.

---

## 🤝 Contributing

Pull requests are welcome! Feel free to fork the repo and submit issues or new features.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/ZoniBoy00/MotorStorm-Server-Status/blob/main/LICENSE) file for more info.
