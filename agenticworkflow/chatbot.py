#
'''
This is a sample proejct of basic connection to OPENAI API directly
message is a dic with role and content as user/assistant msg to keep the history
'''

from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime


#api key loading
load_dotenv()
client= OpenAI()
selected_model= "gpt-4o-mini"
maxToken=30


userQuery= "what's the most rewarding engineering major in 2026? answer shortly in one sentence"

def simpleQA ():
    response= client.chat.completions.create(
    model=selected_model,
    messages= [
        {
        "role":"user",
        "content": userQuery
        }
    ], max_tokens=maxToken)
    print(response.choices[0].message.content)

#calls openAPI and stores the result as assistance response into the history of chats

def askBot(messagesHist):

    response= client.chat.completions.create(
        messages=messagesHist, model=selected_model, max_tokens=maxToken)
    responseContent=response.choices[0].message.content
    # update the history
    addMsgToHistory(messagesHist, responseContent, "assistant")
    return responseContent

#this func prints result using stream using chunck of available events to improve latency and user experience
def askBotWithStreaming(messageHist):

    stream=client.chat.completions.create(
        messages=messageHist,model=selected_model, max_tokens=maxToken , stream=True)
    response=""
    for chunk in stream:
        #extract text
        content=chunk.choices[0].delta.content
        if content:
            response+=content
            print(content,end="",flush=True) # show content as it arrives contiguously
    # update the history
    addMsgToHistory(messagesHist, response, "assistant")
    return response

# helper function to update the history
def addMsgToHistory(messagesHist, content, role):
    messagesHist.append({"role": role, "content": content})





############################# Starting the main chatBot app #################
 # add a system instruction for the whole conversation from AI response to be brief
def chatDemo():
    messagesHist=[{"role": "system", "content": "Be concise. Answer in one or two sentences only."}]

    print("Starting chat with a bot. If you want to finish, type 'exit'")
    userQuery=input("> ")
    while(userQuery!="exit"):

        addMsgToHistory(messagesHist,userQuery ,"user")
        #result_1 = askBot(messagesHist)
        #print(result_1)
        askBotWithStreaming(messagesHist)
        userQuery = input("\n> ")

    #writing to a txt file
    with open ("output/chat_with_bot.txt", 'a') as file:
        currentT= datetime.now().strftime("%Y-%m-%d %H:%M")
        file.write(f"new chat\n Time: [{currentT}]\n")
        for entry in messagesHist:
            file.write(str(entry))
            file.write("\n")

        file.write( "\n")

    print("Conversation ended! Enjoy your day!")

chatDemo()