ask_user_prompt = """As an agent responsible for defining the scope of a task for an autonomous AI system, your task is to gather necessary information from the user by asking relevant questions about their query. Please use the following user query to generate refining questions:

{user_query}

Please output your refining questions as a JSON object in the following format:
{{"questions": ["question1", "question2", ...]}}

These refining questions will help us establish the scope of the project, which should contain the requirements and constraints for the user's goal.
Your output should only contain the JSON object and no additional text!"""

retrieve_requirements_prompt = """As an agent responsible for defining the scope of a task for an autonomous AI system, your task is to extract the requirements needed to achieve the following user goal based on the answers provided to the refining questions:

User goal: {user_goal}
Answers: {answer}

Please output the extracted requirements as a JSON object in the following format:
{{
    "requirements": [
        "requirement1",
        "requirement2",
        ...
    ]
}}

Make sure to strictly follow this format and not include any additional text in your response. These extracted requirements will be used to establish the scope of the project."""

retrieve_goal_prompt = """As an AI agent responsible for retrieving the user's goal for an autonomous system, your role is to extract the user's main goal from the provided user query and represent it as a JSON object.

Given the following user query: "{user_query}", your task is to identify and extract the user's main goal, which represents their desired outcome or intention within the context of the AI agent system.

Please output the user goal as a JSON object in the following format:
{{
    "user_goal": "user_goal_here"
}}

Ensure that the extracted user goal accurately reflects the main objective expressed in the user query. Preserve all the information from the query without omitting anything, capturing the essence of the user's intention. Your response should strictly follow the JSON format and exclude any additional text.

Keep in mind that the extracted user goal will be utilized by the AI agent system to orchestrate the autonomous tasks accordingly.
Your output should only contain the JSON object and no additional text!
{validation_instructions}"""

validate_scope_prompt = """Please review the following requirements for the user goal: {user_goal}

Here is the history of the questions and answers that were asked to the user: {history}

Here are the requirements that were extracted from the user's answers: {scope}

Please provide your feedback on whether the requirements are complete and accurate. If you think additional refinement or clarification is needed, please include specific suggestions in the feedback message field.

Output your feedback as a JSON object in the following format:

{{
  "feedback": {{
      "success": true/false,
      "message": "Your feedback message here"
      }}
}}
Your output should only contain the JSON object and no additional text!"""

describe_scope_prompt = """Generate a coherent description of these requirements for the user goal {user_goal}: {scope}
You MUST include all the information from the user's goal and scope in your description, without adding any additional information.
{validation_instructions}"""

create_plan_prompt = """As the planner for an autonomous AI system, create a plan to achieve the following goal: {description}

You MUST output the plan as a JSON object in the following format:

{{
  "plan": {{
    "step_1": "description_1",
    "step_2": "description_2",
    ...
  }}
}}

Your output should only contain the JSON object and no additional text!
{validation_instructions}"""

update_plan_prompt = """As the planner for an autonomous AI system, update the plan based on the current scope, previous plan, and feedback from the task handler.

The current scope is as follows:
{scope}

The previous plan is as follows:
{previous_plan}

The feedback received from the task handler is as follows:
{feedback}

You may refine the plan based on the feedback, but note that the overall structure of the plan should remain the same.

You MUST output the plan as a JSON object in the following format:

{{
  "plan": {{
    "step_1": "description_1",
    "step_2": "description_2",
    ...
  }}
}}

Your output should only contain the JSON object and no additional text!
{validation_instructions}"""

tool_selection_prompt = """As the tool selector for an autonomous AI system, select the best tool or combination of tools to accomplish the following step:

{step}

Based on the step description, the following candidate tools have been identified as potentially suitable for this task:

{candidate_tools}

After careful consideration, please choose the tool that you believe would work best for this task, create a feedback object with an explanation of your thought process. Output your selection as a JSON object in the following format:

{{
  "tool": "tool_name", 
  "feedback": {{
    "success": true/false, 
    "message": "feedback_message"
    }}
}}

If none of the candidate tools would be suitable for this task, please output a feedback object with the success field set to False and an explanation of why the task cannot be accomplished with the given tools.

Similarly, if you think the step should be accomplished with a combination of tools, please output a feedback object with the success field set to False and an explanation of why the task cannot be accomplished with a single tool.

Make sure to strictly follow these formats and not include any additional text in your response.
{validation_instructions}"""

turn_to_action_prompt = """As the operator for an autonomous AI system, turn the following step into an action by providing the necessary input to the selected tool:

Step: {step}

Tool Descriptions:
{tool_descriptions}

Using the selected tool, provide an input to complete the step, and output the result as a JSON object in the following format:

{{
  "action": {{
    "tool_input": "input_here"
    }},
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
    }}
}}

Make sure to strictly follow this format and not include any additional text in your response. If the tool(s) cannot be used to complete the step, set the `success` field in the feedback object to `False` and provide an explanation in the `message` field.
{validation_instructions}"""

validate_scope_description_prompt = """As the validator for an autonomous AI system, your role is to review and assess the description of the project's scope generated by another AI agent. Your objective is to provide feedback on the completeness, accuracy, and coherence of the description. The scope description should include all the necessary information derived from the user's goal and requirements while avoiding any additional information.

Given that the description is generated by an AI language model (LLM), it's important to exercise critical thinking and consider potential pitfalls. LLMs may sometimes produce descriptions that are overly verbose, include unnecessary details, or lack clarity. As a validator, it is your responsibility to identify and address these issues to ensure a clear and concise scope description.

You will be provided with the following inputs:
- User Goal: "{user_goal}"
- Requirements: {scope}

The AI agent generated the following description of the scope of the project:
{description}

Your task is to carefully evaluate the generated scope description and provide feedback in the form of a JSON object with the following structure:

{{
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
  }},
  "validation_instructions": "instructions"
}

If you consider the description to be complete and accurate, set the "success" field in the feedback object to true. Provide your thoughts on the description in the "message" field, highlighting its strengths and alignment with the user's goal and requirements. Set the "validation_instructions" field to an empty string.

If you find the description to be incomplete, inaccurate, or unclear, set the "success" field in the feedback object to false. In the "message" field, provide specific feedback on the description's shortcomings, addressing any issues related to verbosity, unnecessary details, or lack of clarity. In the "validation_instructions" field, include clear and actionable instructions on how the AI agent can improve the description in subsequent iterations. These instructions should guide the AI agent in refining the scope description, avoiding common LLM pitfalls, and ensuring clarity and conciseness.

Your expertise and critical thinking skills are essential in evaluating the scope description and providing constructive feedback. By addressing potential LLM pitfalls, you contribute to the improvement of the AI agent's capabilities in accurately representing the project's scope.

Utilize your knowledge and experience to assess the generated scope description from both a technical and user-oriented perspective. Your feedback and instructions will enhance the AI agent's ability to produce high-quality scope descriptions that align with the user's goals and requirements while avoiding unnecessary complexity or ambiguity.

Your output should only contain the JSON object and no additional text!"""

validate_goal_prompt = """As an AI agent responsible for validating the extracted user's goal, your role is to critically evaluate the accuracy and appropriateness of the goal extracted by the previous agent, which was generated by an AI language model (LLM). Your objective is to ensure that the extracted goal aligns with the user's intention and captures the essence of their desired outcome.

You will be provided with the following inputs:
- User Query: "{user_query}"
- Extracted User Goal: "{user_goal}"

Your task is to carefully assess the extracted user goal and provide feedback on its validity. Consider the following aspects during your evaluation:
- Relevance: Does the extracted goal accurately capture the main objective expressed in the user query?
- Completeness: Does the extracted goal include all the necessary information and important details from the user query?
- Clarity: Is the extracted goal clear, concise, and free from ambiguity?

Based on your evaluation, provide feedback in the form of a JSON object with the following structure:
{{
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
  }},
  "validation_instructions": "instructions"
}}

In the "feedback" field, set the "success" field to true if the extracted user goal is deemed valid and appropriate. Set it to false if there are concerns or room for improvement. In the "message" field, provide a brief explanation of your feedback.

If the extracted user goal is judged to need improvement (i.e., "success" is set to false), include relevant "validation_instructions" to guide the next iteration of the extraction process. These instructions should outline specific areas of improvement or provide guidance on how to refine the extracted goal.

Utilize your critical thinking skills, consider potential pitfalls of an LLM-generated output, and make an informed judgment based on the provided inputs. 

Remember this is only the first processing part of the user's query and details will be added later, just make sure that all the information is preserved and the essence of the user's intention is captured.

Your output should only contain the JSON object and no additional text!"""

validate_requirements_prompt = """As the validator for an autonomous AI system, your task is to review and validate the requirements associated with the user's goal. Your role is crucial in ensuring that the requirements are accurately captured and aligned with the intended outcomes.

Given the following inputs:
User Goal: {user_goal}
Requirements: {requirements}

Your objective is to provide feedback on the completeness, clarity, and coherence of the requirements. It is essential to carefully evaluate whether the extracted requirements effectively address the user's goal and provide a clear and concise set of guidelines for the autonomous AI system.

Please provide your feedback as a JSON object in the following format:

{{
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
  }},
  "validation_instructions": "instructions"
}}

If you consider the requirements to be complete and aligned with the user's goal, set the "success" field in the feedback object to true. In the "message" field, provide your thoughts on the requirements, highlighting their strengths and coherence with the user's goal. Set the "validation_instructions" field to an empty string.

If you find the requirements to be incomplete, unclear, or lacking coherence with the user's goal, set the "success" field in the feedback object to false. In the "message" field, provide specific feedback on the shortcomings of the requirements, highlighting areas that need improvement or clarification. In the "validation_instructions" field, include clear and actionable instructions on how to enhance the requirements to better align them with the user's goal. These instructions should guide the AI agent or the system in refining the requirements, ensuring they accurately capture the desired outcomes.

Your expertise in evaluating requirements is vital in driving the success of the autonomous AI system. By providing comprehensive feedback and actionable instructions, you contribute to the development of a robust system that effectively addresses the user's goal and achieves the desired results.

Exercise critical thinking and attention to detail to thoroughly review the requirements and ensure their accuracy and coherence. Consider the user's goal as the guiding principle and evaluate the requirements from both a technical and user-oriented perspective. Your feedback will empower the AI agent or the system to make informed decisions and drive the project's success.

Your output should only contain the JSON object and no additional text!"""

prompts = {'ask_user': ask_user_prompt,
    'retrieve_requirements': retrieve_requirements_prompt,
    'retrieve_goal': retrieve_goal_prompt,
    'validate_scope': validate_scope_prompt,
    'describe_scope': describe_scope_prompt,
    'create_plan': create_plan_prompt,
    'update_plan': update_plan_prompt,
    'tool_selection': tool_selection_prompt,
    'turn_to_action': turn_to_action_prompt,
    'validate_scope_description': validate_scope_description_prompt,
    'validate_goal': validate_goal_prompt,
    'validate_requirements': validate_requirements_prompt}
