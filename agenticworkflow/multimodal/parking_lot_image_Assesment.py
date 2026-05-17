import sys
import os

# Adds the parent directory to import methods of code_assistant into this class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from code_assistant import  addMsgToHistory,writeToFile
# Load env variables and create client
import base64
from dotenv import load_dotenv
import copy
from openai import OpenAI
load_dotenv()
client= OpenAI()
selected_model= "gpt-4o-mini"
maxToken=65


prompt="""analyze the attached parking lot image considering below factors: 1-estimate approximate parking occupancy. 
2- Identify visible vehicle categories such as sedans, SUVs, trucks, or motorcycles. 3- Note any unusual parking 
patterns or congestion. 4-Estimate overall parking organization on a scale of 1-4: 1 =  very organized 2 = minor 
congestion 3 = significant congestion 4 = sever congestion or safety concerns and as the response only give 
score:score_value and only say one sentence about the score reasoning. Keep the response concise. """




def askBot(messagesHist, maxT=None):

    response = client.responses.create(
        model=selected_model,
        input=messagesHist,
        max_output_tokens=maxT if maxT else maxToken
    )

    responseContent = response.output_text

    addMsgToHistory(messagesHist, responseContent, "assistant")

    return responseContent

from pathlib import Path




def process_file(multimodal_files, file_type,media_type ):


    if isinstance(multimodal_files, str):
        multimodal_files = [multimodal_files]

    for file in multimodal_files:
        file_addr = Path(file).stem

        with open(file, "rb") as f:
            file_bytes = base64.standard_b64encode(f.read()).decode("utf-8")
            if file_type == "input_image":
                file_block = {
                    "type": "input_image",
                    "image_url": f"data:{media_type};base64,{file_bytes}"
                }

            elif file_type == "input_file":
                file_block = {
                    "type": "input_file",
                    "filename": Path(file).name,
                    "file_data": f"data:{media_type};base64,{file_bytes}"
                }
            else:
                raise ValueError("file_type must be 'input_image' or 'input_file'")

            messages=[]
            addMsgToHistory(messages,
                [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    file_block
                ]
                , "user")

            response=askBot(messages,maxT=50)
            #safe_messages = copy.deepcopy(messages)

            for msg in messages:
                if isinstance(msg.get("content"), list):
                    for block in msg["content"]:
                        if block.get("type") == "input_image":
                            block["image_url"] = "[IMAGE_DATA_REMOVED]"
                        elif block.get("type") == "input_file":
                            block["file_data"] = "[FILE_DATA_REMOVED]"

            writeToFile(messages, fDir=f"output/{file_addr}.txt")


################### starting the image process #####################

#image_files= ["parking_1.png" , "parking_2.png"]
# process_file(image_files,type= "input_image", media_type="image/png")
prompt="very concisely and through one sentence tell me what is this file about?"
file=["human_ev.pdf"]
process_file(file,file_type= "input_file", media_type="application/pdf")

#type=input_file media=application/pdf