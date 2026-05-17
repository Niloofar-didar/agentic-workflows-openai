'''
In this project, we use AI run a data analysis on a csv file.
The csv file includes work related data of software engineers, and I wanted to analyze the reason behind
employees tickets_completed count compared to each other. The output of this project is some analytical graphs stored in output
'''

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import copy
from openai import OpenAI
load_dotenv()
client= OpenAI()
selected_model= "gpt-4o-mini"
maxToken=65
# Adds the parent directory to import methods of code_assistant into this class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from code_assistant import  addMsgToHistory,writeToFile,askBotWithTool
# Load env variables and create client


def upload(file_path):
    return client.files.create(
        file=open(file_path, "rb"),
        purpose="assistants"
    )

def list_files():
    return client.files.list()


def delete_file(id):
    return client.files.delete(id)


def download_file( container_id, file_id, output_path):

    content = client.containers.files.content.retrieve(
        container_id=container_id,
        file_id=file_id
    )


    with open(output_path, "wb") as f:
        f.write(content.read())


def get_generated_files(response):
    generated_files = []

    for item in response.output:
        if item.type == "code_interpreter_call":
            container_id = item.container_id

            files = client.containers.files.list(
                container_id=container_id
            )

            for f in files.data:
                generated_files.append({
                    "file_id": f.id,
                    "container_id": container_id,
                    "filename": getattr(f, "filename", None)
                })

    return generated_files

################### run analysis on CSV file#####################
file="input/se_productivity_dataset.csv"
uploaded_file= upload(file)


messages = []
prompt="""
Run an analysis to determine major drivers of tickets_completed count.
Your final output should include up to detailed plots using matplotlib summarizing your findings very concisely.
Critical note: Every time you execute code, you're starting with a completely clean slate.
After saving the figure, reply only:DONE. no more words.
"""

# prompt = """
# Read the uploaded CSV. Create a scatter plot of tickets_completed vs coding_hours_week using matplotlib.
# Save the figure to /mnt/data/plot.png. After saving, reply only:DONE. no more words.
# """

tools=[
           {
                "type": "code_interpreter",
                "container": {
                    "type": "auto",
                    "file_ids": [uploaded_file.id]
                }
            }
        ]

addMsgToHistory(
    messages,
    [{
      "type": "input_text",
      "text": prompt,
        }],"user")

response= askBotWithTool(messages, tool=tools, responseAPI=True, maxT=450,model="gpt-4o")
print(response.output_text)
print(response.output)

generated_files= get_generated_files(response)
print(generated_files)

#generated_files=[{'file_id': 'cfile_6a0a21fbc9948191a86105c262be65c4', 'container_id': 'cntr_6a0a21fa1d8c81908e79d733135305430268efc2a8e4aeb0', 'filename': None}, {'file_id': 'cfile_6a0a21fbc9948191a86105c262be65c4', 'container_id': 'cntr_6a0a21fa1d8c81908e79d733135305430268efc2a8e4aeb0', 'filename': None}]
container_id=generated_files[0]["container_id"]
file_id=generated_files[0]["file_id"]

files = client.containers.files.list(
    container_id=container_id
)

for f in files.data:
    meta = client.containers.files.retrieve(
        container_id=container_id,
        file_id=f.id
    )

    print(meta.path, meta.source)



download_file(
    container_id=generated_files[0]["container_id"],
    file_id=generated_files[0]["file_id"],
    output_path="output/generated_plot.png"
)
