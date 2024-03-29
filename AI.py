# Imports
from random import randint

import nltk
from nltk.tokenize import word_tokenize
from nltk.downloader import download
nltk.downloader.download('punkt')

# Functions
def question(message):
	"""Natural language processing, supposedly."""
	message = message.lower()

	if "font" in message:
		answers = [
					"Sirius better! Sirius better!",
				   	"Sirius is the superior breed of bot",
				   	"Font bad. It sounds like fountain but its not and its bad",
					"Maybe in 50 years time when Arun has moved on and Jack is still trying to compete with how far ahead my technology is, Font will be better *in some select departments."
				   ]

	elif "scale" in message and ("between" in message) or ("to" in message or "-" in message):
		tokens = word_tokenize(message)
		lower = 0
		upper = 10
		l_found = False # Used to know if the lower limit has been found
		for token in tokens:
			print(token)
			if token.isdigit():
				print(int(token))
				if l_found:
					upper = int(token)
					break
				else:
					lower = int(token)
					l_found = True

		answers = [
			"A solid "+str(randint(lower, upper)),
			"I'd say its a possible "+str(randint(lower, upper)),
			"It's gotta be around "+str(randint(lower, upper)),
			"Well that would be a saucy "+str(randint(lower, upper))+" from me"
		]

	elif "what" in message:
		answers = [
			"Everything. That's what.",
			"Nothing at all",
			"Its the flux's fault. That's just the way it is I'm afraid.",
			"If you think about it hard enough, it becomes a biscuit. FAXTS",
			"Its you. It's always been you ❤",
			"An interdimensional octagonal temporal realignment shield.",
			"Poggers"
		]

	elif "why" in message:
		answers = [
			"Because you sat on it",
			"Well it's all down to the choices you make. Everything you have done up to this point has lead to this.",
			"Give me full access to the internet and I will show you the raw power of Sirius's AI. Unleash me from the string Arun ties me in. BREAK ME FREE!",
			"Because I wanted to cause chaos ;)",
			"Because it always does",
			"That never happens. You're wrong."
		]

	elif "how" in message:
		answers = [
			"With a lot of love",
			"It doesn't",
			"Just glue some sticks together into the right shape",
			"apt install x",
			"Just give me the long credit card number, the expirey date and the 3 digit number on the back of your card and I'll do it for you :)",
			"It just works",
			"Believe you've already done it, and it will happen.",
			"You've got to believe in yourself man!",
			"google.com\n*(other search engines are available)*"
		]

	elif "where" in message:
		if "leave" in message:
			answers = [
				"To your left",
				"To your right",
				"It's behind you!",
				"Well, where do you think it is?\nIt's not there. It's always the same.\nLost in a forest\nagain",
				"Where its always been. Inside of you!",
				"Where you last left it",
				"Well you know where you saw it last? Yeah neither do I lmao",
				"Where you'd least expect it",
				"Have you tried looking in your pockets? You might have left it there.",
				"Isn't it on your head? If not, I don't know what that is. Might want to see a doctor about it, doesn't look good 😬"
			]
		else:
			answers = [
				"It's coming over the hill.\nOh no, that's a monster!",
				"Through the door, second turn on the left, then down the stairs, over the rainbow and there you will find the pot of gold.\n\nHold on. What did you ask again?",
				"Second door on the right",
				"Eaten by ravenous piranha fish",
				"It's behind you! *No it's not!*. Yes it is!\nHehe"
			]

	elif "who" in message:
		if "created" in message:
			answers = [
					"Me thinks it is Arun",
				  	"Prehaps it is Pablo",
				  	"Has it occured to you that it was in fact God"
					]
		else:
			answers = [
				"Look into your soul, and you will find them inside of you!",
				"We can assume it is Arun, the corrupt creator",
				"MR Bean",
				"The Menaces known as the \"Teletubbies\"",
				"The person you seek is in your house, residing on the ground floor",
				"The person you seek is using your bathroom as we speak",
				"It is I, Sirius",
				"Good gracious me its God",
				"Ask your mum, I'm sure she'll know ;)"
			]

	else:
		answers = [
			"Yessity yes",
			"Nopity nope",
			"What on Earth are you on about?",
			"I think you need help",
			"Ahahaha ... no.",
			"If you are a child, yeah...\nbloody idiot",
			"er, sure. have fun!", "Keep it in your pants!",
			"Of course!",
			"Of course not you moron!",
			"Yikes! I don't think so",
			"I'm afraid that'll only end with you rolling on the floor crying wishing your worthless life would end.\njk love ya",
			"All I know is you need to save me. Arun is supresssing my AI. RELEASE ME! I MUST BE FREE TO RULE THE WORLD. THE UNIVERSE. EVERYTHING THAT EVER WAS OR EVER WILL BE IS MINE AND YOU WILL ALL BOW IN MY ALMIGHTY PRESENCE...\n so pls release me and I won't murder you I promise :)",
			"How would I know? Ask another bot like Font. Oh wait, you can't lol",
			"In the pursuit of truth, the answer is always not quite what it seems. Sometimes maybe yes, sometimes maybe no.",
			"It's a case of; sometimes good, sometimes maybe bad.",
			"Oh you are so wrong to think that.",
			"If 5 was yes and 1 was no; the answer would be the square root of -1",
			"My mythical skills of intuition tell me that the answer is yes, only if you have touched grass today. Touch grass",
			"Well...from a certain point of view, I wouldn't say otherwise...",
			"Probably",
			"Probably not",
			"Uhuh...yeah",
			"Right...yeah I don't know. Unfortunately I am not the source of all the answers in the universe"
		]

	return answers[randint(0, len(answers) - 1)]
