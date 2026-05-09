'''
This project leverages the dataset (json tasks) created in code_assistant to run an evaluation on the prompt quality.
Each response will be graded and compared to another round of prompt generation. the purpose is to improve the prompt quality.
'''


from openai import OpenAI
from dotenv import load_dotenv
import json
from code_assistant import askBot,writeToFile,addMsgToHistory,writeToDataset
import re
import ast


#api key loading
load_dotenv()
client= OpenAI()
selected_model= "gpt-4o-mini"
maxToken=60

#input is json format testCase
def run_prompt(test_case):

    prompt=f"""solve the following task: 
    {test_case["task"]}
    * respond only with python or json"""

    # this is to control the code generation lenghth and quality, force minified Json
    messagesHist  =[{"role": "system", "content":  "you're a raw code generator."
                                                   "Output ONLY the code.Do NOT use markdown code blocks (no ```). No headers, no footers. no newlines, no indentation, no whitespace between keys and values.No explanations, no comments"}]

    addMsgToHistory(messagesHist, prompt,"user" )

    result= askBot(messagesHist,responseFormat=None, maxT=maxToken)
    #result='import re;emails=["alice@example.com","bob'
    return result

#grading system using AI
def gradeByAIModel(testcase,output):
    eval_prompt = f"""
    You are an expert developer. Your task is to evaluate the following AI-generated solution.
    Original Task:
    <task>
    {testcase["task"]}
    </task>

    Solution to Evaluate:
    <solution>
    {output}
    </solution>

    Output Format
    Provide your evaluation as a structured JSON object with the following fields, in this specific order:
    - "strengths": An array of 1 key strength up to 10 words
    - "weaknesses": An array of 1 key area for improvement up to 10 words
    - "reasoning": up to 10 words of your overall assessment
    - "score": A number between 1-10

    Respond with JSON. Keep your response concise and direct. No headers, no footers. no newlines, no indentation, no whitespace between keys and values.
    Example response shape:
    {{
        "strengths": string[],
        "weaknesses": string[],
        "reasoning": string,
        "score": number
    }}
        """

    messages = []
    addMsgToHistory(messages, eval_prompt,"user")

    eval_text = askBot(messages,responseFormat=None,maxT=None)
    #eval_text= '{"strengths": ["Uses regex for email validation"], "weaknesses": ["Does not handle edge cases effectively"],"reasoning": "Overall, a basic but functional solution.","score": 7}'
    return json.loads(eval_text)



def gradeBySyntax(response,testCase):
    format=testCase["format"]
    if format=="json":
        return validate_json(response)

    if format=="regex":
        return validate_regex(response)
    if format=="python":
        return validate_python(response)

# calls runPrompt and gather result along with score and input in a dic
def run_testcase_and_rank(test_case):

    output = run_prompt(test_case)
    print(str(output))

    # score
    model_grade=gradeByAIModel(test_case,output)
    model_score=model_grade["score"]
    reasoning=model_grade["reasoning"]

    syntaxScore=gradeBySyntax(output,test_case)

    score=(model_score+syntaxScore)/2
    return {
        "score":score,
        "reasoning":reasoning,
        "test_case" :test_case,
        "output":output
    }



######### code validator, this checks if the response form AI models aligns with the correct format using the corresponding text reader packages

def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0

def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0

def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0



############### Main evaluation mehtod that takes the dataset and runs testCase to retrieve response and ranks it
def run_evaluation(dataset):

    final_result=[]
    for task in dataset["tasks"]:
       result=run_testcase_and_rank(task)

       print(str(result))
       writeToDataset( result, fileDir= 'output/prompt_evaluation.json')
       final_result.append(result)


    return final_result

### running evalation

with open("output/dataset.json", 'r') as file:

    dataset=json.load(file)
    result= run_evaluation(dataset)
