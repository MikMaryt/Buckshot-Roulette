#Buckshot roulette
import os
import random
import time


DEFAULT_HEALTH = 4
dir_path = os.path.dirname(os.path.realpath(__file__))

gun_side = open(os.path.join(dir_path,'gun-side.txt'),'r').read()
gun_fwd = open(os.path.join(dir_path,'gun-forwards.txt'),'r').read()
gun_back = open(os.path.join(dir_path,'gun-backwards-small.txt'),'r').read()
explosion = open(os.path.join(dir_path,'explosion.txt'),'r').read()
blank_round = open(os.path.join(dir_path,'blank-round.txt'),'r').read().splitlines()
live_round = open(os.path.join(dir_path,'live-round.txt'),'r').read().splitlines()

def displayList(arr):
    for i,s in enumerate(arr):
        time.sleep(0.6)
        print(f"{i+1}) {s}")
    print()

def displayRounds(live,blank,space=2):
    s = ""
    for line in range(len(blank_round)):
        for _ in range(live):
            s += live_round[line] + " "*space
        for _ in range(blank):
            s += blank_round[line] + " "*space
        s += "\n"
    print(s,end="")
    
def displayHelp():
    print("\n+=====================+\n")
    print("This game is based on the actual game 'buckshot roulette'.\nIn a nutshell, this is russian roulette.\nInfo: https://en.wikipedia.org/wiki/Buckshot_Roulette\n")
    print("INSTRUCTIONS:")
    print("    - OBJECTIVE: SURVIVE.")
    print("    - A shotgun is loaded with a disclosed number of bullets, some of which will be blanks.")
    print("    - Participants are given a set amount of lives (default = 4) to survive.")
    print("    - You and 'The Dealer' will take turns shooting.")
    print("    - Aim at The Dealer or at yourself - shooting yourself with a blank skips the Dealers turn.")
    print("    - Participants are given items to help out. Use them wisely.")
    print("    - if you have chosen wrongly, type 'q'/'quit'/'back' to go back.")
    print()
    print("ITEMS:")
    print("    • 🚬 = Gives the user an extra life.")
    print("    • 🍺 = Racks the shotgun and the bullet inside will be discarded.")
    print("    • 🔪 = Shotgun will deal double damage for one turn.")
    print("    • 🔍 = User will see what bullet is in the chamber.")
    print("    • ⛓ = Handcuffs the other person so they miss their next turn.")
    print("\nGood Luck.\n")
    print("+=====================+")


class Shotgun():
    def __init__(self):
        self.damage = 1
        self.rounds = []
    def doubleDamage(self):
        self.damage = 2
    def resetDamage(self):
        self.damage = 1
    
    def addRounds(self,live=0,blank=0):
        self.rounds.extend([True]*live)
        self.rounds.extend([False]*blank)
        random.shuffle(self.rounds)
            
    def pickRound(self):
        l = len(self.rounds)
        if not l: return
        return self.rounds.pop()
    
class Player():
    def __init__(self,health=DEFAULT_HEALTH,items=[]):
        self.health = health
        self.items = items
        self.turnsWaiting = 0
        
    def takeDamage(self,dmg=1):
        self.health = self.health - dmg
        return (not self.health)
    
    def addHealth(self,health=1):
        self.health = self.health +health
    
    def addRandomItems(self,n=None):
        if not n:
            n = random.randint(1,4)
        items = ["⛓","🔪","🍺","🚬","🔍"]
        self.items = [items[random.randint(0,4)] for _ in range(n)]
            
    def useItem(self,item, gun, effector):
        if not item in self.items:
            return False
        
        temp = self.items
        temp.remove(item)
        self.items = temp
        time.sleep(1)
        match item:
            case '🔪':
                gun.doubleDamage()
                print("Gun now does 2 damage.")

            case '🔍':
                print("Shhhh~~~")
                time.sleep(0.8)
                print(".. The next round is..")
                time.sleep(1)
                print()
                time.sleep(1)
                print(["blank.", "LIVE."][gun.rounds[-1]])
                time.sleep(0.5)
                print("~~~~~~~~~~")

            case '⛓':
                if not effector: return False
                effector.missTurns(1)
                print("The Dealer will now miss a turn.")
            
            case '🍺':
                print("gun has been racked.")
                r = gun.pickRound()
                time.sleep(1)
                print("Round was..")
                time.sleep(0.7)
                print()
                time.sleep(0.7)
                print(["blank.","LIVE."][r])
                print()

            case '🚬':
                self.addHealth()
                print(self.health)

            case _:
                print("uhm....")
                time.sleep(2.7)
                print("Game does not recognise the item.")
                return False
        time.sleep(1)
        return True
    
    def missTurns(self,n=1):
        self.turnsWaiting = n
    
class AI(Player):
    def useItem(self,item,effector=None,gun=None):

        if item not in self.items or (
                item == '⛓' and effector.turnsWaiting) or (
                item == '🔪' and sg.damage != 1
                ): return False
        temp = self.items
        temp.remove(item)
        self.items = temp

        print("Dealer is using item..")
        time.sleep(0.8)
        print()
        time.sleep(0.8)

        match item:
            case '⛓':
                effector.missTurns()
                print("Dealer has cuffed you.")
            case '🔪':
                gun.doubleDamage()
                print("Dealer has used 🔪.")
                time.sleep(0.7)
                print("Shotgun now does 2 damage.")
            case '🚬':
                self.addHealth()
                print("Dealer used 🚬.")
                time.sleep(0.7)
                print("Dealer now has",self.health,"lives left.")
            case '🍺':
                print("gun has been racked.")
                r = gun.pickRound()
                time.sleep(0.5)
                print("Round was..")
                time.sleep(0.7)
                print()
                time.sleep(0.7)
                print(["blank.","LIVE."][r])
            case '🔍':
                r = gun.rounds[-1]
                print("Dealer has inspected the gun.")
                time.sleep(1)
                if r:
                    self.useItem('🔪',gun=gun)
                    self.shoot(gun,effector)
                    return True
                self.shoot(gun)
                return True
                
        print()
        time.sleep(1)
        return True

    def shoot(self,gun,effector=None):
        r = gun.pickRound()

        if effector:
            print("\n",gun_back,"\n")
            time.sleep(2.3)
            if r:
                effector.takeDamage(gun.damage)
                print("\n",explosion,"\n")
                print("BOOM")
                time.sleep(0.8)
                print("You got shot.")
                time.sleep(1.4)
                print("Lives left:", p1.health)
                time.sleep(3)
                gun.resetDamage()
                return
        else:
            print("\n",gun_fwd,"\n")
            time.sleep(2)
            if r:
                self.takeDamage(1)
                print("\n",explosion,"\n")
                print("BOOM")
                time.sleep(0.5)
                print("Dealer was shot.")
                time.sleep(0.8)
                print("Dealer has", self.health ,"lives left.")
                time.sleep(1)
                gun.resetDamage()
                return
        print("*click*")
        time.sleep(0.8)
        print("round was blank.")
        time.sleep(1.5)
        print()
        gun.resetDamage()


sg = Shotgun()
p1 = Player(DEFAULT_HEALTH)
dealer = AI(DEFAULT_HEALTH)

time.sleep(1)

print("Type 'help' for help/instructions, otherwise ignore.")
askforhelp = input(">>> ").lower().strip(" ")
if askforhelp == "help":
    displayHelp()
    input("Ready? ")

while p1.health > 0 and dealer.health > 0:
    # load the shotgun
    live = random.randint(1,3)
    blank =  random.randint(1,3)
    sg.addRounds(live, blank)
    print("\n",gun_side)
    time.sleep(1)
    displayRounds(live,blank)
    time.sleep(0.5)
    print(f"The gun has {live+blank} bullets - {live} live, {blank} blank\n")
    time.sleep(1.8)
    input("Continue? ")
    
    #give the players items
    p1.addRandomItems()
    dealer.addRandomItems()
    print()
    print("Your inventory:")
    time.sleep(0.5)
    displayList(p1.items)
    time.sleep(2)
    print("Dealers inventory:")
    time.sleep(0.5)
    displayList(dealer.items)
    time.sleep(1)
    
    #start turns
    turn = random.choice([True,False])
    
    
    while sg.rounds and p1.health and dealer.health:
        
        if (turn and (not p1.turnsWaiting)) or dealer.turnsWaiting:
            # =========> PLAYERS TURN TO CHOOSE
            opt = ""
            inp = ""

            if dealer.turnsWaiting:
                print("*Dealer skips his turn*")
                turn = not turn
                time.sleep(0.5)
                print()
                dealer.turnsWaiting = dealer.turnsWaiting - 1
            
            while sg.rounds:
                opt = ""

                if p1.items:
                    print("+==============+")
                    time.sleep(0.4)
                    print("Your items:")
                    time.sleep(0.3)
                    displayList(p1.items)
                    print("+==============+")
                    time.sleep(0.4)
                    print("It is your turn.")
                    time.sleep(1)
                    print("(a) Use item")
                    time.sleep(0.5)
                    print("(b) Shoot")
                    time.sleep(0.5)

                    while opt.lower().strip(" ") not in ["a","b"]:
                        opt = input(" ").lower().strip(" ")

                    print()
                    time.sleep(0.5)
                #endif

                if opt == "a": # ======== > PLAYER USE ITEM
                    inp = ""
                    while (not inp.isdigit() or int(inp) < 1 or int(inp) > len(p1.items)) and inp not in ["quit","q","back","x"]:
                        inp = input("Use: ")
                        
                    if inp not in ["quit","q","back","x"]:
                        use = p1.useItem(p1.items[int(inp)-1],sg,dealer)
                        
                        if not use:
                            print(inp,"not used.\n\n\n\n")
                    time.sleep(1)

                else: # ============= > PLAYER SHOOT
                    print("Shooting yourself will skip dealers turn if round is blank.")
                    time.sleep(0.7)
                    print("Shoot:")
                    time.sleep(0.5)
                    print("(a) Dealer")
                    time.sleep(0.5)
                    print("(b) You")
                    inp = ""

                    while inp not in ["a","b","back","q","quit","x"]:
                        inp = input(" ").lower().strip(" ")

                    
                    time.sleep(0.5)
                    
                    if inp == "a": # shoot DEALER
                        r = sg.pickRound()
                        print("\n",gun_fwd,"\n")
                        time.sleep(1.4)
                        if r:
                            dealer.takeDamage(sg.damage)
                            print("\n",explosion,"\n")
                            time.sleep(0.5)
                            print("Dealer was shot.")
                            print("Dealer health:", dealer.health)
                            time.sleep(1.2)
                        else:
                            print("*click*")
                            time.sleep(0.5)
                            print("round was blank.")
                            time.sleep(0.5)
                            print()
                        break
                    elif inp == "b": # shoot YOURSELF
                        r = sg.pickRound()
                        print("\n",gun_back,"\n")
                        time.sleep(2.5)
                        if r:
                            p1.takeDamage(sg.damage)
                            print("\n",explosion,"\n")
                            time.sleep(0.5)
                            print("You got shot.")
                            print("Your health:", p1.health)
                            time.sleep(1.2)
                            break
                        else:
                            print("*click*")
                            time.sleep(0.5)
                            print("round was blank.")
                            time.sleep(0.5)
                            
                    
        else: #DEALERS turn
            if p1.turnsWaiting:
                print("You skip this turn.")
                turn = not turn
                time.sleep(0.6)
                print()
                time.sleep(0.6)
                p1.turnsWaiting = p1.turnsWaiting - 1

            print("DEALERS TURN.")
            time.sleep(1)

            while sg.rounds:
                r = sg.rounds[-1]

                # BEGIN AI DECIDING
                print("Dealer is chosing...")
                time.sleep(random.randint(5,25)/10)
                
                if False not in sg.rounds:
                    dealer.useItem('🔪',gun=sg)
                    dealer.shoot(sg,p1)
                    break

                if True not in sg.rounds:
                    dealer.shoot(sg)
                    continue
                
                if dealer.health < DEFAULT_HEALTH:
                    if dealer.useItem('🚬'): continue

                roundsLeft = len(sg.rounds)
                if roundsLeft < 5:
                    if (sg.rounds.count(True)/roundsLeft) >= 0.5:
                        if dealer.useItem('⛓',p1): continue
                        if not p1.turnsWaiting and dealer.useItem('🔍',gun=sg): continue
                        if random.choice(sg.rounds) and dealer.useItem('🔪',gun=sg): continue
                        
                        dealer.shoot(sg,p1)
                        break
                    
                
                # ⛓, mag.g, knf, cg, 🍺
                if random.choice([True,False]):
                    dealer.useItem(random.choice(dealer.items),p1,sg)
                    continue

                temp = [None,p1][random.choice(sg.rounds)]
                dealer.shoot(sg,temp)
                sg.resetDamage()
                if temp != None:
                    break
                if r: break

        turn = not turn
        sg.resetDamage()
        

    sg.resetDamage()
    p1.turnsWaiting = 0
    dealer.turnsWaiting = 0
    if p1.health > 0 and dealer.health > 0:
        print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
        print("..NEXT ROUND..")
        time.sleep(1)
        print("Dealers Health:")
        time.sleep(0.5)
        print(dealer.health)
        time.sleep(0.5)
        print("Your health:")
        time.sleep(0.5)
        print(p1.health)
        time.sleep(0.5)



c = 0
while c < 700000:
    c+=1
    print("█",end="")

if not dealer.health:
    print("\n\n\n\nDealer dies.")
    print("You win.")
else:
    print("\n\n\n\nYou died.")
