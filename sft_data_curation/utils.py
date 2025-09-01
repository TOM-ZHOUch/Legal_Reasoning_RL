import json

from prompts import USER_PROMPT, SYSTEM_PROMPT

def load_json(file):
    with open(file,'r', encoding="utf8") as load_f:
        data = json.load(load_f)
        return data
    
def write_json(file, dict):
    with open(file, "w", encoding="utf8") as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)


def build_user_prompts(data):
    
    prompts = []
    
    for d in data:
        # print(d)
        # print(d['question'])
        prompt = USER_PROMPT.format(question = d['question'])
        
        prompts.append(prompt)
      
    return prompts


def build_messages(data, use_system_prompt):
    

    user_prompts = build_user_prompts(data=data)
    
    messages = []
    
    for i in range(len(data)):
        
        system_prompt = SYSTEM_PROMPT
        
        if use_system_prompt:
            messages.append([
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompts[i]}
                    ]
            )
            
        else:
            messages.append([
                    {'role': 'user', 'content': f'{system_prompt}\n{user_prompts[i]}'}
                ]
            )

    return messages
