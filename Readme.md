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
---

## Projects I Started With (In Order)
1.  **Project One Name** - Short description.
2.  **Project Two Name** - Short description.


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
},
```
