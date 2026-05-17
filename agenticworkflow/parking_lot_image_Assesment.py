
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


image_files= ["parking_1.png" , "parking_2.png"]

for image in image_files:

    with open(image, "rb") as f:
        image_bytes = base64.standard_b64encode(f.read()).decode("utf-8")

        messages=[]
        addMsgToHistory(messages,
            [
                {
                    "type": "input_text",
                    "text": prompt
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{image_bytes}"
                    # "image_url": "https://media.istockphoto.com/id/1181862816/photo/aerial-shot-of-crowded-parking-with-many-cars-near-the-supermarket-view-from-above-many-cars.jpg?s=2048x2048&w=is&k=20&c=HL32Cf78Eypy-oe9dJG8E2D5iBi7-nJDsfKEyFgepsw="
                }
            ]
            , "user")
        response=askBot(messages,maxT=50)
        safe_messages = copy.deepcopy(messages)

        for msg in safe_messages:
            if isinstance(msg.get("content"), list):
                for block in msg["content"]:
                    if block.get("type") == "input_image":
                        block["image_url"] = "[IMAGE_DATA_REMOVED]"
        writeToFile(safe_messages, fDir="output/parking_result.txt")