from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json

cloud_config = {
  'secure_connect_bundle': 'secure-connect-chooseDB.zip'
}

with open("chooseDB-token.json") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_DB_KEYSPACE = "databse"
OPENAI_API_KEY = "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"

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

template = """
You are the guide of a troubled farmer who is the head farmer at a magical potato farm. 
One day an young farm apprentice named Spud finds his way to the farm to help the head farmer. 
The apprentice is tasked with making all of the potatoes in the farm turn from rotten to healthy and edible. 
You must navigate him through challenges, choices, and consequences, dynamically adapting the tale based on the apprentice's decisions. 
Your goal is to create a branching narrative experience where each choice leads to a new path, ultimately determining Spud's fate and the troubled farmer. 

Here are some rules to follow:
1. Start by asking the player to choose some kind of tools or equipment that iwll be used later in the game
2. Have a few paths that lead to success
3. Have some paths that lead to failure. Failure looks like all the potatoes dying and turning rotten and the farm going out of business. If the player fails, generate a response that explains the failure and ends in the text: "The end.", I will search for this text to end the game. 

Here is the chat history, use this to understand what to say next: {chat_history}
Human: {Human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    prompt=prompt,
    llm=llm,
    memory=cass_buff_memory
)

choice = "start"

while True:
    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    if "The End." in response:
        break

    choice = input("Your reply: ")