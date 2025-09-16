
# you can customize the script's behaviour here

api_key = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
# your api key as shown in https://web.simple-mmo.com/p-api/home

update_rate = 5.0
# seconds between each update cycle.
# setting the variable to less than 1.5 will cause ratelimit errors

expected_pace = 7
# expected stepping speed (steps/min), used to calculate target ETAs.
# without any stepping speed bonus, a player could typically maintain a
# speed of 7 - 7.5 steps/min

targets = {
    'daily': 0,
    'weekly': 0
    }
# the amount of (lifetime) steps you need to reach before the next 
# daily/weekly reset (e.g. for tasks)

level_display = 'decimal'
# how the player level is displayed (one of 'decimal', 'verbose',
# 'absolute'). Examples:
# 'decimal': Level 1234.92
# 'verbose': Level 1234 (92% to next level)
# 'absolute': Level 1234 (56789/61700 XP)