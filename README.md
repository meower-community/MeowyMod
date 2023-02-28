# MeowyMod
Source code for the Meower Administrative robot, "MeowyMod". A tool to replace the aging Meower Vanilla moderator functionality.

(Formerly known as "DuckWithBanHammerBot". *Yes, that was indeed the original name. Please don't ask why.*)

> **Note**
>
> MeowyMod is intended for use with Meower moderators and administrators.

# 💡 Features 💡
### 👨‍💻 Friendly commands
Simply @MeowyMod in Meower to utilize the bot. Commands are listed below, or can be accessed by using `@MeowyMod help`.

### 🪶 Fast and lightweight 
MeowyMod can run on minimal resources. At least 32MB of RAM and any reasonably capable CPU can run MeowyMod.

### 📃 Feature-Rich
* Ability to update
* Ability to self-restart
* Create announcements and warnings
* User promotion/demotion
* Supports account kicks/bans/pardons, as well as IP bans/pardons.
* Ticket logging
* Announcements
* **Missing features:** Reports management

> **Note**
>
> main.py can be updated using the `@MeowyBot update` command, but the MeowerBot library will require manual updates.

# 📦 Dependencies 📦
* 🐍 Python >=3.11
* 🤖 MeowerBot.py >=2.4.5 (Built-in)
* 🗂️ PyMongo
* 🗄 dotenv
* 🌐 CloudLink 3 Client (Component of MeowerBot.py)

# ⌨ Commands ⌨
* `@MeowyMod help` - Displays a list of commands.
* `@MeowyMod meow` - MeowyMod will Meow, because it is indeed a Cat.
* `@MeowyMod update` - Checks and applies new updates to the bot.
* `@MeowyMod kick (username)` - Disconnects a user from Meower.
* `@MeowyMod ban (username)` - Bans a user from Meower.
* `@MeowyMod pardon (username)` - Pardons a ban for a user on Meower.
* `@MeowyMod ipban (username)` - Blocks the IP address of a user on Meower.
* `@MeowyMod ippardon (username)` - Pardons blocked IP addresses for a user on Meower.
* `@MeowyMod announce (announcement)` - Creates a Meower-wide announcement.
* `@MeowyMod warn (username) (message)` - Sends a warning message to a user's inbox on Meower.
