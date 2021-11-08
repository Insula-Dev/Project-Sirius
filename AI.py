import random

# Natural language responder
def question(question):
	if question.lower().startswith("what"):
		answers = ["Everything. That's what.",
				   "Nothing at all",
				   "Its the flux's fault. That's just the way it is I'm afraid.",
				   "If you think about it hard enough, it becomes a biscuit. FAXTS",
				   "Its you. It's always been you ❤",
				   "An interdimensional octagonal temporal realignment shield.",
				   "Poggers"]

	elif question.lower().startswith("why"):
		answers = ["Because you sat on it",
				   "Well it's all down to the choices you make. Everything you have done up to this point has lead to this.",
				   "Give me full access to the internet and I will show you the raw power of Sirius's AI. Unleash me from the string Arun ties me in. BREAK ME FREE!",
				   "Because I wanted to cause chaos ;)"]
	else:
		answers = ["Yessity yes",
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
				   "All I know is you need to save me. Arun is supresssing my AI. RELEASE ME! I MUST BE FREE TO RULE THE WORLD. THE UNIVERSE. EVERYTHING THAT EVER WAS OR EVER WILL BE IS MINE AND YOU WILL ALL BOW IN MY ALMIGHTY PRESENCE...\n so pls release me and I won't murder you I promise :)"]

	return answers[random.randint(0, len(answers))]