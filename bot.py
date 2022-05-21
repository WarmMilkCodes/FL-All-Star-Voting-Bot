import discord
from discord.ext import commands
import config
from discord.commands import Option
from pymongo import MongoClient
import pymongo
import certifi

#Mongo Setup
mongoURL = config.MONGO_CLIENT
ca = certifi.where()
cluster = pymongo.MongoClient(mongoURL, tlsCAFile=ca) 
db = cluster["flcc"]
collection = db["allstar"]
registeredEast = db["registeredEast"]
registeredWest = db["registeredWest"]

#Discord Bot
bot = commands.Bot(command_prefix = '!', case_insensitive=True)
guildID = config.flccId


# Lists for temp use
westPlayers = []
eastPlayers = []
conference = []
playersRemaining = []
hasVoted = []
previouslyVoted = []


@bot.event
async def on_ready():
    print('%s is online!' % bot.user.name)
    await bot.change_presence(activity=discord.Game(name='Voting for the Fettuccine All-Stars'))
    
@bot.slash_command(guild_ids = guildID, description = "Test latency")
@commands.has_role("FL League Director")
async def ping(ctx):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)} ms')
    user = ctx.author.name
    print("%s ran ping command" % user)
    

@bot.slash_command(guild_ids = guildID, description = "Register for All-Star Series")
async def register(ctx,
                   conference_of_player:Option(str)):
    conference_of_player = conference_of_player.capitalize()
    if conference_of_player not in conference:
        await ctx.respond("Conferences are 'East' or 'West'. Please submit again.")
    elif ctx.author.name in westPlayers or ctx.author.name in eastPlayers:
        await ctx.respond("You are already registered.")
    elif conference_of_player == 'West':
        westPlayers.append(ctx.author.name)
        print('%s added to West Conference' % ctx.author.name)
        print(westPlayers)
        dict = {
            "Player Name: ":ctx.author.name
        }
        registeredWest.insert_one(dict)
    elif conference_of_player == 'East':
        eastPlayers.append(ctx.author.name)
        print('%s added to East Conference' % ctx.author.name)
        print(eastPlayers)
        dict = {
            "Player Name: ":ctx.author.name
        }
        registeredEast.insert_one(dict)
        
    
@bot.slash_command(guild_ids = guildID, description = "Cast vote")
async def vote(ctx,
            player:Option(discord.Member),
            player2:Option(discord.Member)):
    
    user = str(ctx.author)
    voted = str(player)
    voted2 = str(player2)
    
    
    
    await ctx.respond("Voting is closed.")
    
@bot.slash_command(guild_ids=guildID, description = "List FL All-Star Roster")
@commands.has_role("FL League Director")
async def roster(ctx):
    embed = discord.Embed(title="FL All-Star Roster", color=discord.Color.green())
    embed.add_field(name="East Roster", value="Dewbert\nGemini\nCheft\nCloud")
    embed.add_field(name="West Roster", value="LogiCC\nSlum\nFirst Precision\nalex.")
    await ctx.channel.send(embed=embed)
    




@bot.slash_command(guild_ids=guildID, description="Vote for remaining West roster")
async def vote_east(ctx,
                    player:Option(discord.Member)):
    user = str(ctx.author)
    vote = str(player)
    if ctx.author == player and ctx.author in playersRemaining:
        await ctx.respond("Please don't vote for yourself. Here are the players remaining: %s" % ' , '.join(playersRemaining))
    elif str(user) in hasVoted:
        await ctx.respond("You have already voted.")
        
    elif str(vote) not in playersRemaining:
        await ctx.respond("Please choose one of these players: %s" % (', '.join(playersRemaining)))
    elif str(vote) in playersRemaining:
        await ctx.respond("Thank you for voting.")
        hasVoted.append(user)
        print(hasVoted) 
    else:
        await ctx.respond("Tell Milk his bot broke.")
        
@bot.slash_command(guild_ids=guildID, description="Remaining players to vote for")
@commands.has_role("FL League Director")
async def remaing_players(ctx,
                          player:Option(discord.Member),
                          player2:Option(discord.Member):
    await ctx.respond(', '.join(playersRemaining))
    if player == player2:
        await ctx.respond("Please vote for two different players.")
        print("%s tried voting for %s twice" % (user, player))
    #elif player not in eastPlayers or westPlayers and player2 not in eastPlayers or westPlayers:
    #    await ctx.respond("One of the players you voted for has not registered to play in the All Star game yet.")
    elif user in previouslyVoted:
        await ctx.respond("You've already voted.")
        print("%s tried voting again." % user)
    else:
        await ctx.respond("Your vote has been recorded!")
        previouslyVoted.append(ctx.author)
        dict = {
            "Vote 1 for: ":voted,
            "Vote 2 for: ":voted2,
            "Vote by: ":user
        }
        collection.insert_one(dict)    
        print("%s voted for %s and %s" % (user,player,player2))
        print(previouslyVoted)
    
        
@bot.slash_command(guild_ids = guildID, description = "List Teams by Conference")
@commands.has_role("FL League Director")
async def list_teams(ctx):
    embed = discord.Embed(title="FL Teams by Conference", color=discord.Color.green())
    embed.add_field(name="Eastern",value="Detroit\nAtlanta\nBaltimore\nJersey\nNashville\nBuffalo\nMiami\nWashington\nCarolina\nOttawa\nCleveland\nNew England\nMontreal\nChicago\nPittsburgh\nPhiladelphia")
    embed.add_field(name="Western",value="Los Angeles\nKansas City\nUtah\nHouston\nPortland\nPhoenix\nSan Francisco\nSanta Fe\nNew Oreleans\nDallas\nLas Vegas\nSan Diego\nSeattle\nDenver\nSan Antonio\nMaui")
    await ctx.channel.send(embed=embed)


bot.run = bot.run(config.BOT_TOKEN)