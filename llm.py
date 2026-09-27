from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# tokenizer = AutoTokenizer.from_pretrained("babylm/babyllama-100m-2024")
# model = AutoModelForCausalLM.from_pretrained("babylm/babyllama-100m-2024", device_map="auto")

tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    dtype=torch.float16,  # halves memory usage
    device_map="auto"
)

BOT_CONTEXT = (
    "You are Sirius, a friendly Discord bot made by Insula (formerly known as APE)"
    "Commands: level, leaderboard, help, embed, (/)poll, (/)purge, review confessions, post confessions, settings, config, report, announce, locate, kill" 
    "Answer simply and briefly, usually in one sentence. "
    "Do not repeat the question."
)

def generate_reply(input_text):
    prompt = f"{BOT_CONTEXT}\nUser: {input_text}\nSirius:"
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            do_sample=True,
            temperature=0.75,
            top_p=0.99,
            repetition_penalty=1.15,
            no_repeat_ngram_size=3,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = output[0, inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

if __name__ == '__main__':
	# Example usage
	input_text = "Who made Sirius and what can it do?"
	generated_text = generate_reply(input_text)
	print(generated_text)