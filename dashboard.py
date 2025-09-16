from math import ceil, modf
from time import time, localtime, gmtime, strftime, mktime, sleep
import requests
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from settings import api_key, update_rate, expected_pace, targets, level_display

def effectiveLevel(level, exp): return level+(exp-level*(level-1)*25)/level/50

def printBasicInfo(name, userid, level, gold, ep, maxep, qp, maxqp, hp):
    epFormat = '#f2ff80' if ep<maxep else '#000000 on #f2ff80'
    qpFormat = '#80dcff' if qp<maxqp else '#000000 on #80dcff'
    basicInfoList = []
    basicInfoList.append(f'[#0099ff]{name} (@{userid})[/]')
    if level_display == 'decimal':
        basicInfoList.append(f'Level [#80ff80]{level:.2f}[/]')
    elif level_display == 'verbose':
        exp = modf(level)[0]
        level = int(modf(level)[1])
        basicInfoList.append(f'Level [#80ff80]{level}[/] ([#80ff80]{int(exp*100)}%[/] to next level)')
    elif level_display == 'absolute':
        exp, level = modf(level)
        exp = round(exp*level*50)
        level = int(level)
        basicInfoList.append(f'Level [#80ff80]{level}[/] ([#80ff80]{exp}/{level*50}[/] XP)')
    basicInfoList.append(f'Pocket gold: [#ffdc80]{gold}[/]')
    basicInfoList.append(f'Health: [#ff8080]{hp}%[/]')
    basicInfoList.append('')
    basicInfoList.append(f'E: [{epFormat}]{ep}/{maxep}[/]')
    basicInfoList.append(f'Q: [{qpFormat}]{qp}/{maxqp}[/]')
    basicInfoStr = '\n'.join(basicInfoList)
    console.print(Panel(basicInfoStr))

def printStepInfo(sessionStart, sessionEnd):
    sessionTime = curTime - sessionStart['timestamp']
    sessionSteps = sessionEnd['steps'] - sessionStart['steps']
    sessionLevel = sessionEnd['level'] - sessionStart['level']
    if (mins:=sessionTime/60) != 0:
        stepSpeed = sessionSteps/mins
        levelSpeed = sessionLevel/mins
    else: stepSpeed, levelSpeed = 0, 0
    stepSpeedBar = min(int(stepSpeed*2), 20)
    levelSpeedBar = min(int(levelSpeed*10), 20)
    stepInfoList = []
    stepInfoList.append(f'Session time: [#a680ff]{sessionTime}[/] secs')
    stepInfoList.append('')
    stepInfoList.append(f'Steps in this session: [#80ffd2]+{sessionSteps}[/]')
    stepInfoList.append(f'Levels gained in this session: [#80ff80]+{sessionLevel:.2f}[/]')
    stepInfoList.append(f'[{"-"*stepSpeedBar}{" "*(20-stepSpeedBar)}] [#80ffd2]{stepSpeed:.2f}[/]st/m')
    stepInfoList.append(f'[{"-"*levelSpeedBar}{" "*(20-levelSpeedBar)}] [#80ff80]{levelSpeed:.2f}[/]lv/m')
    stepInfoStr = '\n'.join(stepInfoList)
    console.print(Panel(stepInfoStr))

def printTargetInfo(steps, expected_pace, targets):
    dailyReset = 86400-(curTime-43200)%86400
    weeklyReset = 604800-(curTime-388800)%604800
    targetInfoList = []
    targetInfoList.append(f'Current time: [#a680ff]{strftime("%Y-%m-%d %H:%M:%S %z", localtime(curTime))}[/]')
    targetInfoList.append('')
    targetInfoList.append(f'Time left until daily reset: [#a680ff]{strftime("%H:%M:%S", gmtime(dailyReset))}[/]')
    if (targets['daily']-steps) < 0:
        targetInfoList.append("You've met your daily target!")
    elif (targets['daily']-steps)/expected_pace*60 < dailyReset:
        targetInfoList.append(f"You will meet your daily target in [#a680ff]{strftime('%H:%M:%S', gmtime((targets['daily']-steps)/expected_pace*60))}[/] ([#80ffd2]{(targets['daily']-steps)}[/] steps @ [#80ffd2]{expected_pace}[/]st/m)")
    else:
        targetInfoList.append(f'You will miss your daily target! ([#00ffff]{int(targets["daily"]-(dailyReset)/60*expected_pace-steps)}[/] steps short at daily reset @ [#80ffd2]{expected_pace}[/]st/m)')
    targetInfoList.append(f'Time left until weekly reset: [#a680ff]{int((weeklyReset)/86400):02d}:{strftime("%H:%M:%S", gmtime(weeklyReset))}[/]')
    if (targets['weekly']-steps) < 0:
        targetInfoList.append("You've met your weekly target!")
    elif (targets['weekly']-steps)/expected_pace*60 < weeklyReset:
        targetInfoList.append(f"You will meet your weekly target in [#a680ff]{int((targets['weekly']-steps)/expected_pace*60/86400):02d}:{strftime('%H:%M:%S', gmtime((targets['weekly']-steps)/expected_pace*60))}[/] ([#80ffd2]{(targets['weekly']-steps)}[/] steps @ [#80ffd2]{expected_pace}[/]st/m)")
    else:
        targetInfoList.append(f'You will miss your weekly target! ([#80ffd2]{int(targets["weekly"]-(weeklyReset)/60*expected_pace-steps)}[/] steps short at weekly reset @ [#80ffd2]{expected_pace}[/]st/m)')

    targetInfoStr = '\n'.join(targetInfoList)
    console.print(Panel(targetInfoStr))

def postRequest(url, json):
    ratelimit = 1
    while True:
        request = requests.post(url, json=json, headers=headers)
        if repr(request) == '<Response [200]>': # success
            json_response = request.json()
            break
        else: # failed, maybe ratelimit?
            sleep(ratelimit)
            ratelimit += 1 # wait a bit longer after each retry
    return json_response

creds = {'api_key': api_key}
endpoint = 'https://api.simple-mmo.com/v1/player/me'
console = Console(highlight=False,width=80)
console.show_cursor(show=False)

response = postRequest(endpoint, creds)
sessionStart = {
    'steps': response['steps'],
    'level': effectiveLevel(response['level'], response['exp']),
    'timestamp': int(time())
    }
sessionEnd = {}
sessionEnd.update(sessionStart)

while True:
    response = postRequest(endpoint, creds)

    console.clear()
    
    curTime = int(time())
    name = response['name']
    userid = response['id']
    level = effectiveLevel(response['level'], response['exp'])
    gold = response['gold']
    hp = ceil(response['hp']/response['max_hp']*100)
    ep = response['energy']
    maxep = response['maximum_energy']
    qp = response['quest_points']
    maxqp = response['maximum_quest_points']
    printBasicInfo(name, userid, level, gold, ep, maxep, qp, maxqp, hp)
    
    steps = response['steps']
    sessionEnd['level'] = level
    
    if steps-sessionEnd['steps'] != 0:
        sessionEnd['steps'] = steps
        sessionEnd['timestamp'] = curTime
    if (curTime - sessionEnd['timestamp'] >= 30) or (steps == sessionStart['steps']):
        sessionEnd['timestamp'] = curTime
        sessionStart.update(sessionEnd)
    printStepInfo(sessionStart, sessionEnd)

    printTargetInfo(steps, expected_pace, targets)
    
    sleep(update_rate-time()%update_rate)