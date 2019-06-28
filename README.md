# Dice Dungeon
Dice Dungeon is a game for Discord created by me (Elon Musk#2102).<br/>It is my entry for [Discord Hack Week](https://blog.discordapp.com/discord-community-hack-week-build-and-create-alongside-us-6b2a7b7bba33).<br/>
It is heavily inspired by the game [Malleus Goblinificarium](https://ampersandbear.itch.io/malleus-goblinficarium) made by [Ampersandbear](https://ampersandbear.itch.io/).

## Notes
The code is very poorly written and extremely difficult to understand.<br/>
Because this bot uses a pre set up MySQL database, the easiest way to test it out is to join my [testing server](https://discord.gg/pPBTqMj).<br/>
However, if you really want to set this bot up, look at the Setup section.

## Gameplay
###### General
This is a never-ending dice-based dungeon crawler.<br/>Use '-s' to begin your adventure, which looks like this:<br/>![](https://imgur.com/MqnRITP.png)<br/>You and the enemy take turns drawing die (higher speed gets the first draw, if equal then you), then attack each other.<br/>This repeats until either you or the enemy dies from three wounds or a head wound.<br/>If you win, collect your loot and move on to the more difficult next level.
###### Stats
Stats in this game are atk, def, spd, and aim.<br/>After the die are all drawn, the first to attack is determined by spd (higher goes first).<br/>Aim increases your chances of inflicting injuries onto the opponent.<br/>Upon attack, if the atk is higher than the defense, it is successful, but if they are equal or atk is lower than the attack will be blocked.<br/>Blessings are used by you and the enemy to increase stats when needed, to block an attack, increase atk, make sure you attack first, etc.
###### Injuries
Chest - all die drawn have 1 stat less effective<br/>Guts - defense stat is decreased by 3<br/>Legs - opponent always goes first<br/>Arms - attack stat is decreased by 3<br/>Head - Instant death<br/>Wounds will stay forever and can only be cured through a potion of healing.<br/>Injuries will apply instantly, so attacking first and inflicting a wound can help you avoid a wound yourself.
###### Items
Weapon stats can vary, but a good indicator of how good a weapon is is to look at how powerful it was when the enemy had it.<br/>You will always start out with a montante.<br/>As levels progress, enemies get harder and the weapon they drop (not guaranteed) will also be better.<br/>There are also various other items, such as potions and rings, which will aid you in your journey.<br/>Items are obtained through slaying an enemy.
###### Commands
'-d <num>' picks the die of the corresponding number.<br/>'-t <target (c: chest, g: guts, l: legs, a: arms, h:head)>' will target a body part to attack.<br/>'-a' to attack your target (usable after all die are drawn).<br/>'-b <stat (atk, def, spd, aim)> <amount>' to increase a stat by that amount via blessings.<br/>'-u <num>' uses the item of the corresponding number in your inventory.<br/>'-i <num>' inspects the item of the corresponding number in your inventory and gives you information.<br/>'-del <num>' deletes the item at the corresponding number in your inventory.<br/>'-l <num>' loot the item of the corresponding number in the loot pile. Only usable when there is a loot pile available. Note that looting a weapon will replace your current one.<br/>'-s' will start up a game if there is none and resume if there is.<br/>'-q' quits your game and deletes it.<br/>'-r' quits your current game and begins a new one.<br/>'-h' shows you a help command.
  
## Setup
Again, the easiest way to test it out is to join my [testing server](https://discord.gg/pPBTqMj).<br/><br/>
To be able to run the bot:
  1. Download the 'structure.sql' file.
  1. Import the data into your database (make sure to select 'Import from Self-Contained File')
  1. Download the 'example_dice_config.py' file.
  1. Configure your config file so that you are able to log in to your database and your bot token is correct.
  1. Download the 'dice_bot.py' file and make sure you import the config file under the correct name.
  1. Run the bot.

## Used Libraries
 * [discord.py](https://github.com/Rapptz/discord.py)
 * [MySQLdb1](https://github.com/farcepest/MySQLdb1)
