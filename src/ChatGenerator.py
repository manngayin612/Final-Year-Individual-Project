import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from random import randrange
model_name = 'tuner007/pegasus_paraphrase'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

def pegasus_paraphraser(input_text):
  batch = tokenizer([input_text],truncation=True,max_length=60, return_tensors="pt").to(torch_device)
  translated = model.generate(**batch,max_length=60,num_beams=5, num_return_sequences=5, temperature=1.5)
  tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
  index = randrange(len(tgt_text))
  return tgt_text[index]
