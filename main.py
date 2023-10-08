from typing import Union

from fastapi import FastAPI, Request

import openai, pandas as pd

openai.api_key = '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'


import sqlite3

conn = sqlite3.connect('llm') 
c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS results
          ([url] TEXT PRIMARY KEY, [chatgpt_response] TEXT)
          ''')
conn.commit()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test/{item_id}")
def test(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/crawl/{url:path}")
def crawl(url: str, request:Request):

	response = openai.ChatCompletion.create(
	model='gpt-3.5-turbo',
	messages=[{'role':'user','content':'¿Can you provide a user friendly name, a user friendly summary of the page in 2 sentences , 5 keywords, and a user friendly detailed summary, of the most relevant information, of the page '+url+'?'}])
	chatgpt_response = response['choices'][0]['message']['content']
	chatgpt_response = chatgpt_response.replace('"',"'")
	
	conn = sqlite3.connect('llm') 
	c = conn.cursor()            
	c.execute('''SELECT * FROM results WHERE url = "'''+url+'''"''')
	df = pd.DataFrame(c.fetchall(), columns=['url','chatgpt_response'])
	conn.commit()

	if df.shape[0] > 0:
		return {
		"chatgpt_response": df['chatgpt_response'].iloc[0]
		}
	else:
		conn = sqlite3.connect('llm') 
		c = conn.cursor()  
		query = '''INSERT INTO results (url, chatgpt_response) VALUES ("'''+url+'''","'''+chatgpt_response+'''")'''  
		print("Insert Query")
		print(query)              
		c.execute(query)
		conn.commit()
		return {"chatgpt_response": chatgpt_response}

@app.get("/data/{url:path}")
def crawl(url: str, request:Request):

	conn = sqlite3.connect('llm') 
	c = conn.cursor()            
	c.execute('''SELECT * FROM results WHERE url = "'''+url+'''"''')
	df = pd.DataFrame(c.fetchall(), columns=['url','chatgpt_response'])
	conn.commit()

	print(df)
	if df.shape[0] > 0:
		return {
		"chatgpt_response": df['chatgpt_response'].iloc[0]
		}
	else:
		suggest_url = "/crawl/"+url
		return {"message":"We have not processed that dataset yet. You can do it by entering the URL of the dataset in this endpont: "+suggest_url}
