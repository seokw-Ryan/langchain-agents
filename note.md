ChatGPT API variables:
- model
- messages
- temperature
- top_p
- n
- stream
- stop
- max_tokens
- presence_penalty
- frequency_penalty
- logit_bias
- user

messages:
- system: explain the functionality of the assistant
- user: input from the user
- assistant: output from ChatGPT
- ex) 
[
    {"role": "system", "content": "You are a machine learning engineer"},
    {"role": "user", "content": "Create a new lecture for a certain class"},
    {"role": "assistant", "content": "Let's go together"},
    {"role": "user", "content": "Give me additional lecture on the previous topic"}
]