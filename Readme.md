# Collection of projects and experiments documenting my learning journey with LLMs.
This repository focuses on building practical applications using learnings from Claude (Anthropic) and implementation via OpenAI APIs.

## Requirements to Install
Run the following commands in your terminal to install the necessary libraries and set up your environment:

### 1. Install Dependencies
```bash
pip install openai langchain-openai langchain-core python-dotenv
```

### 2. Core Features
This setup enables the core LLM pipeline, including:
*   **Prompting:** Structuring inputs for the model.
*   **Context Injection:** Feeding data into the LLM.
*   **Response Parsing:** Formatting model outputs into usable data.

### 3. Environment Setup
1.  Get an **API key** from [OpenAI](https://openai.com).
2.  Create a `.env` file in your project root.
3.  Add your key to the file:
    ```text
    OPENAI_API_KEY=your_api_key_here
    ```


## Projects I Started With (In Order)

---<img width="3782" height="2234" alt="agent-time-calculator" src="https://github.com/user-attachments/assets/b79f1d36-46c4-4225-9223-260fca63c509" />


1- **chatBot.py**
This is a chatBot that connects to OpenAPI directly and answers user's input question while saving the history of conversation.
The conversation sample are published into chat_with_bot.txt. I've limited the max_token to 30, that's why some answers may be incomplete! 
in the following a demo is shown:

https://github.com/user-attachments/assets/21a91def-5a71-4f7d-86b3-e93c06c49622

2- **code_assistant.py**
This is to enable generating codes, and sample dataSet (json files) for prompt quality validation.

3- **prompt validation*** 
feeding the dataset of code_assistant into OPNEN_AI, we want to run an evaluation on the prompt quality.
Each response will be graded and compared to another round of prompt generation. the purpose is to train and generate a better prompt 
that results in a result with higher quality. i.e., higher score. The overview of this project is shown in the following, with dataset on left, AI model that process the input and generates results and result at right.

<img width="744" height="234" alt="image" src="https://github.com/user-attachments/assets/9f275f4b-e84c-4833-aeb1-a7a3724c3e89" />


The grading system is done using the two approaches: 1-code format evaluator leveraging python packages to check the output format, and 2- using AI system for grading the result with a scale of 1-10.
The test results sample is as below, also provided in output/prompt_evaluation.json.

```json
{
  "score": 8.5,
  "reasoning": "Effectively identifies valid emails overall",
  "test_case": {
    "task": "Extract email addresses from a list of consumer emails.",
    "format": "python"
  },
  "output": "import re;emails=[\"example1@example.com\",\"not_an_email\",\"test@email.com\",\"hello@world.com\"];valid_emails=[email for email in emails if re.match(r\"[^@]+@[^@]+\\.[^@]+\",email)];print(valid_emails)"
}
```

** 4- A reminder Tool - Connectivity to external services  **
For some applications, AI may not know the exact solution or may require extra info to act upon. For instance, if we ask AI to remind us in 4 hours, it requires accessing some tools such as the current datetime, calculating the alarm time from now (duration), and a reminder set to send the user and alert.
For that, in our server we need to enable a tool on our server. We start with creating a tool to calculate the time, we use an schema to show AI models how the tools work. The AI model generates the expected input, sent it back to our server, then in our server, we run the built tool and reply to AI model with the result and the expected output format. The tools we used include current date time calculator, duration addition to current time, and timer setter which is a simple function that prints the result to the user.
Finally, the AI model generates the final output to be shown to the end user as shown in the following.

<img width="2790" height="1348" alt="reminder app" src="https://github.com/user-attachments/assets/1cb91956-2c9c-47e8-a034-a037e7e78141" />

This flow is shown through the image below taken from https://anthropic.skilljar.com/claude-with-the-anthropic-api/287752

<img width="1920" height="1080" alt="img_1" src="https://github.com/user-attachments/assets/ae24a73a-615e-44c7-b65a-7f9a7e4ea916" />


Here is a demo of the interactive UI I implemented and shows the use of two Tools to respond to my prompt.

https://github.com/user-attachments/assets/8a65e74b-83b8-4fcf-933e-c155b4fc6526

5- Multi-Index Rag Pipeline:
In this project, we create a multi-index rag pipeline that answers to the user's question based on a report.md file in an efficient way.
We create two search methods: 1-semantic search (vector Index) and 2-texted-based search (BM25 Index) that finds the most closet section of the report to user's question.
For chunking the report file, we use section-based method because the file structure has an appropriate marks to separate the sections.

