import random
import math
import discord
import MySQLdb
import traceback
import sys
import dice_config
import math
import asyncio
from discord.ext import commands as cmds

bot = cmds.Bot(command_prefix='-', activity=discord.Game("-h"))
client = discord.Client()
connection = MySQLdb.connect(**dice_config.database_config)
cursor = connection.cursor()

enemies = {'skeleton':{'atk':(0,1), 'def':(0,0), 'spd':(0,0), 'aim':(0,1)}, 
            'goblin':{'atk':(0,1), 'def':(-1,0), 'spd':(1,2), 'aim':(0,0)}, 
            'kobold':{'atk':(0,0), 'def':(-1,0), 'spd':(0,1), 'aim':(0,1)}, 
            'troll':{'atk':(1,2), 'def':(1,2), 'spd':(-2,-1), 'aim':(-1,0)}}
weapons = {'montante':{'atk':(2,3), 'def':(1,2), 'spd':(1,2), 'aim':(1,2), 'special':(None)},
            'flail':{'atk':(3,4), 'def':(-1,0), 'spd':(1,1), 'aim':(0,1), 'special':(None, 'chance to injure two body parts upon attack')},
            'shield':{'atk':(1,1), 'def':(3,4), 'spd':(1,1), 'aim':(1,1), 'special':(None, 'chance to reduce enemy\'s speed next turn')},
            'rapier':{'atk':(1,2), 'def':(0,1), 'spd':(3,4), 'aim':(3,4), 'special':(None)},
            'dagger':{'atk':(1,2), 'def':(-1,0), 'spd':(3,4), 'aim':(3,4), 'special':(None, 'chance to dodge enemy\'s attacks')}}
values = {'---(0)':0, 'aim(1)':1, 'spd(1)':2, 'aim(2)':3, 'spd(2)':4, 'aim(3)':5, 'spd(3)':6, 'def(1)':7, 'atk(1)':8, 'aim(4)':9, 'spd(4)':10, 'def(2)':11, 'atk(2)':12, 'aim(5)':13, 'spd(5)':14, 'aim(6)':15, 'spd(6)':16, 'def(3)':17, 'atk(3)':18, 'def(4)':19, 'atk(4)':20, 'def(5)':21, 'atk(5)':22, 'def(6)':23, 'atk(6)':24}
kinds = ['atk', 'def', 'spd', 'aim']
targets = {'c':'chest', 'g':'guts', 'l':'legs', 'a':'arms', 'h':'head'}
target_list = ['filler', 'chest', 'filler', 'guts', 'filler', 'legs', 'filler', 'arms', 'filler', 'head']
loot_list = ['totem', 'totem', 'totem', 'totem', 'totem', 'minor potion of atk', 'minor potion of atk', 'minor potion of atk', 'minor potion of def', 'minor potion of def', 'minor potion of def', 'minor potion of spd', 'minor potion of spd', 'minor potion of spd', 'minor potion of aim', 'minor potion of aim', 'minor potion of aim', 'minor potion of weakness', 'minor potion of weakness', 'minor potion of weakness', 'potion of atk', 'potion of atk', 'potion of def', 'potion of spd', 'potion of spd', 'potion of aim', 'potion of aim', 'potion of weakness', 'ring of atk', 'ring of def', 'ring of spd', 'ring of aim', 'armor', 'lucky charm', 'potion of healing', 'scroll of blessings']
footer_text = "'-d <num>' to pick a die / '-t <target>' to target a body part for attack / '-a' to attack a body part / '-b <stat> <amount>' to use blessings on a stat / '-u <num>' to use an item from your inventory / '-i <num>' to learn about an inventory item / '-l <num>' to loot items / '-s' to resume your game / '-q' to quit your game / '-r' to restart your game / '-del <num>' to delete an item from your inventory / '-h' for a more detailed help."

class Die():
    '''
    Simple die class that allows us to quickly pull\n
    out the type and value.
    '''
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __str__(self):
        return f"{self.kind}({self.value})"

class Game():
    '''
    A game object. Contains all the information about\n
    a game as. Pass in a tuple object gained from selecting\n
    from your database to instantly create a game instance.
    '''
    def __init__(self, game):
        self.game = game
        self.identi = self.game[0]
        self.enemy = self.game[1]
        self.wpn = self.game[2]
        self.e_split = list(map(int, self.game[3].split(',')))
        self.e_stats = {'atk':self.e_split[0], 'def':self.e_split[1], 'spd':self.e_split[2], 'aim':self.e_split[3]}
        self.p_split = list(map(int, self.game[4].split(',')))
        self.p_stats = {'atk':self.p_split[0], 'def':self.p_split[1], 'spd':self.p_split[2], 'aim':self.p_split[3]}
        self.inv = self.game[5].split(',')
        self.die_list = [Die(kind, int(value)) for (kind, value) in list(zip(self.game[6].split(','), self.game[7].split(',')))]
        self.e_blessings = self.game[8]
        self.p_blessings = self.game[9]
        self.cur_level = self.game[10]
        self.p_b_uses = list(map(int, self.game[11].split(',')))
        #test = self.game[12].split(',')
        self.p_wounds = self.game[12].split(',')
        #test2 = self.game[13].split(',')
        self.e_wounds = self.game[13].split(',')
        self.p_dice = list(map(int, self.game[14].split(',')))
        self.e_dice = list(map(int, self.game[15].split(',')))
        self.actionstr = self.game[16]
        self.p_targeting = self.game[17]
        self.e_targeting = self.game[18]
        self.e_attacked = self.game[19]
        self.p_d_count = list(map(int, self.game[20].split(',')))
        self.e_d_count = list(map(int, self.game[21].split(',')))
        self.p_extra = list(map(int, self.game[22].split(',')))
        self.loot = self.game[23].split(',')
        #test = self.game[24].split(',')
        self.p_popper = self.game[24].split(',')
        #test2 = self.game[25].split(',')
        self.e_popper = self.game[25].split(',')

        #the comments are there because otherwise the code breaks even though they don't do anything

    def to_db(self):
        cursor.execute(f'''UPDATE games SET enemy='{self.enemy}', e_wpn='{self.wpn}', e_stats='{','.join(list(map(str, self.e_stats.values())))}', p_stats='{','.join(list(map(str, self.p_stats.values())))}', inv='{','.join(self.inv)}', dice_ranks='{','.join([die.kind for die in self.die_list])}', dice_values='{','.join([str(die.value) for die in self.die_list])}', e_blessings={self.e_blessings}, p_blessings={self.p_blessings}, cur_level={self.cur_level}, p_b_uses='{','.join(list(map(str, self.p_b_uses)))}', p_wounds='{','.join(self.p_wounds)}', e_wounds='{','.join(self.e_wounds)}', p_dice='{','.join(list(map(str, self.p_dice)))}', e_dice='{','.join(list(map(str, self.e_dice)))}', actions="{self.actionstr}", p_targeting='{self.p_targeting}', e_targeting='{self.e_targeting}', e_attacked={self.e_attacked}, p_d_count='{','.join(list(map(str, self.p_d_count)))}', e_d_count='{','.join(list(map(str, self.e_d_count)))}', p_extra='{','.join(list(map(str, self.p_extra)))}', loot='{','.join(self.loot)}', p_popper='{','.join(self.p_popper)}', e_popper='{','.join(self.e_popper)}' WHERE identi='{self.identi}';''')

    def gen_embed(self, resume=False):
        '''
        Generates an embed for the game and returns it.
        '''
        game_embed = discord.Embed(color=int('0x%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
        if resume:
            game_embed.add_field(name=f"\_\_ @ \_\_\_\_\_ {self.enemy[0]} \_\_", value=f'Current level: {self.cur_level}\nResumed game.', inline=False)
        else:
            game_embed.add_field(name=f"\_\_ @ \_\_\_\_\_ {self.enemy[0]} \_\_", value=f'Current level: {self.cur_level}', inline=False)
        percent_list = [round((self.p_stats['aim']+self.p_dice[3]+self.p_b_uses[3]+self.p_extra[3])**2/target_list.index(self.p_targeting)**2*100), round((self.e_stats['aim']+self.e_dice[3])**2/target_list.index(self.e_targeting)**2*100)]
        percent_list = [percent if percent <= 100 else 100 for percent in percent_list]
        game_embed.add_field(name="\u200b\nyou", value=f"{self.p_stats['atk']+self.p_dice[0]+self.p_b_uses[0]+self.p_extra[0]} atk\n {self.p_stats['def']+self.p_dice[1]+self.p_b_uses[1]+self.p_extra[1]} def\n{self.p_stats['spd']+self.p_dice[2]+self.p_b_uses[2]+self.p_extra[2]} spd\n{self.p_stats['aim']+self.p_dice[3]+self.p_b_uses[3]+self.p_extra[3]} aim\ntargeting: {self.p_targeting} ({percent_list[0]}%)\nwounds: {', '.join(self.p_wounds)}\nblessings: {self.p_blessings}", inline=True)
        game_embed.add_field(name=f"\u200b\n{self.enemy}", value=f"{self.e_stats['atk']+self.e_dice[0]} atk\n{self.e_stats['def']+self.e_dice[1]} def\n{self.e_stats['spd']+self.e_dice[2]} spd\n{self.e_stats['aim']+self.e_dice[3]} aim\ntargeting: {self.e_targeting} ({percent_list[1]}%)\nwounds: {', '.join(self.e_wounds)}\nblessings: {self.e_blessings}", inline=True)
        game_embed.add_field(name=f"\u200b", value=f"\u200b", inline=True)
        game_embed.add_field(name=f"\u200b\ninv", value=f"**1**: {self.inv[0]} \n**2**: {self.inv[1]}\n**3**: {self.inv[2]}\n**4**: {self.inv[3]}\n**5**: {self.inv[4]}\n**6**: {self.inv[5]}", inline=True)
        game_embed.add_field(name=f"\u200b\ndie", value=f"**1**: {self.die_list[0]} \n**2**: {self.die_list[1]}\n**3**: {self.die_list[2]}\n**4**: {self.die_list[3]}\n**5**: {self.die_list[4]}\n**6**: {self.die_list[5]}\n", inline=True)
        generated = ''
        if 'none' not in self.loot:
            for i in range(1,len(self.loot)+1):
                generated += f"**{i}**: {self.loot[i-1]}\n"
            if generated != '':
                game_embed.add_field(name=f"\u200b\nLoot", value=generated, inline=True)
            else:
                game_embed.add_field(name=f"\u200b", value=f"\u200b", inline=True)
            if len(self.loot) == 0:
                self.loot = ['none']
        else:
            game_embed.add_field(name=f"\u200b", value=f"\u200b", inline=True)
        if len(self.actionstr.strip()) > 1:
            game_embed.add_field(name=f"\u200b\nActions", value=self.actionstr, inline=True)
        return game_embed

    def gen_loot(self):
        self.loot = []
        if random.randint(1,4) == 1:
            if 'lucky charm' in self.inv:
                for i in range(random.randint(1,4)):
                    self.loot.append(random.choice(loot_list))
                if random.randint(1,3) == 1:
                    self.actionstr += f"Your lucky charm disintegrates into ash!"
                    self.inv[self.inv.index('lucky charm')] = '----'
            else:
                for i in range(random.randint(1,3)):
                    self.loot.append(random.choice(loot_list))
        else:
            self.loot.append(self.wpn)
            if 'lucky charm' in self.inv:
                for i in range(random.randint(1,3)):
                    self.loot.append(random.choice(loot_list))
                if random.randint(1,3) == 1:
                    self.actionstr += f"Your lucky charm disintegrates into ash!"
                    self.inv[self.inv.index('lucky charm')] = '----'
            else:
                for i in range(random.randint(1,2)):
                    self.loot.append(random.choice(loot_list))
        cursor.execute(f"UPDATE games SET loot='{','.join(self.loot)}', inv='{','.join(self.inv)}' WHERE identi='{self.identi}';")

    def w_l_check(self):
        if len(self.e_wounds) == 3 or 'head' in self.e_wounds:
            cursor.execute(f"UPDATE games SET enemy='{self.enemy} (dead)' WHERE identi='{self.identi}';")
            self.enemy += ' (dead)'
            self.gen_loot()
            return f"**You slay the {self.enemy[:-7]} with your blow.**\n"
        elif len(self.p_wounds) == 3 or 'head' in self.p_wounds:
            cursor.execute(f"DELETE FROM games WHERE identi='{self.identi}';")
            return f"**The {self.enemy} slays you with its blow.**\nThis game has now been deleted."
        return ''

    def player_attack(self, quick=False):
        actionstr = ''
        chance_to_succeed = round((self.p_stats['aim']+self.p_dice[3]+self.p_b_uses[1])**2/target_list.index(self.p_targeting)**2, 2)
        if chance_to_succeed > 1:
            going_to_hit = True
        else:
            rand = random.randint(1,100)
            if rand >= 1 and rand <= chance_to_succeed*100:
                going_to_hit = True
            else:
                going_to_hit = False
                actionstr += f"You swing at the {self.enemy}'s {self.p_targeting} and miss.\n"
        if going_to_hit:
            p_atk, e_def = self.p_stats['atk']+self.p_dice[0]+self.p_b_uses[0], self.e_stats['def']+self.e_dice[1]
            if p_atk > e_def:
                if self.e_blessings >= p_atk - e_def:
                    self.e_dice[1] += (p_atk - e_def)
                    self.e_blessings -= (p_atk - e_def)
                    if (p_atk - e_def) == 1:
                        actionstr += f"The {self.enemy} uses {(p_atk - e_def)} blessing to boost its defense to {e_def+(p_atk - e_def)}.\nYou swing at the {self.enemy}'s {self.p_targeting}, but it blocks your attack.\n"
                    else:
                        actionstr += f"The {self.enemy} uses {(p_atk - e_def)} blessings to boost its defense to {e_def+(p_atk - e_def)}.\nYou swing at the {self.enemy}'s {self.p_targeting}, but it blocks your attack.\n"
                else:
                    if self.p_targeting == 'chest' and quick:
                        for i in range(4):
                            self.e_dice[i] -= self.e_d_count[1]
                    try: self.e_wounds.remove('none')
                    except: pass
                    if self.p_targeting not in self.e_wounds:
                        self.e_wounds.append(self.p_targeting)
                        self.e_popper.append(self.p_targeting)
                    actionstr += f"**You swing at the {self.enemy}'s {self.p_targeting}, injuring it!**\n"
                    actionstr += self.w_l_check()
                    e_wound_checker(self)
            elif p_atk == e_def or p_atk < e_def:
                actionstr += f"You swing at the {self.enemy}'s {self.p_targeting}, but it blocks your attack.\n"
        return actionstr

    def calc_attack(self):
        attacks = list(targets.values())[::-1]
        for wound in self.p_wounds:
            try: attacks.remove(wound)
            except ValueError: pass
        attack_prob = [round((self.e_stats['aim']+self.e_dice[3])**2/target_list.index(attack)**2, 2) for attack in attacks]
        prob_filtered = min([round(prob, 2) if prob >= 0.83 else 0 for prob in attack_prob])
        if prob_filtered != 0:
            self.e_targeting = attacks[attack_prob.index(prob_filtered)]
            return
        self.e_targeting = attacks[attack_prob.index(max(attack_prob))]

    def enemy_attack(self, quick=False):
        actionstr = ''
        self.calc_attack()
        self.e_attacked = 1
        if 'dead' not in self.enemy:
            chance_to_succeed = round((self.e_stats['aim']+self.e_dice[3])**2/target_list.index(self.e_targeting)**2,2)
            if chance_to_succeed > 1:
                going_to_hit = True
            else:
                rand = random.randint(1,100)
                if rand >= 1 and rand <= chance_to_succeed*100:
                    going_to_hit = True
                else:
                    going_to_hit = False
                    actionstr += f"The {self.enemy} swings at your {self.e_targeting} and misses.\n"
            if going_to_hit:
                e_atk, p_def = self.e_stats['atk']+self.e_dice[0], self.p_stats['def']+self.p_dice[1] + self.p_b_uses[1]
                if e_atk > p_def:
                    try: self.p_wounds.remove('none')
                    except: pass
                    if self.e_targeting not in self.p_wounds:
                        self.p_wounds.append(self.e_targeting)
                        self.p_popper.append(self.p_targeting)
                    actionstr += f"**The {self.enemy} swings at your {self.e_targeting}, injuring it!**\n"
                    actionstr += self.w_l_check()
                    if self.e_targeting == 'chest' and quick:
                        for i in range(4):
                            self.p_dice[i] -= self.p_d_count[i]
                    p_wound_checker(self)
                elif e_atk + self.e_blessings > p_def:
                    acc_tester = self.e_dice.copy()
                    percent = round((self.e_stats['aim']+acc_tester[3])**2/target_list.index(self.e_targeting)**2*100)
                    while percent < 83:
                        if e_atk + self.e_blessings > p_def + 1:
                            acc_tester[3] += 1
                            percent = round((self.e_stats['aim']+acc_tester[3])**2/target_list.index(self.e_targeting)**2*100)
                        else:
                            break
                    if percent >= 83:
                        self.e_blessings -= (acc_tester[3] - self.p_dice[3])
                        self.p_dice[3] += (acc_tester[3] - self.p_dice[3])
                        try: self.p_wounds.remove('none')
                        except: pass
                        if self.e_targeting not in self.p_wounds:
                            self.p_wounds.append(self.e_targeting)
                            self.p_popper.append(self.p_targeting)
                        self.e_dice[0] += (p_def - e_atk) + 1
                        self.e_blessings -= (p_def - e_atk) + 1
                        if (p_def - e_atk) + 1 == 1:
                            actionstr += f"The {self.enemy} uses {(p_def - e_atk) + 1} blessing to boost its attack to {e_atk+(p_def - e_atk) + 1}.**\nThe {self.enemy} swings at your {self.e_targeting}, injuring it!**\n"
                        else:
                            actionstr += f"The {self.enemy} uses {(p_def - e_atk) + 1} blessings to boost its attack to {e_atk+(p_def - e_atk) + 1}.**\nThe {self.enemy} swings at your {self.e_targeting}, injuring it!**\n"
                        actionstr += self.w_l_check()
                        if self.e_targeting == 'chest' and quick:
                            for i in range(4):
                                self.p_dice[i] -= self.p_d_count[i]
                        p_wound_checker(self)
                    else:
                        actionstr += f"The {self.enemy} swings at your {self.e_targeting}, but you block its attack.\n"
                elif e_atk == p_def or e_atk < p_def:
                    if "you block its attack" not in actionstr:
                        actionstr += f"The {self.enemy} swings at your {self.e_targeting}, but you block its attack.\n"
        return actionstr

    def enemy_move(self):
        if len([die for die in self.die_list if die.value != 0]) >= 1:
            values_list = [values[str(die)] for die in self.die_list]
            popped = values_list.index(max(values_list))
            die = self.die_list.pop(popped)
            self.die_list.insert(popped, Die('---',0))
            if 'chest' in self.e_wounds:
                self.e_dice[kinds.index(die.kind)] += die.value-1
            else:
                self.e_dice[kinds.index(die.kind)] += die.value
            self.calc_attack()
            return die
        return ''

    def move_after_draw(self):
        if len([die for die in self.die_list if die.value != 0]) == 0 and self.e_stats['spd'] + self.e_dice[2] > self.p_stats['spd'] + self.p_dice[2] + self.p_b_uses[2]:
            return self.enemy_attack(quick=True)
        return ''

    def pick_die(self, num):
        '''
        Picks a die off of the list
        '''
        if self.die_list[num].value != 0:
            die = self.die_list.pop(num)
            self.die_list.insert(num, Die('---',0))
            if 'chest' in self.p_wounds:
                self.p_dice[kinds.index(die.kind)] += die.value-1
            else:
                self.p_dice[kinds.index(die.kind)] += die.value
            self.p_d_count[kinds.index(die.kind)] += 1
            return die
        else:
            return "You cannot choose that die, as it has already been taken."

    def take_loot(self, num):
        item = self.loot.pop(num)
        if item in list(weapons.keys()):
            multiplier = 0.2 * self.cur_level + 1
            self.p_stats = {'atk':round(random.randint(weapons[item]['atk'][0], weapons[item]['atk'][1])*multiplier), 'def':round(random.randint(weapons[item]['def'][0],weapons[item]['def'][1])*multiplier), 'spd':round(random.randint(weapons[item]['spd'][0],weapons[item]['spd'][1])*multiplier), 'aim':round(random.randint(weapons[item]['aim'][0],weapons[item]['aim'][1])*multiplier)}
            self.inv[0] = item
            return f"You take the {item}, which is now your active weapon."
        for i in range(1, len(self.inv)+1):
            if self.inv[i] == '----':
                self.inv[i] = item
                if 'ring' in item:
                    self.p_extra[kinds.index(item.split()[2])] += 1
                    return f"You take the {item}, which is now at inventory slot {i}. The ring increases your {item.split()[2]} by 1."
                else:
                    return f"You take the {item}, which is now at inventory slot {i}."
        return "something bad happened"

@bot.event
async def on_ready():
    '''
    Just to let me know the bot is logging in correctly
    '''
    print(f"Successful log in as {bot.user}.")

@bot.event
async def on_command_error(ctx, error):
    '''
    Called when there is an error with a command,\n
    allows easy sending of error messages to the\n
    user without the use of a ton of try/except/else\n
    statements.
    '''
    identi = ctx.message.author.id
    cmd = ctx.message.content.split()[0]
    error = getattr(error, 'original', error)
    if hasattr(ctx.command, 'on_error'):
        return
    elif isinstance(error, cmds.MissingRequiredArgument):
        await ctx.send(f"You are missing one or more arguments for '{cmd}'. Use '-h commands' for more information on bot commands.")
    elif isinstance(error, cmds.BadArgument):
        await ctx.send(f"You have have one or more incorrect arguments for '{cmd}'. Use '-h commands' for more information on bot commands.")
    elif isinstance(error, cmds.CommandNotFound):
        await ctx.send(f"The command '{cmd}' was not found.")
    else:
        print('Ignoring exception in command {}:'.format(
            ctx.command), file=sys.stderr)
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)

def _adder(tup1, tup2):
    '''
    Pass in two tuples (most gained from weapon\n
    and enemy selection) and sum the random numbers\n
    for each. Used for assembling the enemy's stats.
    '''
    return random.randint(tup1[0], tup1[1]) + random.randint(tup2[0], tup2[1])

@bot.command(aliases=['begin', 'start', 'restart', 'retry', 'r', 'resume'])
async def s(ctx):
    '''
    Called when a user starts a game. 
    '''
    identi = ctx.message.author.id
    if ctx.message.content[1] == 'r':
        identi = ctx.message.author.id
        cursor.execute(f"DELETE FROM games WHERE identi='{identi}';")
        await ctx.send("Restarting game...")
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    game = cursor.fetchone()
    if game is None:
        enemy = random.choice(list(enemies))
        wpn = random.choice(list(weapons))
        (e_atk, e_def, e_spd, e_aim) = (enemies[enemy]['atk'], enemies[enemy]['def'], enemies[enemy]['spd'], enemies[enemy]['aim'])
        (w_atk, w_def, w_spd, w_aim) = (weapons[wpn]['atk'], weapons[wpn]['def'], weapons[wpn]['spd'], weapons[wpn]['aim'])
        e_stats = {'atk':_adder(e_atk, w_atk), 'def':_adder(e_def, w_def), 'spd':_adder(e_spd, w_spd), 'aim':_adder(e_aim, w_aim)}
        p_stats = {'atk':2, 'def':2, 'spd':2, 'aim':1}
        inv = ['montante', 'totem', '----', '----', '----', '----']
        die_list = [Die(random.choice(kinds), random.randint(1,6)) for k in range(6)]
        game_embed = discord.Embed(color=int('0x%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
        game_embed.add_field(name=f"\_\_ @ \_\_\_\_\_ {enemy[0]} \_\_", value='Current level: 1', inline=False)
        game_embed.add_field(name="\u200b\nyou", value=f"{p_stats['atk']} atk\n {p_stats['def']} def\n{p_stats['spd']} spd\n{p_stats['aim']} aim\ntargeting: chest\nwounds: chest\nblessings: 3", inline=True)
        game_embed.add_field(name=f"\u200b\n{enemy}", value=f"{e_stats['atk']} atk\n{e_stats['def']} def\n{e_stats['spd']} spd\n{e_stats['aim']} aim\ntargeting: chest\nwounds: none\nblessings: 2", inline=True)
        game_embed.add_field(name=f"\u200b", value=f"\u200b", inline=True)
        game_embed.add_field(name=f"\u200b\ninv", value=f"**1**: montante \n**2**: {inv[1]}\n**3**: {inv[2]}\n**4**: {inv[3]}\n**5**: {inv[4]}\n**6**: {inv[5]}", inline=True)
        game_embed.add_field(name=f"\u200b\ndie", value=f"**1**: {die_list[0]} \n**2**: {die_list[1]}\n**3**: {die_list[2]}\n**4**: {die_list[3]}\n**5**: {die_list[4]}\n**6**: {die_list[5]}\n", inline=True)
        game_embed.add_field(name=f"\u200b", value=f"\u200b", inline=True)
        cursor.execute(f"INSERT INTO games (identi, enemy, e_wpn, e_stats, p_stats, inv, dice_ranks, dice_values, e_blessings, p_blessings, cur_level, p_b_uses, p_wounds, e_wounds, p_dice, e_dice, p_d_count, e_d_count, p_extra, p_popper, e_popper) VALUES ('{identi}', '{enemy}', '{wpn}', '{','.join(map(str, e_stats.values()))}', '2,2,2,1', '{','.join(inv)}', '{','.join([die.kind for die in die_list])}', '{','.join([str(die.value) for die in die_list])}', 2, 3, 1, '0,0,0,0', 'none', 'none', '0,0,0,0', '0,0,0,0', '0,0,0,0', '0,0,0,0', '0,0,0,0', 'none', 'none');")
        cursor.execute(f"SELECT * FROM games WHERE identi='{identi}';")
        game = Game(cursor.fetchone())
        if game.e_stats['spd'] + game.e_dice[2] > game.p_stats['spd'] + game.p_dice[2]:
            e_move = game.enemy_move()
            if 'chest' in game.e_wounds:
                actionstr = f"The {game.enemy} chooses {str(e_move)}, boosting its {e_move.kind} stat by {e_move.value-1} due to its chest wound. It now has {game.e_stats[e_move.kind]+game.e_dice[kinds.index(e_move.kind)]} {e_move.kind}.\n"
            else:
                actionstr = f"The {game.enemy} chooses {str(e_move)}, boosting its {e_move.kind} stat by {e_move.value}. It now has {game.e_stats[e_move.kind]+game.e_dice[kinds.index(e_move.kind)]} {e_move.kind}.\n"
            game.actionstr = actionstr
            game_embed = game.gen_embed()
        if game.loot == ['none']:
            game_embed.set_footer(text=footer_text)
        else:
            game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
        await ctx.send(embed=game_embed)
        game.to_db()
    else:
        game = Game(game)
        game.calc_attack()
        game_embed = game.gen_embed(resume=True)
        if game.loot == ['none']:
            game_embed.set_footer(text=footer_text)
        else:
            game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
        await ctx.send(embed=game_embed)

@bot.command(aliases=['use'])
async def u(ctx, num:int):
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        num -= 1
        selected = game.inv[num]
        if num < 0 or num > 5:
            await ctx.send(f"Invalid item to use.")
            return
        elif selected == '----':
            await ctx.send(f"You have no item at that inventory space.")
        elif num == 0:
            await ctx.send(f"You are already using your {game.inv[0]}.")
            return
        elif 'ring' in selected:
            await ctx.send(f"Rings have a passive effect and thus cannot be used as an active.")
            return
        elif 'charm' in selected:
            await ctx.send(f"The lucky charm has a passive effect and thus cannot be used as an active.")
            return
        else:
            if selected == 'totem':
                rand = random.randint(1,2)
                game.p_blessings += rand
                game.actionstr = f'You use your totem, increasing your blessings by {rand}.'
            elif selected == 'scroll of blessings':
                rand = random.randint(3,5)
                game.p_blessings += rand
                game.actionstr = f'You use your scroll of blessings, increasing your blessings by {rand}.'
            elif 'weakness' in selected:
                if 'minor' in selected:
                    game.e_dice = [stat-1 for stat in game.e_dice]
                    game.actionstr = f"You use your minor potion of weakness, reducing the enemy's stats by 1."
                else:
                    game.e_dice = [stat-2 for stat in game.e_dice]
                    game.actionstr = f"You use your potion of weakness, reducing the enemy's stats by 2."
            elif 'healing' in selected:
                game.p_wounds = ['none']
                game.actionstr = f"You use your potion of healing, and you feel your wounds close!"
            elif 'potion' in selected:
                if 'minor' in selected:
                    game.p_dice[kinds.index(selected.split()[3])] += 1
                    game.actionstr = f"You use your {selected}, increasing your {selected.split()[3]} by 1."
                else:
                    game.p_dice[kinds.index(selected.split()[2])] += 2
                    game.actionstr = f"You use your {selected}, increasing your {selected.split()[2]} by 1."
            elif selected == 'armor':
                game.p_dice['def'] += 5
                game.actionstr = f"You use your armor, increasing your def by 5."
            game.inv[num] = '----'
            game.calc_attack()
            game_embed = game.gen_embed()
            if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
            else:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            await ctx.send(embed=game_embed)
            game.to_db()

@bot.command(aliases=['inspect'])
async def i(ctx, num:int):
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        num -= 1
        selected = game.inv[num]
        if num < 0 or num > 5:
            await ctx.send(f"Invalid item to inspect.")
            return
        elif selected == '----':
            await ctx.send(f"You have no item at that inventory space.")
        else:
            if num == 0:
                await ctx.send(f"Your {selected} grants you {game.p_stats['atk']} atk, {game.p_stats['def']} def, {game.p_stats['spd']} spd, and {game.p_stats['aim']} aim.")
            elif selected == 'totem':
                await ctx.send(f"The mysterious totem can be used to grant the favor of a god, increasing your blessings by 1 or 2. It burns up after use.")
            elif selected == 'scroll of blessings':
                await ctx.send(f"The powerful magic of this scroll increases your blessings by 3, 4, or 5 when read. It burns up after use.")
            elif 'weakness' in selected:
                await ctx.send(f"The fumes released from this potion weaken an enemy's stats by 2 for one round. Upon use, it is thrown at the enemy.")
            elif 'healing' in selected:
                await ctx.send(f"This sweet-smelling potion has enough power to instantly close your wounds. It is consumed on use.")
            elif 'potion' in selected:
                if 'minor' in selected:
                    await ctx.send(f"This small potion will increase your {selected.split()[3]} by 1 for one round. It is consumed on use.")
                else:
                    await ctx.send(f"This potion will increase your {selected.split()[2]} by 2 for one round. It is consumed on use.")
            elif selected == 'armor':
                await ctx.send(f"This powerful armor grants the wearer 5 defense for one round upon use. Afterwards, the armor disintegrates into a fine dust.")
            elif 'ring' in selected:
                await ctx.send(f"The magic of this ring grants you power, increasing your {selected.split()[2]} by 1. It is a passive effect.")
            elif 'charm' in selected:
                await ctx.send(f"Seems lucky. Maybe it will help you get more loot?")

@bot.command(aliases=['del', 'remove', 'dispose'])
async def delete(ctx, num:int):
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        num -= 1
        selected = game.inv[num]
        if num < 0 or num > 5:
            await ctx.send(f"Invalid item to delete.")
            return
        elif selected == '----':
            await ctx.send(f"You have no item at that inventory space.")
        elif num == 0:
            await ctx.send(f"Deleting your weapon is not a good idea.")
        else:
            game.inv[num] = '----'
            if 'ring' in selected:
                game.p_extra[kinds.index(selected.split()[2])] -= 1
                game.actionstr = f"You dispose your {selected}. The ring's power fades and your {selected.split()[2]} decreases by 1."
            else:
                game.actionstr = f'You dispose your {selected}.'
            game.calc_attack()
            game_embed = game.gen_embed()
            if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
            else:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            await ctx.send(embed=game_embed)
            game.to_db()

@bot.command(aliases=['quit', 'end'])
async def q(ctx):
    identi = ctx.message.author.id
    cursor.execute(f"DELETE FROM games WHERE identi='{identi}';")
    await ctx.send(f"Deleted any games that you had.")

def p_wound_checker(game):
    if 'legs' in game.p_popper:
        game.p_extra[2] = -99 #lowered speed
        game.p_popper.remove('legs')
    if 'guts' in game.p_popper:
        game.p_extra[1] -= 3 #lowered defense
        game.p_popper.remove('guts')
    if 'arms' in game.p_popper:
        game.p_extra[0] -= 3 #lowered attack
        game.p_popper.remove('arms')
    game.to_db()

def e_wound_checker(game):
    if 'legs' in game.e_popper:
        game.e_stats['spd'] = -99
        game.e_popper.remove('legs')
    if 'guts' in game.e_popper:
        game.e_stats['def'] -= 3
        game.e_popper.remove('guts')
    if 'arms' in game.e_popper:
        game.e_stats['atk'] -= 3
        game.e_popper.remove('arms')
    game.to_db()

@bot.command(aliases=['continue'])
async def c(ctx):
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        if 'dead' in game.enemy:
            game.die_list = [Die(random.choice(kinds), random.randint(1,6)) for k in range(6)]
            game.p_dice = [0,0,0,0]
            game.e_dice = [0,0,0,0]
            game.p_d_count = [0,0,0,0]
            game.e_d_count = [0,0,0,0]
            game.loot = ['none']
            game.actionstr = ''
            game.to_db()
            wpn = random.choice(list(weapons))
            multiplier = 0.2 * game.cur_level + 1
            e_updated_stats = f"{round(random.randint(weapons[wpn]['atk'][0], weapons[wpn]['atk'][1])*multiplier)},{round(random.randint(weapons[wpn]['def'][0],weapons[wpn]['def'][1])*multiplier)},{round(random.randint(weapons[wpn]['spd'][0],weapons[wpn]['spd'][1])*multiplier)},{round(random.randint(weapons[wpn]['aim'][0],weapons[wpn]['aim'][1])*multiplier)}"
            die_list = [Die(random.choice(kinds), random.randint(1,6)) for k in range(6)]
            cursor.execute(f"UPDATE games SET enemy='{random.choice(list(enemies))}', e_wpn='{wpn}', e_wounds='none', e_stats='{e_updated_stats}', dice_ranks='{','.join([die.kind for die in die_list])}', dice_values='{','.join([str(die.value) for die in die_list])}', e_blessings={game.cur_level+2}, cur_level={game.cur_level+1}, loot='none' WHERE identi='{identi}';")
            cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
            game = Game(cursor.fetchone())
            game.calc_attack()
            game_embed = game.gen_embed()
            if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
            else:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            await ctx.send(embed=game_embed)
        else:
            game.actionstr = ''
            if game.e_stats['spd'] + game.e_dice[2] > game.p_stats['spd'] + game.p_dice[2] + game.p_b_uses[2] and game.die_list[0].value != 0 and game.die_list[1].value != 0 and game.die_list[2].value != 0 and game.die_list[3].value != 0 and game.die_list[4].value != 0 and game.die_list[5].value != 0:
                e_move = game.enemy_move()
                if isinstance(e_move, Die):
                    actionstr = ''
                    if 'chest' in game.e_wounds:
                        actionstr = f"The {game.enemy} chooses {str(e_move)}, boosting its {e_move.kind} stat by {e_move.value-1} due to its chest wound. It now has {game.e_stats[e_move.kind]+game.e_dice[kinds.index(e_move.kind)]} {e_move.kind}.\n"
                    else:
                        actionstr = f"The {game.enemy} chooses {str(e_move)}, boosting its {e_move.kind} stat by {e_move.value}. It now has {game.e_stats[e_move.kind]+game.e_dice[kinds.index(e_move.kind)]} {e_move.kind}.\n"
                    game.actionstr = actionstr
            game.calc_attack()
            game_embed = game.gen_embed()
            if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
            else:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            await ctx.send(embed=game_embed)

@bot.command(aliases=['target', 'aim'])
async def t(ctx, target:str):
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        if 'dead' in game.enemy:
            await ctx.send(f"The enemy is dead. Use '-l <num>' to loot and '-c' to continue down to the next level.")
            return
        if target not in list(targets.keys()) and target not in list(targets.values()):
            await ctx.send(f"The body part you are trying to target ({target}) is not valid. Select from one of the following: chest, guts, legs, arms, head.")
        else:
            if target in list(targets.keys()):
                game.p_targeting = targets[target]
                game.actionstr = f"You are now aiming at the {game.enemy}'s {targets[target]}.\n"
            else:
                game.p_targeting = target
                game.actionstr = f"You are now aiming at the {game.enemy}'s {target}.\n"
            game_embed = game.gen_embed()
            if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
            else:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            await ctx.send(embed=game_embed)
            game.to_db()

@bot.command(aliases=['attack', 'hit', 'damage'])
async def a(ctx):
    actionstr = ''
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        if len([die for die in game.die_list if die.value != 0]) >= 1:
            await ctx.send(f"You cannot attack yet, as there are still die to be picked.")
            return
        if 'dead' in game.enemy:
            await ctx.send(f"The enemy is dead. Use '-l <num>' to loot and '-c' to continue down to the next level.")
            return
        actionstr += game.player_attack(quick=True)
        game.actionstr = actionstr
        if game.e_attacked == 1:
            game_embed = game.gen_embed()
            if 'dead' in game.enemy:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            else:
                game_embed.set_footer(text="Use '-c' to continue.")
            await ctx.send(embed=game_embed)
            game.p_b_uses = [0,0,0,0]
            game.e_attacked = 0
        else: 
            actionstr += game.enemy_attack()
            cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
            fetched = cursor.fetchone()
            game.actionstr = actionstr
            game_embed = game.gen_embed()
            if 'dead' in game.enemy:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            else:
                game_embed.set_footer(text="Use '-c' to continue.")
            await ctx.send(embed=game_embed)
            game.p_b_uses = [0,0,0,0]
            game.e_attacked = 0
            if fetched is None: pass
            else: game.to_db()
        if 'dead' not in game.enemy:
            game.die_list = [Die(random.choice(kinds), random.randint(1,6)) for k in range(6)]
            game.p_dice = [0,0,0,0]
            game.e_dice = [0,0,0,0]
            game.p_d_count = [0,0,0,0]
            game.e_d_count = [0,0,0,0]
            game.to_db()
            
@bot.command(aliases=['dice', 'die', 'pick'])
async def d(ctx, num:int):
    actionstr = ''
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        if 'dead' in game.enemy:
            await ctx.send(f"The enemy is dead. Use '-l <num>' to loot and '-c' to continue down to the next level.")
            return
        num -= 1
        if num >= 0 and num >= 6:
            await ctx.send(f"Invalid dice number to pick.")
            return
        p_dice = game.pick_die(num)
        if len([die for die in game.die_list if die.value != 0]) == 6:
            p_wound_checker(game)
            e_wound_checker(game)
        if isinstance(p_dice, Die):
            if 'chest' in game.p_wounds:
                actionstr = f"You pick {str(p_dice)}, boosting your {p_dice.kind} stat by {p_dice.value-1} due to your chest wound. You now have {game.p_stats[p_dice.kind]+game.p_dice[kinds.index(p_dice.kind)]} {p_dice.kind}.\n"
            else:
                actionstr = f"You pick {str(p_dice)}, boosting your {p_dice.kind} stat by {p_dice.value}. You now have {game.p_stats[p_dice.kind]+game.p_dice[kinds.index(p_dice.kind)]} {p_dice.kind}.\n"
        else:
            await ctx.send(p_dice)
            return
        e_move = game.enemy_move()
        if isinstance(e_move, Die):
            if 'chest' in game.e_wounds:
                actionstr += f"The {game.enemy} picks {str(e_move)}, boosting its {e_move.kind} stat by {e_move.value-1} due to its chest wound. It now has {game.e_stats[e_move.kind]+game.e_dice[kinds.index(e_move.kind)]} {e_move.kind}.\n"
            else:
                actionstr += f"The {game.enemy} picks {str(e_move)}, boosting its {e_move.kind} stat by {e_move.value}. It now has {game.e_stats[e_move.kind]+game.e_dice[kinds.index(e_move.kind)]} {e_move.kind}.\n"
        actionstr += game.move_after_draw()
        try: game.actionstr = actionstr
        except: game.actionstr = ''
        game_embed = game.gen_embed()
        if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
        else:
            game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
        await ctx.send(embed=game_embed)
        game.to_db()

@bot.command(aliases=['bless', 'blessing'])
async def b(ctx, stat:str, amount:int):
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        if 'dead' in game.enemy:
            await ctx.send(f"The enemy is dead. Use '-l <num>' to loot and '-c' to continue down to the next level.")
            return
        if stat not in kinds:
            await ctx.send(f"The stat you are trying to increase ({stat}) is not valid. Select from one of the following: atk, def, spd, aim.")
        else: 
            if amount > game.p_blessings:
                await ctx.send(f"You are trying to use more blessings than you have.")
                return
            elif amount <= 0:
                await ctx.send(f"You cannot increase a stat by 0 or less.")
                return
            if amount == 1: s = ''
            else: s = 's'
            game.p_b_uses[kinds.index(stat)] += amount
            game.p_blessings -= amount
            game.actionstr = f"You use {amount} blessing{s} to increase your {stat} from {game.p_stats[stat]+game.p_dice[kinds.index(stat)]} to {game.p_stats[stat]+game.p_dice[kinds.index(stat)]+amount}."
            game_embed = game.gen_embed()
            if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
            else:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            await ctx.send(embed=game_embed)
            game.to_db()

@bot.command(aliases=['loot'])
async def l(ctx, num:int):
    identi = ctx.message.author.id
    cursor.execute(f"SELECT * FROM games WHERE identi={identi};")
    fetched = cursor.fetchone()
    if fetched is None:
        await ctx.send(f"You are not currently in a game! Use '-s' to start.")
    else:
        game = Game(fetched)
        num -= 1
        if num not in [num for num in range(len(game.loot))]:
            await ctx.send(f"Invalid loot to pick up.")
            return
        elif game.inv[1] != "----" and game.inv[2] != "----" and game.inv[3] != "----" and game.inv[4] != "----" and game.inv[5] != "----":
            await ctx.send(f"Insufficient inventory space.")
            return
        elif game.loot == ['none']:
            await ctx.send(f"There are no items to loot.")
            return
        if 'dead' in game.enemy:
            game.actionstr = game.take_loot(num)
            game_embed = game.gen_embed()
            if game.loot == ['none']:
                game_embed.set_footer(text=footer_text)
            else:
                game_embed.set_footer(text="'-l <num>' to loot and '-c' to continue to the next level.")
            await ctx.send(embed=game_embed)
            game.to_db()
        else:
            await ctx.send("There is nothing to loot here!")

bot.remove_command('help')
@bot.command(aliases=['help'])
async def h(ctx, *help_tup):
    help_embed = discord.Embed(color=int('0x%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 16))
    try: help_for = help_tup[0].lower()
    except: help_for = 'none'
    if len(help_tup) == 0 or help_for != 'general' and help_for != 'stats' and help_for != 'injuries' and help_for != 'items' and help_for != 'commands':
        help_embed.add_field(name=f"Help", value=f"'-s'to start your adventure\n'-h all' for a complete embed of all the help messages\n'-h general' for a general idea on how to play the game\n'-h stats' for more information on stats and blessings\n'-h injuries' for more information on injuries\n'-h items' for more help with items and loot\n'-h commands' for a detailed list of commands and command usage", inline=False)
    if help_for == 'general' or help_for == 'all':
        help_embed.add_field(name=f"General", value=f"This is a never-ending dice-based dungeon crawler.\nUse '-s' to begin your adventure.\nYou and the enemy take turns drawing die (higher speed gets the first draw, if equal then you), then attack each other.\nThis repeats until either you or the enemy dies from three wounds or a head wound.\nIf you win, collect your loot and move on to the more difficult next level.", inline=False)
    if help_for == 'stats' or help_for == 'all':
        help_embed.add_field(name=f"Stats", value=f"Stats in this game are atk, def, spd, and aim.\nAfter the die are all drawn, the first to attack is determined by spd (higher goes first).\nAim increases your chances of inflicting injuries onto the opponent.\nUpon attack, if the atk is higher than the defense, it is successful, but if they are equal or atk is lower than the attack will be blocked.\nBlessings are used by you and the enemy to increase stats when needed, to block an attack, increase atk, make sure you attack first, etc.", inline=False)
    if help_for == 'injuries' or help_for == 'all':
        help_embed.add_field(name=f"Injuries", value=f"Chest - all die drawn have 1 stat less effective\nGuts - defense stat is decreased by 3\nLegs - opponent always goes first\nArms - attack stat is decreased by 3\nHead - Instant death\nWounds will stay forever and can only be cured through a potion of healing.\nInjuries will apply instantly, so attacking first and inflicting a wound can help you avoid a wound yourself.", inline=False)
    if help_for == 'items' or help_for == 'all':
        help_embed.add_field(name=f"Items", value=f"Weapon stats can vary, but a good indicator of how good a weapon is is to look at how powerful it was when the enemy had it.\nYou will always start out with a montante.\nAs levels progress, enemies get harder and the weapon they drop (not guaranteed) will also be better.\nThere are also various other items, such as potions and rings, which will aid you in your journey.\nItems are obtained through slaying an enemy.", inline=False)
    if help_for == 'commands' or help_for == 'all':
        help_embed.add_field(name=f"Commands", value=f"'-d <num>' picks the die of the corresponding number.\n'-t <target (c: chest, g: guts, l: legs, a: arms, h:head)>' will target a body part to attack.\n'-a' to attack your target (usable after all die are drawn).\n'-b <stat (atk, def, spd, aim)> <amount>' to increase a stat by that amount via blessings.\n'-u <num>' uses the item of the corresponding number in your inventory.\n'-i <num>' inspects the item of the corresponding number in your inventory and gives you information.\n'-del <num>' deletes the item at the corresponding number in your inventory.\n'-l <num>' loot the item of the corresponding number in the loot pile. Only usable when there is a loot pile available. Note that looting a weapon will replace your current one.\n'-s' will start up a game if there is none and resume if there is.\n'-q' quits your game and deletes it.\n'-r' quits your current game and begins a new one.\n'-h' shows you this help command.", inline=False)
    await ctx.send(embed=help_embed)

bot.run(dice_config.bot_token)