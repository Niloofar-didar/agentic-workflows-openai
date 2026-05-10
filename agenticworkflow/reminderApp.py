'''

create a reminder app:
1-need to calculate the current time
2-add duration to it
3-a reminder tool

- tool schema (get_current_datetime_schema) shows AI the available tools to it and how to call these tools
- AI finds the input to the tool using schema, and the code runs the tool (get_current_date), and passes the result to AI for final resposne
'''
from datetime import datetime
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageFunctionToolCall, Function
import json

from openai.types.chat import ChatCompletionMessage

from code_assistant import askBotWithTool,addMsgToHistory,text_from_message, addMsgToHistoryGeneric, writeToFile,writeToDataset,askBotGeneric

def get_current_date(date_format="%Y-%m-%d %H:%M:%S"):

        if not date_format:
            raise ValueError("date_format cannot be empty")
        return datetime.now().strftime(date_format)

# the schema in below is taken from openAPI answer when shared the function above along with the best practices for tools in the website
get_current_datetime_schema = {
    "type": "function",  # This was the missing required parameter
      "function": {
        "name": "get_current_date",
        "description": "Returns the current date and time formatted according to the specified format",
        "parameters": {  # OpenAI uses 'parameters' instead of 'input_schema'
            "type": "object",
            "properties": {
                "date_format": {
                    "type": "string",
                    "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes.",
                    "default": "%Y-%m-%d %H:%M:%S"
                }
            },
            "required": []
        }
      }
}

def demo_1_use_tool_date_calculator():

    messages = []
    addMsgToHistory( messages,"What is the exact time, formatted as HH:MM:SS?","user")

    tools=[get_current_datetime_schema]
    assistant_msg=askBotWithTool(messages,responseFormat=None,maxT=40,tool=tools)


    if assistant_msg.tool_calls:
        for tool_call in assistant_msg.tool_calls:
            # Run the function, example of result: '09:15:14'
            result = get_current_date(**json.loads(tool_call.function.arguments))

            #  Add result to history with the tool_call_id
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        # SECOND Call: AI now has the info to actually talk
        # still the final req should include the tool schema so that AI-model understand the tool ref in the msg_history. eventhough the AI model isn't expected to make another tool call
        final_response = askBotWithTool(messagesHist=messages, responseFormat=None, maxT=None, tool=tools)

        #final_response=[{'role': 'user', 'content': 'What is the exact time, formatted as HH:MM:SS?'}, ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_LNXM0usJIR0hWEpr21ysq95Y', function=Function(arguments='{"date_format":"%H:%M:%S"}', name='get_current_date'), type='function')]), {'role': 'tool', 'tool_call_id': 'call_LNXM0usJIR0hWEpr21ysq95Y', 'content': '09:15:14'}, ChatCompletionMessage(content='The exact time is 09:15:14.', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None)]

        # 2. Convert to dic and Dump into json format
        clean_history = []
        for msg in messages:
            # Use model_dump for the objects , to convert to dic type
            if isinstance(msg, ChatCompletionMessage):
                 clean_history.append(msg.model_dump())
            else:
                clean_history.append(msg)

        writeToDataset(clean_history,"output/demo_1_use_tool_date_calculator.txt")


def process_raw_response_to_dic(messages):
    clean_history = []
    for msg in messages:
        # Use model_dump for the objects , to convert to dic type
        if isinstance(msg, ChatCompletionMessage):
            clean_history.append(msg.model_dump())
        else:
            clean_history.append(msg)
    return clean_history

## run any implemented tool and return the response
def run_tool(tool_name, tool_input):
    if tool_name == "get_current_date": # Matches your previous function name
        return get_current_date(**tool_input)


def run_tools(message):

    if not message.tool_calls:
        return []
    #store a dic result from running each tool
    tool_result=[]
    for tool_call in message.tool_calls:

        try:
            func_name=tool_call.function.name
            func_arg= tool_call.function.arguments
            # convert string to dictionary
            args = json.loads(func_arg)
            ## call the general run_tool method that runs the corresponding method that AI model needs
            response=run_tool(func_name,args)
            tool_result.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(response)
                }
            )

        # this is for AI model to know the reason behind the error to retry correctly next time
        except Exception as e:
            tool_result.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Error: {e}"
                }
            )

    return tool_result

## here is an autonomous loop between the server and AI model to find the final response user is looking for
"""we call the tools required by the bot unril """
def run_conversation(messages, tool,ui_callback=None):

    if ui_callback:
        ui_callback("System: AI is processing...")

    while True:

        ai_response = askBotGeneric(messages, tool=tool, maxT=50)

        addMsgToHistoryGeneric(messages, ai_response,"assistant")

        # 3. Print text if there is any
        content = text_from_message(ai_response)
        if content:
            print(f"AI: {content}")

        if ai_response.tool_calls:
            if ui_callback:
                ui_callback(f"System: AI is calling {len(ai_response.tool_calls)} tools...")

            print("AI is requesting tools...")
            tool_results = run_tools(ai_response)
            # add server response from calling the tool
            messages.extend(tool_results)
        else:
            #Safety break for other finish reasons like 'length' or 'content_filter'
            break

    #######
    response_dic_formatted = process_raw_response_to_dic(messages)
    return response_dic_formatted

def demo_2_autonomousToolUseByAI():
    message=[]
    addMsgToHistoryGeneric(message, "what is current time in HH:MM format? how about time in Y-M-d format? ","user")
    tool=[get_current_datetime_schema]
    response_to_user= run_conversation(message,tool)
    writeToDataset(response_to_user,"output/multi_Q_tool.json")

## test demo_2
#demo_2_autonomousToolUseByAI()