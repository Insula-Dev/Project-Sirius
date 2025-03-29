import asyncio
from datetime import datetime
from random import random, randint, choice
import re
import sched
import time
from venv import logger


def formatChallenge(rawText: str):
    # Get all cases of [] in the text
    dynamicComponents = re.findall(r'\[.*?\]', rawText)

    for dyn in dynamicComponents:
        # Get the text inside the []
        if "-" in dyn and not "\-" in dyn:
            parts = dyn.split("-")
            if "." in parts[0] or "." in parts[1]:
                left = float(parts[0][1:])
                right = float(parts[1][:-1])
                # Get ranndom number between left and right
                randomValue = round(left + random() * (right - left), 1)
                # Replace the [] with the random number
                rawText = rawText.replace(dyn, str(randomValue))
            else:
                left = int(parts[0][1:])
                right = int(parts[1][:-1])
                # Get ranndom number between left and right
                randomValue = randint(left, right)
                # Replace the [] with the random number
                rawText = rawText.replace(dyn, str(randomValue))
        elif "," in dyn:
            parts = dyn.split(",")
            parts[0] = parts[0][1:]
            parts[-1] = parts[-1][:-1]
            # Get ranndom number between left and right
            randomValue = choice(parts)
            randomValue = randomValue.replace("\\", "")
            # Replace the [] with the random number
            rawText = rawText.replace(dyn, str(randomValue))
        else:
            logger.error("Invalid format")
            return f"Invalid format for {rawText}. Perform manual duties."
    
    return rawText

async def pubCrawl(challengeSetA, challengeSetB, originalMessage):
    taskNumber = 0
    # Run function at 17:00
    s1 = sched.scheduler(time.time, time.sleep)
    now = datetime.now()
    # 1 - 5pm
    await originalMessage.channel.send(f"# Pub Crawl Commencing...")
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")

    taskNumber += 1
    # 2 - 6pm
    await asyncio.sleep(60*0.5)
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")
    
    taskNumber += 1
    # 3 - 6:45pm
    await asyncio.sleep(60*0.5)
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")

    taskNumber += 1
    # 4 - 7:30pm
    await asyncio.sleep(60*0.5)
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")

    taskNumber += 1
    # 5 - 8:15pm
    await asyncio.sleep(60*0.5)
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")

    taskNumber += 1
    # 6 - 9pm
    await asyncio.sleep(60*0.5)
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")

    taskNumber += 1
    # 7 - 9:30pm
    await asyncio.sleep(60*0.5)
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")

    taskNumber += 1
    # 8 - 10pm
    await asyncio.sleep(60*0.5)
    await originalMessage.channel.send(f"## Round {taskNumber+1}")
    await originalMessage.channel.send(f"**Drink Challenge {taskNumber+1}**: {formatChallenge(challengeSetA[taskNumber])}")
    await originalMessage.channel.send(f"**Random Challenge {taskNumber+1}**: {formatChallenge(challengeSetB[taskNumber])}")

    taskNumber += 1
    await originalMessage.channel.send(f"That was the last challenge. Good luck!")
def doNothing():
    print("Nothing done")

if __name__ == "__main__":
    print(formatChallenge("Round closest to £[20-30] (no tipping allowed)"))
    print(formatChallenge("Round closest to [2.5-3.5]L (based on full drinks as bought)"))
    print(formatChallenge("Number of different [Norfolk,Non\-European] made drinks in a round"))