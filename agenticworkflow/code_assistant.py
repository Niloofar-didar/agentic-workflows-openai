#
'''
This project is with regard to best practices to use openAPI for code generation

To avoid header and footer for AI response, you need to include it as assistant message and stop_sequence (stop in openAPI) for claude API so that
the API reads the beginning and assumes it's included, so it won't include the token
For openAPI as below, we choose response_format for getting the right format

'''

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json

#api key loading
load_dotenv()
client= OpenAI()
selected_model= "gpt-4o-mini"
maxToken=65

def askBot(messagesHist, responseFormat):

    apiParameter={
        "messages" : messagesHist,
        "model":  selected_model,
        "max_tokens" : maxToken}

    if responseFormat:
        apiParameter["response_format"]=responseFormat

    response= client.chat.completions.create(**apiParameter)
    responseContent=response.choices[0].message.content
    # update the history
    addMsgToHistory(messagesHist, responseContent, "assistant")
    return responseContent

# helper function to update the history
def addMsgToHistory(messagesHist, content, role):
    messagesHist.append({"role": role, "content": content})


def generate_dataset(messages):

    prompt = """
Generate an evaluation dataset for a prompt evaluation.
The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for 
personal email automation and data extraction task. Generate an array of JSON objects, each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
  {
    "task": "Description of task",
  },
  ...additional
]
```
generate 3 objects . Each 'task' description must be exactly one sentence and no more than 12 words."
"* Generate diverse tasks related to personal productivity, inbox organization, and extracting info from everyday consumer emails."
* the tasks should be solved by writing a single Python function, a single JSON object, or a single regex without requiring writing much code
"""
    addMsgToHistory(messages,prompt,"user")
    tasks= askBot(messages, responseFormat={ "type": "json_object" })
    json_output= json.loads(tasks.strip())
    writeToFile(messages)
    writeToDataset(json_output)
    return json_output

def writeToDataset(json_output):
    with open ('dataset.json','a') as f:
        json.dump(json_output,f,indent=2)

def jsonCreator(messagesHist):
    userQuery="generate a very short user profile info as json"

    addMsgToHistory(messagesHist,userQuery ,"user")
    result_1 = askBot(messagesHist, responseFormat={ "type": "json_object" }) # This forces valid JSON)
    json_output= json.loads(result_1.strip())
    print(json_output)
    writeToFile(messagesHist)


def writeToFile (message):
    #writing to a txt file
    with open ("output/code_assistant.txt", 'a') as file:
      currentT= datetime.now().strftime("%Y-%m-%d %H:%M")
      file.write(f"\n Time: [{currentT}]\n")
      for entry in message:
           file.write(str(entry))
           file.write("\n")

      file.write( "\n")


############################# Starting the main code generation assistant #################
# this is to control the code generation lenghth and quality, force minified Json
messagesHist = [{"role": "system", "content": "You're a python engineer who writes very concise code."
                " Output ONLY minified code. No newlines, no indentation, no whitespace between keys and values.No explanations, no comments"}]
dataset= generate_dataset(messagesHist)

#Load the data and write to File
#jsonfile=json.loads(dataset)
#dataset='{"tasks":[{"task":"Extract email addresses from a list of consumer emails."},{"task":"Filter emails containing receipts from a given date range."},{"task":"Convert email data to JSON format for easier processing."}]}'

writeToDataset(dataset)
