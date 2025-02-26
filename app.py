import streamlit as st
from openai import OpenAI

from pydantic import BaseModel

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit UI
st.title("LLM Judge 🎓")
st.write("Submit your response and let the AI evaluate it!")

# Input fields
criteria = st.text_area("Enter evaluation criteria", """Here is what we are looking for:
        - The code review should point out that the _check_role() method is duplicated
        - The code review should point out the error in get_neighbors where ni <= len(self.grid) and nj <= len(self.grid[ni])
        - The code review should point out that in simulate_irrigation(), the for loop order is inefficient and also wrong.
        - The code review should point out that hard-coding api keys is never a good idea.
        - The code review should be clear and concise.
        """)
base_code = st.text_area("Enter base code", "Provide the base code.")
llm_response = st.text_area("Enter the submission to evaluate", "The capital of France is Paris.")

class TaskData(BaseModel):
    judge_response: str

class LLMJudge(TaskData):
    score: str


def get_review(prompt, system_message, response_format):
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    system_message
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format=response_format,
    )

    return response.choices[0].message.parsed

if st.button("Evaluate"):
    with st.spinner("Evaluating..."):
        system_prompt = """
        You are a strict but fair judge. Please rate the quality of the code review for the above python code. The reviewer was asked to look especially for things like this:
         - Bad practices
         - Security vulnerabilities
         - Clear inefficiencies
         - Bugs
        And the reviewer was asked to highlight only the most obvious and clearest points that would definitely be mentioned in a good code review.
        The things we are looking for will be provided as evaluation criteria 
         
        Each of the points is worth a maximum of 2 points. Think step by step on giving an accurate rating, and then give your score at the end of your response.
        """
        response_format = LLMJudge

        prompt = str({
            'base_code': base_code,
            "evaluation_criteria": criteria,
        })

        response = get_review(prompt, system_prompt, response_format)

        result = response
        st.subheader("Evaluation Result:")
        st.write(result)
