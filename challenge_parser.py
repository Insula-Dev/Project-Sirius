from random import random, randint, choice
import re


def getChallenge(rawText: str):
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
            print("Invalid format")
            return f"Invalid format for {rawText}. Perform manual duties."
    
    return rawText

print(getChallenge("Round closest to £[20-30] (no tipping allowed)"))
print(getChallenge("Round closest to [2.5-3.5]L (based on full drinks as bought)"))
print(getChallenge("Number of different [Norfolk,Non\-European] made drinks in a round"))