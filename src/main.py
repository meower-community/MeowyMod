from dotenv import load_dotenv
from MeowerBot import Bot
import os
import requests
import time
import json

# Create instance of bot
meowyMod = Bot()

# Cache user account levels
userLevels = dict()

# Keep track of processing requests
tickets = dict()


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
    meowyMod.send_msg(f"@{tickets[ticketID]['origin']} I have processed the request \"{ticketID}\" with result {status}!")
    del tickets[ticketID]


# Commands
@meowyMod.command(args=0, aname="meow")
def quack(ctx):
    ctx.send_msg("MeowyMod is here! Use @MeowyMod help for info!")


@meowyMod.command(args=0, aname="help")
def help(ctx):
    ctx.send_msg(" - help: this message.\n - meow: another fun message!\n - about: Learn a little about me!\n - refresh: Clean up my cached user levels!\n - kick (username)\n - ban (username)\n - ipban (username)\n - pardon (username)\n - ippardon (username)")


@meowyMod.command(args=0, aname="about")
def about(ctx):
    ctx.send_msg("MeowyMod v1.0 \nCreated by @MikeDEV, built using @ShowierData9978's MeowerBot.py library! \n\nI'm a little orange cat with a squeaky toy hammer, and I'm here to keep Meower a safer place! Better watch out, only Meower Mods, Admins, and Sysadmins can use me!")


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


def handleTickets(post, bot):
    # Validate keys
    for key in ["cmd", "val", "listener"]:
        if key not in post:
            return

    # Handle listeners
    if post["cmd"] == "statuscode" and post["listener"] in tickets:
        resolveTicket(post["listener"], post["val"])

if __name__ == "__main__":
    # Load environment keys
    if not load_dotenv():
        print("Failed to load .env keys, exiting.")
        exit()

    meowyMod.callback(handleTickets, cbid="__raw__")
    
    print("MeowyMod starting up now...")
    
    # Run bot
    meowyMod.run(
        username=os.getenv("BOT_USERNAME"),
        password=os.getenv("BOT_PASSWORD"),
        server=os.getenv("SERVER_CL")
    )
