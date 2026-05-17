#
'''
This project is with regard to best practices to use openAPI for code/dataset generation


To avoid header and footer for AI response, you need to include it as assistant message and stop_sequence (stop in openAPI) for claude API so that
the API reads the beginning and assumes it's included, so it won't include the token
For openAPI as below, we choose response_format for getting the right format

'''

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json

#api key loading
from openai.types.chat import ChatCompletionMessage

load_dotenv()
client= OpenAI()
selected_model= "gpt-4o-mini"
maxToken=65

def askBot(messagesHist, responseFormat=None, maxT=None):

    apiParameter={
        "messages" : messagesHist,
        "model":  selected_model,
        "max_tokens" : maxToken}

    if responseFormat:
        apiParameter["response_format"]=responseFormat
    if maxT:
        apiParameter["max_tokens"]=maxT

    response= client.chat.completions.create(**apiParameter)
    responseContent=response.choices[0].message.content
    # update the history
    addMsgToHistory(messagesHist, responseContent, "assistant")
    return responseContent

def askBotWithTool(messagesHist, responseFormat=None, maxT=None, tool=None, responseAPI=None,model=None):


    responseContent =""
    if responseAPI:

        apiParameter = {
            "input": messagesHist,
            "model": selected_model,
            "max_output_tokens": maxT if maxT else maxToken
        }

        if tool:
            apiParameter["tools"] = tool

        if model:
            apiParameter["model"] = model

        response = client.responses.create(**apiParameter)

        responseContent=response
        addMsgToHistory(messagesHist, response.output_text, "assistant")

    else:

        apiParameter = {
            "messages": messagesHist,
            "model": selected_model,
            "max_tokens": maxT if maxT else maxToken
        }

        if responseFormat:
            apiParameter["response_format"] = responseFormat

        if tool:
            apiParameter["tools"] = tool

        response = client.chat.completions.create(**apiParameter)
        responseContent = response.choices[0].message
        # update the history
        messagesHist.append(responseContent)

    return responseContent

def askBotGeneric(messagesHist,system=None, temperature=1.0, responseFormat=None, maxT=None, tool=None):
    apiParameter = {
        "messages": messagesHist,
        "model": selected_model,
        "max_tokens": maxToken,
        "temperature": temperature}

    if responseFormat:
        apiParameter["response_format"] = responseFormat
    if maxT:
        apiParameter["max_tokens"] = maxT
    if tool:
        apiParameter["tools"] = tool
    if system:
        apiParameter["system"] = system

    response = client.chat.completions.create(**apiParameter)
    return response.choices[0].message

# extract the text
def text_from_message(message):
    # for OpenAI message object, take .content attribute
    if hasattr(message, 'content'):
        return message.content if message.content else ""

    # If it's already a string, return it
    if isinstance(message, str):
        return message

    return ""

# helper function to update the history
def addMsgToHistory(messagesHist, content, role):
    messagesHist.append({"role": role, "content": content})


def addMsgToHistoryGeneric(messagesHist, message, role):
    # Check if 'message' is the OpenAI object (similar to your Anthropic check)
    if isinstance(message, ChatCompletionMessage):
        # Extract the string content
        content_str = message.content

        # If you only want to save the string, you must check if it exists.
        if content_str is not None:
            messagesHist.append({"role": role, "content": content_str})
        elif message.tool_calls:
            # If content is empty but tools exist, save the whole object
            # otherwise the AI "chain of thought" breaks.
            messagesHist.append(message)
    else:
        # If it's already a string or a simple dict
        messagesHist.append({"role": role, "content": message})



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
    tasks= askBot(messages, responseFormat={ "type": "json_object" },maxT=None)
    json_output= json.loads(tasks.strip())
    writeToFile(messages, fDir="output/code_assistant.txt")
    writeToDataset(json_output, fileDir='output/dataset.json')
    return json_output

def writeToDataset(json_output, fileDir):
    with open (fileDir,'a') as f:
        if fileDir:
           f.write(',\n')  # Add comma before the next item
        json.dump(json_output,f,indent=2)

def jsonCreator(messagesHist):
    userQuery="generate a very short user profile info as json"

    addMsgToHistory(messagesHist,userQuery ,"user")
    result_1 = askBot(messagesHist, responseFormat={ "type": "json_object" },maxT=None) # This forces valid JSON)
    json_output= json.loads(result_1.strip())
    print(json_output)
    writeToFile(messagesHist, fDir="output/code_assistant.txt" )


def writeToFile (message, fDir):
    #writing to a txt file
    with open (fDir, 'a') as file:
      currentT= datetime.now().strftime("%Y-%m-%d %H:%M")
      file.write(f"\n Time: [{currentT}]\n")
      for entry in message:
           file.write(str(entry))
           file.write("\n")

      file.write( "\n")

def demo():
    ############################# Starting the main code generation assistant #################
    # this is to control the code generation lenghth and quality, force minified Json
    messagesHist = [{"role": "system", "content": "You're a python engineer who writes very concise code."
                " Output ONLY minified code. No newlines, no indentation, no whitespace between keys and values.No explanations, no comments"}]
    dataset= generate_dataset(messagesHist)

