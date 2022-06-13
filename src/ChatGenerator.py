import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import time
from random import randrange
model_name = 'tuner007/pegasus_paraphrase'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

def pegasus_paraphraser(input_text):
  batch = tokenizer([input_text],truncation=True,padding='longest',max_length=60, return_tensors="pt").to(torch_device)
  translated = model.generate(**batch,max_length=60,num_beams=5, num_return_sequences=5, temperature=1.5)
  tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
  index = randrange(len(tgt_text))
  return tgt_text[index]




# input = ["It is locked.", 
#         "You have escaped",
#         "What else do you want to add?",
#         "Do you unlock it with a password?",
#         "It is written 9797 on the painting.",
#         "There is a painitng hanging on the wall of the room.",
#         "I am not sure which item are you referring to, can you try again?",
#         "The room is now ready! I can't wait to see them struggling in here." ,
#         "Imagine all those silly faces in the dark, they have no idea what's in here, tell them what you see.", 
#         "It's time to create your own room! Lock the people up and watch them suffer but before that, how should we call your room?",
#         "What do you want to say to them after unlocking this item? Perhaps congratulating them for escaping from this hell or maybe give them some tips?" ]

# eval = True
# model_name = 'tuner007/pegasus_paraphrase'
# torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
# # tokenizer = PegasusTokenizer.from_pretrained(model_name)
# # model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

# def pegasus_paraphraser(input_text, tokenizer, model):
#   if eval: start = time.process_time()
#   batch = tokenizer([input_text],truncation=True,padding='longest',max_length=60, return_tensors="pt").to(torch_device)
#   translated = model.generate(**batch,max_length=60,num_beams=5, num_return_sequences=5, temperature=1.5)
#   tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
#   index = randrange(len(tgt_text))
#   if eval: print(len(input_text), input_text, tgt_text[index], time.process_time() - start)
#   return tgt_text[index]



# from parrot import Parrot
# import torch
# import warnings
# warnings.filterwarnings("ignore")

# ''' 
# uncomment to get reproducable paraphrase generations
# def random_state(seed):
#   torch.manual_seed(seed)
#   if torch.cuda.is_available():
#     torch.cuda.manual_seed_all(seed)

# random_state(1234)
# '''

# #Init models (make sure you init ONLY once if you integrate this to your code)

  

# def parrot_paraphraser(input, parrot):

#   if eval: start_time = time.process_time()
#   para_phrases = parrot.augment(input_phrase=input, max_return_phrases =5)

#   index = randrange(len(para_phrases))
#   if eval: print(len(input), input, para_phrases[index], time.process_time()- start_time)
#   return para_phrases[index]

# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM





# def t5_paraphraser(input, tokenizer, model):

#   if eval: start_time = time.process_time()
#   # tokenize the text to be form of a list of token IDs
#   inputs = tokenizer([input], truncation=True, padding="longest", return_tensors="pt")
#   # generate the paraphrased sentences
#   outputs = model.generate(
#     **inputs,
#     num_beams=20,
#     num_return_sequences=5,
#   )
# # decode the generated sentences using the tokenizer to get them back to text
#   result = tokenizer.batch_decode(outputs, skip_special_tokens=True)
#   index = randrange(len(result))
#   if eval: print(len(input), input, result[index], time.process_time() - start_time)
#   return result[index]


# def compare():
#     tokenizer = PegasusTokenizer.from_pretrained(model_name)
#     model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)
#     print("-"*100)
#     print("PEGASUS")
#     print("-"*100)
#     for phrase in input:
#       pegasus_paraphraser(phrase, tokenizer, model)

#     tokenizer = AutoTokenizer.from_pretrained("Vamsi/T5_Paraphrase_Paws")
#     model = AutoModelForSeq2SeqLM.from_pretrained("Vamsi/T5_Paraphrase_Paws")
    
    
#     print("\n")
#     print("-"*100)
#     print("T5")
#     print("-"*100)
#     for phrase in input:
#       t5_paraphraser(phrase, tokenizer, model)
#     print("\n")
#     parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5", use_gpu=False)
#     print("\n")
#     print("-"*100)
#     print("Parrot")
#     print("-"*100)
#     for phrase in input:
#       parrot_paraphraser(phrase, parrot)
#     print("\n")

# compare()