# This is a sample Python script.

from typing import Optional
from collections import Counter
import random
from fastapi import FastAPI
import asyncpg
import redis

app = FastAPI()

@app.get("/anagrams/{text_1,text_2}")
def check_anagrams(text_1: str, text_2: str):
    r = redis.Redis(host='redis', port=6379, db=0)
    if Counter(x for x in text_1.lower() if x.isalpha()) == Counter(x for x in text_2.lower() if x.isalpha()):
        counter=r.incr('anagrams')
        r.close()
        return {'are_anagrams?': True, 'counter': counter}
    else:
        counter = int(r['anagrams'])
        r.close()
        return {'are_anagrams?': False, 'counter':counter }


@app.post("/add_10_devices/", status_code=201)
async def create_item():
    conn = await asyncpg.connect(host='db',user='postgres',
    password='12345',
    database='postgres')
    r = redis.Redis(host='redis', port=6379, db=0)
    device_list_types = ['emeter', 'zigbee', 'lora', 'gsm']

    for i in range(5):
            dev_id = bytearray(random.sample(range(0, 255), 6)).hex()
            dev_type = random.choice(device_list_types)
            await conn.fetchval('''
                INSERT INTO devices(dev_id, dev_type) VALUES($1, $2)
            ''', dev_id, dev_type)

    for i in range(5):
            dev_id = bytearray(random.sample(range(0, 255), 6)).hex()
            dev_type = random.choice(device_list_types)
            id= await conn.fetchval('''
                INSERT INTO devices(dev_id, dev_type) VALUES($1, $2) RETURNING id
            ''', dev_id, dev_type,  column=0)
            await conn.execute('''
                        INSERT INTO endpoints (device_id, comment) VALUES($1, $2) RETURNING id
                    ''', id, random.choice("abcde"))
    r.close()
    await conn.close()


@app.get("/devices_without_endpoints/")
async def get_devices_without_endpoints():
    conn = await asyncpg.connect(host='db',user='postgres',
    password='12345',
    database='postgres'
    )
    data = await conn.fetch(
        'SELECT dev_type, count(dev_type) FROM devices WHERE Id NOT IN (SELECT device_id FROM endpoints) GROUP BY dev_type')
    # Close the connection.
    await conn.close()
    return data


