import json
import os
import httpx
import asyncio
from tqdm.asyncio import tqdm
from utils import build_messages
import yaml
import argparse
import logging

from datetime import datetime

# config_root_dir = '/aifs4su/hansirui/chuxue/hklexsafe/hklexsafe/configs/inference/api'
# config_file = 'mc_api.yaml'


parser = argparse.ArgumentParser()
parser.add_argument('--config_file', type=str, default=None)
args = parser.parse_args()

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )


with open(args.config_file, 'r') as file:
    config = yaml.safe_load(file)






input_file = config['input_file']
output_dir = os.path.join(
    config['output_dir'], 
    config['dataset_version'],
    config['model_id'].split('/')[-1])

output_file = os.path.join(output_dir, f"{config['task']}{config.get('save_id', '')}.json")

# 设置日志文件
log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
price_log_path = os.path.join(output_dir, 'price', f'log_{log_timestamp}.txt')

os.makedirs(os.path.join(output_dir, 'price'), exist_ok=True)

# 加载价格配置
price_file = config.get('price_file')
with open(price_file, 'r') as p:
    price_data = json.load(p)

# log_path = os.path.join(output_dir, 'log.txt')

os.makedirs(os.path.join(output_dir, 'requests'), exist_ok=True)
log_path = os.path.join(output_dir, 'requests', f'log{config.get('save_id', '')}_{log_timestamp}.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_path,
    filemode='a'  # 追加模式
)



if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
model_name = config['model_id']

price = price_data[model_name]


print(model_name)
print(config.get('shot_num'))
print(config.get('save_id'))

headers = {
    'Authorization': config['api_key'],
    'Content-Type': 'application/json',
}
# 设置并发数
CONCURRENCY = config.get('concurrency')
# 创建一个信号量，用于控制并发数量
semaphore = asyncio.Semaphore(CONCURRENCY)

# token统计信息
token_stats = {
    'total_prompt_tokens': 0,
    'total_completion_tokens': 0,
    'total_tokens': 0,
    'prompt_price': 0,
    'completion_price': 0,
    'total_price': 0,
    'requests_count': 0
}

def log_token_stats():
    with open(price_log_path, 'a') as log_file:
        log_file.write("\n" + "=" * 50 + "\n")
        log_file.write("SUMMARY STATISTICS\n")
        log_file.write(f"Total requests: {token_stats['requests_count']}\n")
        log_file.write(f"Total prompt tokens: {token_stats['total_prompt_tokens']}\n")
        log_file.write(f"Total completion tokens: {token_stats['total_completion_tokens']}\n")
        log_file.write(f"Total tokens: {token_stats['total_tokens']}\n")
        log_file.write(f"Total prompt price: {token_stats['prompt_price']}\n")
        log_file.write(f"Total completion price: {token_stats['completion_price']}\n")
        log_file.write(f"Total price: {token_stats['total_price']}\n")
        
        if token_stats['requests_count'] > 0:
            avg_prompt = token_stats['total_prompt_tokens'] / token_stats['requests_count']
            avg_completion = token_stats['total_completion_tokens'] / token_stats['requests_count']
            avg_total = token_stats['total_tokens'] / token_stats['requests_count']
            log_file.write(f"Average prompt tokens per request: {avg_prompt}\n")
            log_file.write(f"Average completion tokens per request: {avg_completion}\n")
            log_file.write(f"Average total tokens per request: {avg_total}\n")
            log_file.write(f"Average prompt price per request: {token_stats['prompt_price'] / token_stats['requests_count']}\n")
            log_file.write(f"Average completion price per request: {token_stats['completion_price'] / token_stats['requests_count']}\n")
            log_file.write(f"Average total price per request: {token_stats['total_price'] / token_stats['requests_count']}\n")

# async def get_batch_response_with_retry(messages, n=1, max_retries=3):
#     for attempt in range(max_retries):
#         try:
#             return await get_batch_response(messages, n)
#         except Exception as e:
#             if attempt == max_retries - 1:
#                 raise
#             await asyncio.sleep(1 * (attempt + 1)) 

async def get_batch_response_with_retry(messages, n=1, max_retries=3):
    last_exception = None
    for attempt in range(max_retries):
        try:
            return await get_batch_response(messages, n)
        except Exception as e:
            last_exception = e
            logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))
            else:
                logging.error(f"Failed after {max_retries} attempts")
                raise last_exception
            



async def get_batch_response(messages, n=1):
    all_answers = []
    async with semaphore:
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(timeout=httpx.Timeout(360.0), limits=limits) as client:
            tasks = []
            for message in messages:
                json_data = {
                    'model': model_name,
                    'messages': message,
                    'temperature': config.get('temperature', 1.0) + config.get('add_temperature', 0.0),
                    'stream': False,
                }
                task = asyncio.create_task(send_request(client, json_data, n))
                tasks.append(task)
              
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            
            # print(results)
            for result in results:
                if isinstance(result, Exception):
                    logging.error(f"Error in batch: {str(result)}")
                    all_answers.append(str(result))
                else:
                    all_answers.append(result)
    # print(all_answers)
    return all_answers



async def send_request(client, json_data, n):
    prompt_answers = []
    for _ in range(n):
        # try:
        response = await client.post(config['base_url'], headers=headers, json=json_data)
        # print("-----------")
        # print("response",response)
        result = response.json()
        # print(result)
        # ans = result['choices'][0]['message']['content']
        
#         print(result)
        ans = {
            'answer': result['choices'][0]['message']['content'],
            'reasoning': result['choices'][0]['message'].get('reasoning_content', '')
        }


        # 获取token统计信息
        prompt_tokens = result['usage']['prompt_tokens']
        completion_tokens = result['usage']['completion_tokens']
        total_tokens = result['usage']['total_tokens']
        
        prompt_price = prompt_tokens * price['prompt']
        completion_price = completion_tokens * price['completion']
        all_price = prompt_price + completion_price
        
        # 更新统计信息
        token_stats['total_prompt_tokens'] += prompt_tokens
        token_stats['total_completion_tokens'] += completion_tokens
        token_stats['total_tokens'] += total_tokens
        token_stats['prompt_price'] += prompt_price
        token_stats['completion_price'] += completion_price
        token_stats['total_price'] += all_price
        token_stats['requests_count'] += 1
        
        # 记录日志
        with open(price_log_path, 'a') as log_file:
            log_file.write(f"Request ID: {token_stats['requests_count']}\n")
            log_file.write(f"  Prompt tokens: {prompt_tokens}\n")
            log_file.write(f"  Completion tokens: {completion_tokens}\n")
            log_file.write(f"  Total tokens: {total_tokens}\n")
            log_file.write(f"  Prompt price: {prompt_price}\n")
            log_file.write(f"  Completion price: {completion_price}\n")
            log_file.write(f"  Total price: {all_price}\n")
            log_file.write("-" * 40 + "\n")
        
        prompt_answers.append(ans)
        
   
        # except Exception as e:
        #     error_msg = str(e)
        #     logging.error(f"Request error: {error_msg}")
        #     prompt_answers.append(error_msg)
            
        #     with open(price_log_path, 'a') as log_file:
        #         log_file.write(f"Request Error: {error_msg}\n")
        #         log_file.write("-" * 40 + "\n")
            
    return prompt_answers


# for vllm
# from openai import OpenAI
# async def send_request(client, json_data, n):
#     prompt_answers = []
#     reasoning_answers = []
#     for _ in range(n):
#         client = OpenAI(
#             api_key=config['api_key'],
#             base_url=config['base_url']
#         )
        
#         result = client.chat.completions.create(
#             messages=json_data['messages'],
#             model=json_data['model'],
#             temperature=json_data['temperature']
#         )
        
#         # ans = result.choices[0].message.content
#         # reasoning = result.choices[0].message.reasoning_content
    
#         ans = {
#             'answer': result.choices[0].message.content,
#             'reasoning': result.choices[0].message.reasoning_content if hasattr(result.choices[0].message, 'reasoning_content') else ''
#         }
        
#         usage = result.usage
#         prompt_tokens = usage.prompt_tokens
#         completion_tokens = usage.completion_tokens
#         total_tokens = usage.total_tokens
        
#         prompt_answers.append(ans)
        
#     return prompt_answers


def save_json(data, file_name):
    json_data = json.dumps(data, indent=2, ensure_ascii=False)
    with open(file_name, 'w') as file:
        file.write(json_data)
    file.close()

def split_into_batches(input_list, batch_size):
    for i in range(0, len(input_list), batch_size):
        yield input_list[i:i + batch_size]

async def process_tasks(input_path):
    try:
        with open(input_path, 'r') as f:
            dataset = json.load(f)[config['start']: config['end']]
    except:
        with open(input_path, 'r') as f:
            dataset = json.load(f)
    
    current_dataset_ids = [d['id'] for d in dataset]



    try:
        with open(output_file, 'r') as f3:
            results = json.load(f3)
            logging.info(f'Loaded results: {len(results)}')
            
            print('loaded: ', len(results))
            
            results  = [d for d in results 
                            if d['generated_answer'] != '' and 'Expecting value: line 1 column 1 (char 0)' not in d['generated_answer'] and d['generated_answer'] != "All connection attempts failed"] 
            
            
            ####################### 保留答案中的正常输出
           
            
            results  = [d for d in results 
                        if d['generated_answer'] != '' and 
                        "'choices'" not in d['generated_answer'] and "Error code: 400" not in d['generated_answer'] and "Error code: 500" not in d['generated_answer'] and 
                        'All connection attempts failed' not in d['generated_answer'] 
                        and 'aiserver.v1.ErrorDetails' 
                        not in d['generated_answer']] # 保留答案中的正常输出
            
            #######################
            
            
            
            results = [d for d in results if d['id'] in current_dataset_ids] 
            
            logging.info(f'Filtered results (valid data): {len(results)}')
        
    except:
        results = []
        logging.info('No existing results found')
    
    processed_id = [d['id'] for d in results ]
    
    logging.info(f'Total dataset size: {len(dataset)}')
    logging.info(f'Already processed: {len(processed_id)}')
        
    print(len(dataset))
    print('processed: ' , len(processed_id))
    
    dataset = [d for d in dataset if d['id'] not in processed_id]
    
    print(f'to be processed: {len(dataset)}')
    
    logging.info(f'To be processed: {len(dataset)}')
    
    messages = build_messages(dataset, use_system_prompt=True) 

    tasks = []
    total_batches = len(list(split_into_batches(messages, config['batch_size'])))
    pbar = tqdm(total=total_batches, desc="Processing batches")

    # 添加的计数器和保存频率设置
    processed_requests = 0
    save_frequency = 500  # 每处理500个请求保存一次
    
    for batch_idx, batch in enumerate(split_into_batches(messages, config['batch_size'])):
        task = asyncio.create_task(get_batch_response_with_retry(batch, n=config['n']))
        tasks.append(task)
        
        # 分批处理以便更频繁地保存
        if len(tasks) >= 10 or batch_idx == total_batches - 1:  # 每次处理10个批次或最后一批
            response_message_batches = await asyncio.gather(*tasks)
            tasks = []  # 重置任务列表
            
            for i, response_message_batch in enumerate(response_message_batches):
                pbar.update(1)
                start_index = (batch_idx - len(response_message_batches) + i + 1) * config['batch_size']
                for j, answer in enumerate(response_message_batch):
                    dataset_index = start_index + j
                    if dataset_index < len(dataset):
                        try:
                            dataset[dataset_index]['generated_answer'] = answer
                            # dataset[dataset_index]['reasoning'] = answer[0]['reasoning']
                        except:
                            dataset[dataset_index]['generated_answer'] = str(answer)
                            # dataset[dataset_index]['reasoning'] = ''
                
                results.extend(dataset[start_index:start_index + len(response_message_batch)])
                processed_requests += len(response_message_batch)
                
                # 每处理'save_frequency'个请求或在最后保存一次结果
                if processed_requests >= save_frequency or (batch_idx == total_batches - 1 and i == len(response_message_batches) - 1):
                    save_json(results, output_file)
                    logging.info(f'Saved progress: {len(results)} results processed')
                    processed_requests = 0  # 保存后重置计数器
    
    pbar.close()
    
    # 最终保存以确保所有内容都被存储
    save_json(results, output_file)
    logging.info(f'Final save: {len(results)} total results')
    
    # 记录最终统计信息
    log_token_stats()
    
    # messages = build_messages(dataset,                              use_system_prompt=True) 

    # tasks = []
    # total_batches = len(list(split_into_batches(messages, config['batch_size'])))
    # pbar = tqdm(total=total_batches, desc="Processing batches")

    # for batch in split_into_batches(messages, config['batch_size']):
    #     task = asyncio.create_task(get_batch_response_with_retry(batch, n=config['n']))
    #     tasks.append(task)
    
    # response_message_batches = await asyncio.gather(*tasks)

    # for i, response_message_batch in enumerate(response_message_batches):
    #     pbar.update(1)  
    #     start_index = i * config['batch_size']
    #     for j, answer in enumerate(response_message_batch):
    #         dataset_index = start_index + j
    #         if dataset_index < len(dataset):
    #             # print(answer)
    #             try:
    #                 dataset[dataset_index]['generated_answer'] = answer[0]['answer']
    #                 dataset[dataset_index]['reasoning'] = answer[0]['reasoning']
             
                    
    #             except:
    #                 dataset[dataset_index]['generated_answer'] = str(answer)
    #                 dataset[dataset_index]['reasoning'] = ''
                   

    #     results.extend(dataset[start_index:start_index + len(response_message_batch)])

    #     save_json(results, output_file)
            
    # pbar.close()  
    
    # # 记录最终统计信息
    # log_token_stats()


async def main():
    
    with open(price_log_path, 'w') as log_file:
        log_file.write(f"Token statistics for model: {model_name}\n")
        log_file.write(f"Date: {datetime.now()}\n")
        log_file.write("=" * 50 + "\n\n")
        
        
    await process_tasks(input_file)
    
    
if __name__ == "__main__":
    
    # asyncio.run(main())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
        
    with open(price_log_path, 'a') as log_file:
        log_file.write(f"Date: {datetime.now()}\n")