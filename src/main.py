from dotenv import load_dotenv
import update_check as updater
from MeowerBot import Bot
import requests
import os
import time
#import subprocess

# Version tracker
version = "1.1.0"

# Create instance of bot
meowyMod = Bot()

# Cache user account levels
userLevels = dict()

# Keep track of processing requests
tickets = dict()

# Restart script
def restart():
    print("Shutting down websocket")
    meowyMod.wss.stop()
    
    # Windows only
    #script = os.getenv("RESET_SCRIPT").split()
    #print(f"Running reset script: {script}")
    #subprocess.Popen(script, shell=True)
    
    # Linux
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


# Function for getting user permission level
def getUserLevel(ctx):
    # Cache the user's permissions level
    if ctx.user.username not in userLevels:
        response = requests.get(f"{os.getenv('SERVER_API')}/users/{ctx.user.username}")
        data = response.json()
        userLevels[ctx.user.username] = data["lvl"]
    return userLevels[ctx.user.username]


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
        " - help: this message.\n - meow: another fun message!\n - about: Learn a little about me!\n - refresh: Clean up my cached user levels!\n - kick (username)\n - ban (username)\n - ipban (username)\n - pardon (username)\n - ippardon (username)\n - update\n - shutdown\n - reboot")


@meowyMod.command(args=0, aname="about")
def about(ctx):
    ctx.send_msg(
        f"MeowyMod v{version} \nCreated by @MikeDEV, built using @ShowierData9978's MeowerBot.py library! \n\nI'm a little orange cat with a squeaky toy hammer, and I'm here to keep Meower a safer place! Better watch out, only Meower Mods, Admins, and Sysadmins can use me!")


@meowyMod.command(args=0, aname="refresh")
def refresh(ctx):
    match getUserLevel(ctx):
        case 4:
            # Reset userLevels
            userLevels = dict()
            ctx.send_msg("I've cleared out my cached userlevels.")
        case _:
            ctx.send_msg(f"You're not a sysadmin so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=1, aname="kick")
def kickUser(ctx, username):
    match getUserLevel(ctx):
        case 4:
            # Create new request ticket
            ticketID = registerNewTicket(ctx, username, "kick")

            meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "kick", "val": username}, "listener": ticketID})
        case _:
            ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=1, aname="ban")
def banUser(ctx, username):
    match getUserLevel(ctx):
        case 4:
            # Create new request ticket
            ticketID = registerNewTicket(ctx, username, "ban")

            meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "ban", "val": username}, "listener": ticketID})
        case _:
            ctx.send_msg(
                f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=1, aname="ipban")
def ipBanUser(ctx, username):
    match getUserLevel(ctx):
        case 4:
            # Create new request ticket
            ticketID = registerNewTicket(ctx, username, "ipban")

            meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "block", "val": username}, "listener": ticketID})
        case _:
            ctx.send_msg(
                f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=1, aname="pardon")
def pardonUser(ctx, username):
    match getUserLevel(ctx):
        case 4:
            # Create new request ticket
            ticketID = registerNewTicket(ctx, username, "pardon")

            meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "pardon", "val": username}, "listener": ticketID})
        case _:
            ctx.send_msg(
                f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=1, aname="ippardon")
def ipPardonUser(ctx, username):
    match getUserLevel(ctx):
        case 4:
            # Create new request ticket
            ticketID = registerNewTicket(ctx, username, "ippardon")

            meowyMod.wss.sendPacket({"cmd": "direct", "val": {"cmd": "unblock", "val": username}, "listener": ticketID})
        case _:
            ctx.send_msg(
                f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=0, aname="update")
def updateCheck(ctx):
    match getUserLevel(ctx):
        case 4:
            # Check for updates
            if not updater.isUpToDate(f"{os.getenv('SCRIPT_PATH')}/main.py", "https://raw.githubusercontent.com/MeowerBots/MeowyMod/main/src/main.py"):
                ctx.send_msg("Looks like I'm out-of-date! Downloading updates...")
                time.sleep(1)
                
                updater.update(f"{os.getenv('SCRIPT_PATH')}/main.py", "https://raw.githubusercontent.com/MeowerBots/MeowyMod/main/src/main.py")
                
                ctx.send_msg("Rebooting to apply updates...")
                time.sleep(1)
                restart()
            else:
                ctx.send_msg(f"Looks like I'm up-to-date! Running v{version} right now.")
        case _:
            ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=0, aname="reboot")
def rebootScript(ctx):
    match getUserLevel(ctx):
        case 4:
            ctx.send_msg("Oke! I'm rebooting now...")
            restart()
        case _:
            ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


@meowyMod.command(args=0, aname="shutdown")
def shutdownScript(ctx):
    match getUserLevel(ctx):
        case 4:
            ctx.send_msg("Goodbye! I'm shutting down now...")
            shutdown()
        case _:
            ctx.send_msg(f"You don't have permissions to do that so I ignored your request, {ctx.user.username}.")


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


if __name__ == "__main__":
    # Load environment keys
    if not load_dotenv():
        print("Failed to load .env keys, exiting.")
        exit()

    meowyMod.callback(listenerEventManager, cbid="__raw__")

    print(f"MeowyMod {version} starting up now...")

    # Run bot
    meowyMod.run(
        username=os.getenv("BOT_USERNAME"),
        password=os.getenv("BOT_PASSWORD"),
        server=os.getenv("SERVER_CL")
    )
