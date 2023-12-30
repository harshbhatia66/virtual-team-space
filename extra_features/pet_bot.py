# Extra Feature - Pet Bot
from src.data_store import data_store
from threading import Thread, ThreadError
import time

# Pet Class
class Pet:
    def __init__(self, animal_type, gender, name):
        # Initial Attributes
        self.__animal_type = animal_type.capitalize()
        self.__gender = gender.capitalize()
        self.__name = name.capitalize()

        # Animal Attributes
        self.__health = 100
        self.__hunger = 100
        self.__thirst = 100
        self.__happiness = 100
        self.__is_dead = False
    
    def get_name(self):
        return "Name: " + self.__name + " || Type: " + self.__animal_type

    def is_dead(self):
        return self.__is_dead

    def feed(self):
        """
        Decreases the Pet's hunger level.
        """
        if self.is_dead():
            return
        
        self.__hunger += 5

        # Check for overfeeding
        if self.__hunger > 100:
            self.__hunger = 100
            self.__is_dead = True

    def water(self):
        """
        Decreases the Pet's thirst level.
        """
        if self.is_dead():
            return

        self.__thirst += 10

        # Checks for overwatering
        if self.__thirst > 100:
            self.__thirst = 100
            self.__is_dead = True

    def play(self):
        """
        Increase the Pet's Happiness level.
        """
        if self.is_dead():
            return

        self.__happiness += 5

        if self.__happiness > 100:
            self.__happiness = 100

    def decrease_attributes(self):
        """
        Adjusts stats as though time has passed for this tamagotchi.
        """
        if self.is_dead():
            return 
        
        self.__hunger -= 5
        self.__thirst -= 10
        self.__happiness -= 5

        self.__health = int(((self.__hunger + self.__thirst + self.__happiness) / 300) * 100)
        
        if self.__happiness < 0:
            self.__happiness = 0
            self.__hunger -= 5
            self.__thirst -= 5

        if self.__hunger < 0:
            self.__is_dead = True

        if self.__thirst < 0:
            self.__is_dead = True

        if self.__health < 0:
            self.__health = 0
            self.__is_dead = True

    def increment_time(self):
        """
        Adjusts stats as though time has passed for this Pet.
        """
        # Every 30 mins
        duration = 1800

        curr_time = int(time.time())
        next_time = curr_time + duration
        while not self.is_dead():
            curr_time = int(time.time())
            if curr_time == next_time:
                self.decrease_attributes()
                next_time = curr_time + duration
                 

    def start(self):
        t1 = Thread(target=self.increment_time)

        try:
            t1.start()
        except ThreadError:
            print("Thread Error")

    def stop(self):
        self.__is_dead = True

    def checkon(self):
        """
        Returns a string representing the current status of the Pet.
        """

        if self.is_dead():
            return f"Name: {self.__name} - Dead \n"

        return \
f"""
Name: {self.__name}\n
Type: {self.__animal_type}\n
Gender: {self.__gender}\n
Health: {self.__health}\n
Hunger: {self.__hunger}\n
Thirst: {self.__thirst}\n
Happiness: {self.__happiness}\n
"""

import random

# Player Class
class Player:
    
    ANIMAL_TYPES = ['dog', 'cat', 'bird', 'horse', 'panda']
    GENDER_TYPES = ['male', 'female']

    def __init__(self, u_id):
        self.__u_id = u_id
        self.__pet = {}

        # Inventory
        self.__money = 100
        self.__food = 0
        self.__water = 0

    def get_money(self):
        return self.__money

    def get_food(self):
        return self.__food

    def get_water(self):
        return self.__water

    def get_u_id(self):
        return self.__u_id

    def get_pets(self):
        if len(self.__pet) <= 0:
            return "No Pets"
        return '\n'.join([p.get_name() for p in self.__pet.values()])

    def adopt_pet(self, animal_type, gender, name):
        if animal_type.lower() not in self.ANIMAL_TYPES:
            return
        
        if gender.lower() not in self.GENDER_TYPES:
            return

        if len(name) < 1 or len(name) > 100:
            return 
         
        pet_tmp = Pet(animal_type.lower(), gender.lower(), name.lower())
        pet_tmp.start()
        self.__pet.update({name.lower(): pet_tmp})

    def work(self):
        self.__money += random.randint(100, 300)

    def buy(self, type):
        if self.__money < 0:
            return 

        if type.lower() == 'food' and self.__money > 10:
            self.__food += 1
            self.__money -= 10
        elif type.lower() == 'water' and self.__money > 5:
            self.__water += 1
            self.__money -= 5

        return "Bought"
        
    def water(self, name):
        if self.__water <= 0:
            return
        
        name = name.lower()
        pet_tmp = self.__pet.get(name)
        if pet_tmp != None:
            pet_tmp.water()

        if pet_tmp.is_dead():
            return

        return "Watered"

    def feed(self, name):
        if self.__food <= 0:
            return 

        name = name.lower()
        pet_tmp = self.__pet.get(name)
        if pet_tmp != None:
            pet_tmp.feed()  

        if pet_tmp.is_dead():
            return

        return "Fed" 

    def play(self, name):
        name = name.lower()
        pet_tmp = self.__pet.get(name)
        if pet_tmp != None:
            if pet_tmp.is_dead():
                return
            pet_tmp.play()

    def checkon(self, name):
        name = name.lower()
        pet_tmp = self.__pet.get(name)
        if pet_tmp != None:
            return pet_tmp.checkon()
        else:
            return "Pet does not exist"

    def player_stats(self):
        return \
f"""
Money: {self.__money}\n
Pet Food: {self.__food}\n
Water: {self.__water}\n
"""

"""
'channels': {
    1: {
        'channel_id': 1,
        'name': "Test 1",
        'is_pet_bot_active': True,
        'pet_bot_players': {
            1001: player_1,
        }
    }
}

"""

GAME_NAME = "petbot!"

def activate_pet_bot(channel_id, msg):
    data = data_store.get()
    channel = data['channels'].get(channel_id)

    if "petbot!activate" in msg:
        channel.update({'is_pet_bot_active': True})
        channel.update({'pet_bot_players': {}})
    elif "petbot!deactivate" in msg:
        channel.update({'is_pet_bot_active': False})
        players = channel.get('pet_bot_players')
        if players != None:
            players.clear()

    data_store.set(data)

def check_pet_bot_active(channel_id):
    data = data_store.get()
    channel = data['channels'].get(channel_id)
    
    status = False
    if channel.get('is_pet_bot_active'):
        status = True

    return status

def main_game(auth_user_id, channel_id, msg):

    cmd = msg.split(" ")
    cmd_type = cmd[0]

    print(cmd_type)
    if cmd_type == "pet!adopt":
        msg = adopt_pet(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!checkon":
        msg = check_on(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!play":
        msg = play_pet(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!feed":
        msg = feed_pet(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!water":
        msg = water_pet(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!buy":
        msg = buy(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!work":
        msg = work(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!player_stats":
        msg = player_stats(auth_user_id, channel_id, cmd)
    elif cmd_type == "pet!help":
        msg = help_information()

    return msg
    
def adopt_pet(auth_user_id, channel_id, cmd):
    if len(cmd) != 4:
        return "Not enough commands"
    animal_type = cmd[1]
    gender = cmd[2]
    name = cmd[3]

    if animal_type not in Player.ANIMAL_TYPES:
        return "Invalid Animal Type"
    elif gender not in Player.GENDER_TYPES:
        return "Invalid Animal Gender"
    elif len(name) < 1 or len(name) > 500:
        return "Invalid Name"

    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')
    
    player = None

    # Checks if user is already a current player
    if auth_user_id in curr_players:
        player = curr_players.get(auth_user_id)
    else:
        # Creates 
        player = Player(auth_user_id)
    
    # Adopts pet
    player.adopt_pet(animal_type, gender, name)

    curr_players.update({auth_user_id: player})

    data_store.set(data)

    user = data['users'].get(auth_user_id)
    handle_str = user.get('handle_str')
    return f"{handle_str} have adopted pet {animal_type}, named {name}."

def check_on(auth_user_id, channel_id, cmd):
    if len(cmd) != 2:
        return "Not enough commands"

    name = cmd[1].lower()

    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')

    if auth_user_id not in curr_players:
        return "Invalid Player"
    
    player = curr_players.get(auth_user_id)
    
    return player.checkon(name)

def play_pet(auth_user_id, channel_id, cmd):
    if len(cmd) != 2:
        return "Not enough commands"

    name = cmd[1]
    
    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')

    if auth_user_id not in curr_players:
        return "Invalid Player"

    player = curr_players.get(auth_user_id)

    player.play(name)

    data_store.set(data)

    user = data['users'].get(auth_user_id)
    handle_str = user.get('handle_str')
    return f"{handle_str} played with {name}."


def feed_pet(auth_user_id, channel_id, cmd):
    if len(cmd) != 2:
        return "Not enough commands"

    name = cmd[1]

    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')

    if auth_user_id not in curr_players:
        return "Invalid Player"

    player = curr_players.get(auth_user_id)

    if player.get_food() <= 0:
        return "No food in your invertory"

    if player.feed(name) == None:
        return "Overfed"

    data_store.set(data)
    
    user = data['users'].get(auth_user_id)
    handle_str = user.get('handle_str')
    return f"{handle_str} fed {name}."

def water_pet(auth_user_id, channel_id, cmd):
    if len(cmd) != 2:
        return "Not enough commands"

    name = cmd[1]

    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')

    if auth_user_id not in curr_players:
        return "Invalid Player"

    player = curr_players.get(auth_user_id)

    if player.get_water() <= 0:
        return "No water in your inventory"

    if player.water(name) == None:
        return "Drowned"

    data_store.set(data)

    user = data['users'].get(auth_user_id)
    handle_str = user.get('handle_str')
    return f"{handle_str} gave water to {name}."

def buy(auth_user_id, channel_id, cmd):
    if len(cmd) != 2:
        return "Not enough commands"

    product_type = cmd[1].lower()

    types = ['food', 'water']

    if product_type not in types:
        return "Invalid product"

    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')

    if auth_user_id not in curr_players:
        return "Invalid Player"

    player = curr_players.get(auth_user_id)

    if player.buy(product_type) == None:
        return "Not enough funds"

    data_store.set(data)

    user = data['users'].get(auth_user_id)
    handle_str = user.get('handle_str')
    return f"{handle_str} bought {product_type}."

def work(auth_user_id, channel_id, cmd):
    if len(cmd) != 1:
        return "Too much commands"

    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')

    if auth_user_id not in curr_players:
        return "Invalid Player"

    player = curr_players.get(auth_user_id)

    player.work()

    data_store.set(data)

    user = data['users'].get(auth_user_id)
    handle_str = user.get('handle_str')
    return f"{handle_str} worked and earned ${player.get_money()}."

def player_stats(auth_user_id, channel_id, cmd):
    if len(cmd) != 1:
        return "Too much commands"

    data = data_store.get()
    channel = data['channels'].get(channel_id)
    curr_players = channel.get('pet_bot_players')

    if auth_user_id not in curr_players:
        return "Invalid Player"

    player = curr_players.get(auth_user_id)

    return player.player_stats()

def help_information():
    return \
f"""
Petbot Help:\t\t\t\t\t\tPet Management:\n
petbot!activate\t\t\t\t\tpet!adopt animal_type gender name\n
petbot!deactivate\t\t\t\t\tpet!checkon name\n
pet!help\t\t\t\t\t\t\tpet!play name\n
\t\t\t\t\t\t\t\tpet!feed name\n
\t\t\t\t\t\t\t\tpet!water name\n
\n
Player Management\t\t\t\tVariables:\n
pet!player_stats\t\t\t\t\tAnimal Types: 'dog', 'cat', 'bird', 'horse', 'panda'\n
pet!work\t\t\t\t\t\t\tGender Types: male, female\n
pet!buy product type\n
\n
See Full documentation for more infomation\n
"""
    