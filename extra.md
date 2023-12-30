## Extra Features
### Pet Bot
Pet bot is an extra feature for channels. It allows users in a member to have there own virtual pet. Each users will be entitles to their own pets and won't be able to access others. Users will not be able to take over their pets to other channels as petbot is only unique to a specified channel that its been activated in.

#### Set up:
Enter commands:
- petbot!activate - activates the pet bot features
- petbot!deactvate - deactivates the pet bot features

#### Useful Commands:
- pet!help - outlines all the commands for petbot

#### Pet bot Game:
- pet!adopt animal_type gender name: Creates a player on petbot with their specified pets. It takes in an animal_type (see variable types), gender (see variable types), and name

- pet!checkon name: takes in a specific pet name. returns the current state of the pet

- pet!feed, pet!water, pet!play - These are all different commands to take care of pets. 
- pet!player_status - each player will have attributes such as money, food, water to use on their pets. returns their current states as players
- pet!work - allows players to gain money to buy food and water
- pet!buy - allows players to buy food and water

#### Variables types:
- ANIMAL_TYPES = ['dog', 'cat', 'bird', 'horse', 'panda']
- GENDER_TYPES = ['male', 'female']

#### Time feature:
The petbot has a threading mechanism that allows pets to lose health overtime. By default it is every 30 mins that the health will decrease, with respect to the happiness, hunger, thirst attributes, with all these decreasing overtime. 
