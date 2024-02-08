#Buckshot roulette
import os
import random
import time

print()
DEFAULT_HEALTH = 4
dir_path = os.path.dirname(os.path.realpath(__file__))

rounds = 0

gun_side = open(os.path.join(dir_path,'gun-side.txt'),'r').read()
gun_fwd = open(os.path.join(dir_path,'gun-forwards.txt'),'r').read()
gun_back = open(os.path.join(dir_path,'gun-backwards-small.txt'),'r').read()
explosion = open(os.path.join(dir_path,'explosion.txt'),'r').read()
blank_round = open(os.path.join(dir_path,'blank-round.txt'),'r').read().splitlines()
live_round = open(os.path.join(dir_path,'live-round.txt'),'r').read().splitlines()

def displayList(arr):
    for i,s in enumerate(arr):
        time.sleep(0.1)
        print(f"{i+1}) {s}")

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
        print(f"[{name}] USED:",item)
        time.sleep(1)
        match item:
            case '🔪':
                gun.doubleDamage()
                print("Shotgun now does 2 damage.")

            case '🔍':
                print("Shhhh~~~")
                time.sleep(1)
                print(".. The next round is..")
                time.sleep(2)
                print(["blank.", "LIVE."][gun.rounds[-1]])
                time.sleep(1)
                print("~~~~~~~~~~")

            case '⛓':
                if not effector: return False
                effector.missTurns(1)
                print("Dealer will now miss a turn.")
            
            case '🍺':
                print("Shotgun has been racked.")
                r = gun.pickRound()
                time.sleep(1)
                print("Round was..")
                time.sleep(1.5)
                print(["blank.","LIVE."][r])

            case '🚬':
                self.addHealth()
                print(self.health)

            case _:
                print("uhm....")
                time.sleep(3)
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

        print("[DEALER] used",item)
        time.sleep(1.5)

        match item:
            case '⛓':
                effector.missTurns()
                print("[DEALER] cuffed you.")
            case '🔪':
                gun.doubleDamage()
                time.sleep(0.7)
                print("Shotgun now does 2 damage.")
            case '🚬':
                self.addHealth()
                time.sleep(0.7)
                print("[DEALER] now has",self.health,"lives.")
            case '🍺':
                print("Gun has been racked.")
                r = gun.pickRound()
                time.sleep(0.5)
                print("THE ROUND IS..")
                time.sleep(0.7)
                print()
                time.sleep(0.7)
                print(["blank.","LIVE."][r])
            case '🔍':
                r = gun.rounds[-1]
                print("[DEALER] has inspected the gun 🔍...")
                time.sleep(1)
                print("##############################",r)
                if r:
                    self.useItem('🔪',gun=gun)
                    self.shoot(gun,effector)
                    return True
                self.shoot(gun)
                return True
                
        time.sleep(1)
        return True

    def shoot(self,gun,effector=None):
        r = gun.pickRound()

        if effector:
            print("\n",gun_back,"\n")
            time.sleep(2.3)
            if r:
                if effector.health - gun.damage < 1:
                    time.sleep(2)
                    
                effector.takeDamage(gun.damage)
                print("\n",explosion,"\n")

                if effector.health > 0:
                    print("BOOM")
                    time.sleep(0.8)
                    print("You got shot.")
                    time.sleep(1.4)
                    print("Lives left:", effector.health)
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
        gun.resetDamage()


sg = Shotgun()
p1 = Player(DEFAULT_HEALTH)
dealer = AI(DEFAULT_HEALTH)

time.sleep(1)

print("[DEALER]: PLEASE SIGN THE WAIVER.")
askforhelp = ''

while askforhelp not in ["a","b"]:
    askforhelp = input("(a) Read Waiver or (b) Sign and continue? ").lower().strip(" ")

if askforhelp == "a":
    displayHelp()
    input("READY? ")

name = ""
while name in ["GOD","DEALER","SATAN"] or not (3 < len(name) < 10):
    if name:
        print("INVALID NAME.")
    name = input("ENTER NAME: ").strip(" ").upper()




while p1.health > 0 and dealer.health > 0:
    # load the shotgun
    live = random.randint(1,3)
    blank =  random.randint(1,3)
    sg.addRounds(live, blank)
    print("\n",gun_side)
    displayRounds(live,blank)
    time.sleep(0.5)
    print(f"{live} LIVE, {blank} BLANK\n")
    time.sleep(4)

    if not rounds:
        print("\"I INSERT THE SHELLS IN AN UNKNOWN ORDER.\"")
    else:
        print("\"THEY ENTER THE CHAMBER IN A HIDDEN SEQUENCE.\"")
    time.sleep(4)
    
    #give the players items
    p1.addRandomItems()
    dealer.addRandomItems()
    print("\nYour inventory:")
    displayList(p1.items)
    time.sleep(4)
    print("\nDealer's inventory:")
    displayList(dealer.items)
    time.sleep(3)
    
    #start turns
    turn = random.choice([True,False])
    
    
    while sg.rounds and p1.health and dealer.health:
        
        if (turn and (not p1.turnsWaiting)) or dealer.turnsWaiting:
            # =========> PLAYERS TURN TO CHOOSE
            opt = ""
            inp = ""

            if dealer.turnsWaiting:
                print("\n*Dealer skips their turn*")
                turn = not turn
                time.sleep(0.5)
                dealer.turnsWaiting = dealer.turnsWaiting - 1
            
            while sg.rounds:
                opt = ""

                if p1.items:
                    print("\n+==============+")
                    print("Your items:")
                    displayList(p1.items)
                    print("+==============+")
                    time.sleep(1)
                    print("\nIT IS YOUR TURN.")
                    print("(a) Use item")
                    print("(b) Shoot")

                    while opt.lower().strip(" ") not in ["a","b"]:
                        opt = input(" ").lower().strip(" ")

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
                    print("\nShooting yourself will skip Dealer's turn if round is blank.\n")
                    print("Shoot:")
                    time.sleep(0.6)
                    print("(a) DEALER")
                    time.sleep(0.6)
                    print("(b) YOU")
                    inp = ""

                    while inp not in ["a","b","back","q","quit","x"]:
                        inp = input(" ").lower().strip(" ")

                    
                    time.sleep(0.5)
                    
                    if inp == "a": # shoot DEALER
                        r = sg.pickRound()
                        print("\n",gun_fwd,"\n")
                        time.sleep(1.8)
                        if r:
                            dealer.takeDamage(sg.damage)
                            print("\n",explosion,"\n")
                            time.sleep(0.5)
                            print("[DEALER] was shot.")
                            print("Dealers health:", dealer.health)
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
                        if p1.health - sg.damage < 1:
                            time.sleep(2)
                        if r:
                            p1.takeDamage(sg.damage)
                            print("\n",explosion,"\n")
                            if p1.health > 0 :
                                time.sleep(0.5)
                                print("You got shot.")
                                print(f"YOUR HEALTH:", p1.health)
                                time.sleep(1.2)
                            break
                        else:
                            print("*click*")
                            time.sleep(0.5)
                            print("round was blank.")
                            time.sleep(0.5)
                            
                    
        else: #DEALERS turn
            if p1.turnsWaiting:
                print("\nYou skip this turn.")
                turn = not turn
                time.sleep(1.5)
                p1.turnsWaiting = p1.turnsWaiting - 1

            print("\nDEALERS TURN.")
            time.sleep(2)

            while sg.rounds:
                r = sg.rounds[-1]

                # BEGIN AI DECIDING
                print("[DEALER] is chosing...")
                time.sleep(random.randint(15,45)/10)
                
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
    rounds +=1
    dealer.turnsWaiting = 0
    if p1.health > 0 and dealer.health > 0:
        print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
        print("..NEXT ROUND..")
        time.sleep(2)
        print("DEALER'S HEALTH:")
        time.sleep(1)
        print(dealer.health)
        time.sleep(2)
        print("YOUR HEALTH:")
        time.sleep(1)
        print(p1.health)
        time.sleep(2)



c = 0
while c < 700000:
    c+=1
    print("█",end="")

if not dealer.health:
    print("\n\n\n\nThe dealer died.")
    print("You win..")
else:
    print("\n\n\n\nYOU DIED.")
