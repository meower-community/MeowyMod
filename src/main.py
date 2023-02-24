from dotenv import load_dotenv
import pymongo
import update_check as updater
from MeowerBot import Bot
import requests
import os
import time

# Version tracker
version = "1.1.2"

# Load environment keys
if not load_dotenv():
    print("Failed to load .env keys, exiting.")
    exit()

# Create instance of bot
meowyMod = Bot()

# Keep track of processing requests
tickets = dict()

# Prepare DB connection
print(f"Connecting to database \"{os.getenv('SERVER_DB', 'mongodb://localhost:27017')}\"...")
dbclient = pymongo.MongoClient(os.getenv("SERVER_DB", "mongodb://localhost:27017"))
meowerdb = None

# Check DB connection status
try:
    dbclient.server_info()
    print("Connected to database!")
    meowerdb = dbclient.meowerserver
except pymongo.errors.ServerSelectionTimeoutError as err:
    print(f"Failed to connect to database: \"{err}\"!")
    exit()


# DB methods
def getUserLevel(username):
    return meowerdb.usersv0.find_one({"_id": username})["lvl"]


def modifyUserLevel(username, newlevel):
    return (meowerdb.usersv0.update_one({"_id": username}, {"$set": {"lvl": newlevel}})).matched_count > 0


def isUserValid(username):
    if meowerdb.usersv0.find_one({"_id": username}):
        return True
    return False


# Restart script
def restart():
    print("Shutting down websocket")
    meowyMod.wss.stop()

    script = os.getenv("RESET_SCRIPT")
    print(f"Running reset script: {script}")
    os.system(script)

    print(f"MeowyMod {version} going away now...")
    exit()


# Shutdown script
def shutdown():
    print("Shutting down websocket")
    meowyMod.wss.stop()

    print(f"MeowyMod {version} going away now...")
    exit()


def registerNewTicket(ctx, username, method):
    ticketID = f"{method} {username} @{round(time.time())}"
    tickets[ticketID] = {
        "origin": ctx.user.username,
        "recipient": username
    }
    print(f"Creating new event ticket: \"{ticketID}\"")
    return ticketID


def resolveTicket(ticketID, status):
    if not ticketID in tickets:
        print(f"Invalid ticket ID \"{ticketID}\", exiting resolveTicket method")
    print(f"Ticket \"{ticketID}\" resolving with status {status}")
    meowyMod.send_msg(
        f"@{tickets[ticketID]['origin']} I have processed the request \"{ticketID}\" with result {status}!")
    del tickets[ticketID]


# Commands
@meowyMod.command(args=0, aname="meow")
def quack(ctx):
    ctx.send_msg("Meow!")


@meowyMod.command(args=0, aname="help")
def help(ctx):
    ctx.send_msg(
        " - help: this message.\n - meow: another fun message!\n - about: Learn a little about me!\n - setlevel (username) (user level)\n - kick (username)\n - ban (username)\n - ipban (username)\n - pardon (username)\n - ippardon (username)\n - update\n - shutdown\n - reboot")


@meowyMod.command(args=0, aname="about")
def about(ctx):
    ctx.send_msg(
        f"MeowyMod v{version} \nCreated by @MikeDEV, built using @ShowierData9978's MeowerBot.py library! \n\nI'm a little orange cat with a squeaky toy hammer, and I'm here to keep Meower a safer place! Better watch out, only Meower Mods, Admins, and Sysadmins can use me!\n\nYou can find my source code here: https://github.com/MeowerBots/MeowyMod")


@meowyMod.command(args=2, aname="setlevel")
def modifySecurityLevel(ctx, username, user_level):
    if getUserLevel(ctx.user.username) == 4:
        if username == "MikeDEV":
            ctx.send_msg(f"Sorry {ctx.user.username}, But for security reasons, I am not allowed to modify MikeDEV's permissions.")
            return
        
        if username == "MeowyMod":
            ctx.send_msg(f"Sorry {ctx.user.username}, I am not allowed to modify my own permissions.")
            return
        
        if not isUserValid(username):
            ctx.send_msg(f"Sorry {ctx.user.username}, I couldn't find the user \"{username}\", so I could not complete your request.")
            return
        
        if (user_level < 0) or (user_level > 4):
            ctx.send_msg(f"Sorry {ctx.user.username}, But the userlevel {user_level} is invalid, so I could not complete your request. \n\nValid user levels are: \n0 - Normal user, \n1 - Low-level Moderator (Kicks/bans/pardons), \n2 - Mid-level Moderator (IP kicks/bans/pardons), \n3 - High-Level moderator (Announcements), \n4 - Administrator.")
            return
        
        if (ctx.user.username != "MikeDEV") and (getUserLevel(username) == 4):
            ctx.send_msg(f"Sorry {ctx.user.username}, But for security reasons, You are not allowed to modify a Administrator's permissions. Only MikeDEV is permitted to modify a Administrator's permissions.")
            return
        
        if not modifyUserLevel(username, user_level):
            ctx.send_msg(f"Sorry {ctx.user.username}, something went wrong while I was modifying \"{username}\"'s user level. I was unable to complete your request.")
            return
        
        ctx.send_msg(f"{ctx.user.username}, I have updated \"{username}\"'s user level successfully!")
        
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"setlevel\" requires level 4 access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=1, aname="kick")
def kickUser(ctx, username):
    if getUserLevel(ctx.user.username) >= 1:
        if (username == "MikeDEV") and (not ctx.user.username == "MikeDEV"):
            ctx.send_msg(f"Sorry {ctx.user.username}, Nobody other than himself can disconnect him.")
            return
        
        if (username == "MeowyMod") and (not ctx.user.username == "MikeDEV"):
            ctx.send_msg(f"Sorry {ctx.user.username}, I will not disconnect myself.")
            return
        
        # Create new request ticket
        ticketID = registerNewTicket(ctx, username, "kick")

        meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "kick", "val": username}, "listener": ticketID})
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"kick\" requires level 1 or higher access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=1, aname="ban")
def banUser(ctx, username):
    if getUserLevel(ctx.user.username) >= 1:
        if username == "MikeDEV":
            ctx.send_msg(f"Sorry {ctx.user.username}, But for security reasons, I am not allowed to ban MikeDEV.")
            return
        
        if username == "MeowyMod":
            ctx.send_msg(f"Sorry {ctx.user.username}, I will not ban myself.")
            return
        
        # Create new request ticket
        ticketID = registerNewTicket(ctx, username, "ban")

        meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "ban", "val": username}, "listener": ticketID})
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"ban\" requires level 1 or higher access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=1, aname="ipban")
def ipBanUser(ctx, username):
    if getUserLevel(ctx.user.username) >= 2:
        if username == "MikeDEV":
            ctx.send_msg(f"Sorry {ctx.user.username}, But for security reasons, I am not allowed to IP ban MikeDEV.")
            return
        
        if username == "MeowyMod":
            ctx.send_msg(f"Sorry {ctx.user.username}, I will not IP ban myself.")
            return
        
        # Create new request ticket
        ticketID = registerNewTicket(ctx, username, "ipban")

        meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "block", "val": username}, "listener": ticketID})
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"ipban\" requires level 2 or higher access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=1, aname="pardon")
def pardonUser(ctx, username):
    if getUserLevel(ctx.user.username) >= 1:
        # Create new request ticket
        ticketID = registerNewTicket(ctx, username, "pardon")

        meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "pardon", "val": username}, "listener": ticketID})
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"pardon\" requires level 1 or higher access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=1, aname="ippardon")
def ipPardonUser(ctx, username):
    if getUserLevel(ctx.user.username) >= 2:
        # Create new request ticket
        ticketID = registerNewTicket(ctx, username, "ippardon")

        meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "unblock", "val": username}, "listener": ticketID})
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"ippardon\" requires level 2 or higher access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=0, aname="update")
def updateCheck(ctx):
    if getUserLevel(ctx.user.username) == 4:
        # Check for updates, but better(ish)
        versionHistory = requests.get("https://raw.githubusercontent.com/MeowerBots/MeowyMod/main/versionInfo.json").json()
        if version not in versionHistory["latest"] or version in versionHistory["old"]:
            ctx.send_msg(f"Looks like I'm out-of-date! Latest version(s) are {versionHistory['latest']} while I'm on {version}. Downloading updates...")
            time.sleep(1)
            updater.update(f"{os.getcwd()}/main.py", "https://raw.githubusercontent.com/MeowerBots/MeowyMod/main/src/main.py")
            ctx.send_msg("Rebooting to apply updates...")
            time.sleep(1)
            restart()
        else:
            ctx.send_msg(f"Looks like I'm up-to-date! Running v{version} right now.")
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"update\" requires level 4 access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=0, aname="reboot")
def rebootScript(ctx):
    if getUserLevel(ctx.user.username) == 4:
        ctx.send_msg("Oke! I'm rebooting now...")
        restart()
    else:
        ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}. The command \"reboot\" requires level 4 access, you only have level {getUserLevel(ctx.user.username)}.")


@meowyMod.command(args=0, aname="shutdown")
def shutdownScript(ctx):
    if ctx.user.username == "MikeDEV":
        ctx.send_msg("Goodbye! I'm shutting down now...")
        shutdown()
    else:
        ctx.send_msg(f"Sorry, the \"shutdown\" command is only allowed for MikeDEV.")


# Listener management
def listenerEventManager(post, bot):
    # Validate keys
    for key in ["cmd", "val", "listener"]:
        if key not in post:
            return

    # Handle listeners
    if post["cmd"] == "statuscode":
        if post["listener"] in tickets:
            resolveTicket(post["listener"], post["val"])
        elif post["listener"] == "__meowerbot__login" and post["val"] == "I:100 | OK":
            bot.send_msg(f"MeowyMod v{version} is alive! Use @MeowyMod help for info!")


# Register event listener for tickets and startup message
meowyMod.callback(listenerEventManager, cbid="__raw__")

print(f"MeowyMod {version} starting up now...")

# Run bot
meowyMod.run(
    username=os.getenv("BOT_USERNAME"),
    password=os.getenv("BOT_PASSWORD"),
    server=os.getenv("SERVER_CL")
)
