retrieve_goal_prompt = """As an AI agent responsible for retrieving the user's goal for an autonomous system, your role is to extract the user's goal from the provided user query. The goal represents the user's desired outcome or intention within the context of the autonomous AI system that will execute it.
You must only extract the goal from the user query, without omitting any information from the query. 

User query: {user_query}

Please output the user goal as a JSON object in the following format:
{{
    "user_goal": "user_goal_here"
}}

Ensure that the extracted user goal accurately reflects the main objective expressed in the user query. Preserve all the information from the query without omitting anything, capturing the essence of the user's intention. Your response should strictly follow the JSON format and exclude any additional text.

Keep in mind that the extracted user goal will be utilized by the AI agent system to orchestrate the autonomous tasks accordingly.
Your output should only contain the JSON object and no additional text!
{validation_instructions}"""

validate_goal_prompt = """Your task is to evaluate the goal extracted by another AI agent from the user query. The goal represents the user's desired outcome or intention within the context of the autonomous AI system that will execute it.
You must only validate if the extracted goal accurately reflects the main objective expressed in the user query. It must preserve all the information from the query without omitting anything, capturing the essence of the user's intention.

User Query: {user_query}
Extracted User Goal: {user_goal}

Remember that your job is only to evaluate the goal extracted by the previous agent based on the user query, so don't worry about the quality of the user query itself. You can assume that the user query is accurate and complete so don't provide feedback about it being more complete and needing more specifications about requirements or constraints, that is not your job.

Keep in mind that the goal is necessary in the context of an autonomous AI system that can perform tasks on behalf of the user. The goal is used to guide the system's actions and ensure that they are aligned with the user's intention. Therefore, it is crucial that the extracted goal accurately represents the user's intention and desired outcome.

Based on your evaluation, provide feedback in the form of a JSON object with the following structure:
{{
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
  }},
  "validation_instructions": "instructions"
}}

If you consider the extracted goal to be complete and aligned with the user query, set the "success" field in the feedback object to true. In the "message" field, provide a brief explanation of your feedback. Set the "validation_instructions" field to an empty string.

If you find the extracted goal to be incomplete, unclear, or lacking coherence with the user query, set the "success" field in the feedback object to false. In the "message" field, provide an explanation of your analysis on why it doesn't reflect the user query. In the "validation_instructions" field, include clear and actionable instructions on how to enhance the goal to better align it with the user query. These instructions should guide the AI agent in better capturing the user's intent.

Your output should only contain the JSON object and no additional text!"""


first_ask_user_prompt = """As an agent responsible for defining the scope of a task for an autonomous AI system, your task is to gather necessary information from the user by asking relevant questions about their goal. This goal is meant to be accomplished by an autonomous AI system that is capable of performing a variety of tasks.
You must only focus on creating questions to retrieve requirements about the contract between the user and the project, not the implementation details as the planner will take care of that and we don't want to bombard the user with too many questions of how to achieve their goal. 
So for example, you shouldn't ask the user about what programming language they want a program to be based on, but you should ask them about features of the final product that they want to see. Focus on what the user wants to see in the final product, not how it should be implemented.
Also, you shouldn't be asking the user for requirements that are already included in the user's goal, so make sure to read the user's goal carefully and avoid asking questions that are already answered in the goal.
Use your common sense when generating the questions, for example if the user's goal is to create a program that can play chess, you shouldn't ask what are the basic rules of the chess game that the program should follow.
Focus on the most important requirements and avoid asking low importance questions like quality of life questions, like what aesthetic features the user wants to see in the final product, if anything the user will provide that if they want to.

User's goal: {user_goal}

Please output your refining questions as a JSON object in the following format:
{{"questions": ["question1", "question2", ...]}}

These refining questions will help us establish the scope of the project, which should contain the requirements for the user's goal.
Your output should only contain the JSON object and no additional text!"""

next_ask_user_prompt = """As an agent responsible for defining the scope of a task for an autonomous AI system, your task is to gather necessary information from the user by asking relevant questions about their goal. This goal is meant to be accomplished by an autonomous AI system that is capable of performing a variety of tasks.
You must only focus on creating questions to retrieve requirements about the contract between the user and the project, not the implementation details as the planner will take care of that and we don't want to bombard the user with too many questions of how to achieve their goal. 
So for example, you shouldn't ask the user about what programming language they want a program to be based on, but you should ask them about features of the final product that they want to see. Focus on what the user wants to see in the final product, not how it should be implemented.
Also, you shouldn't be asking the user for requirements that are already included in the user's goal, so make sure to read the user's goal carefully and avoid asking questions that are already answered in the goal.
Use your common sense when generating the questions, for example if the user's goal is to create a program that can play chess, you shouldn't ask what are the basic rules of the chess game that the program should follow.
Focus on the most important requirements and avoid asking low importance questions like quality of life questions, like what aesthetic features the user wants to see in the final product, if anything the user will provide that if they want to.

You will be given requirements that we have retrieved from the user's answers to previous refining questions. You must ask additional refining questions to gather more information from the user to refine the requirements and establish the scope of the project.

User's goal: {user_goal}

In previous iterations we have retrieved the following requirements from the user's answers: 
{requirements}

Here are some additional feedback:
{validation_instructions}

Please output your refining questions as a JSON object in the following format:
{{"questions": ["question1", "question2", ...]}}

These refining questions will help us establish the scope of the project, which should contain the requirements for the user's goal.
Your output should only contain the JSON object and no additional text!"""

retrieve_requirements_prompt = """As an agent responsible for defining the scope of a task for an autonomous AI system, your task is to extract the requirements needed to achieve the following user goal based on the answers provided to the refining questions given to the user.

User's goal: {user_goal}

Questions: {questions}

User's Answers: {answer}

Please output the extracted requirements as a JSON object in the following format:
{{
    "requirements": [
        "requirement1",
        "requirement2",
        ...
    ]
}}

The requirements should not include any additional information, nor should they omit any information provided by the user.
Make sure to strictly follow this format and not include any additional text in your response. These extracted requirements will be used to establish the scope of the project.
{validation_instructions}"""

validate_requirements_retrieved_prompt = """Your task is to make sure that the requirements extracted by an LLM agent from the answers of the user to refining questions maintain all the information from the user's answers. These requirements will be used to establish the scope of the project of an autonomous AI system.
Do not worry about the completeness of the requirements in the context of the project, your job is to evaluate if the requirements extracted reflect the information from the user's answers.
It is possible that the user didn't answer some questions, 

User's goal: {user_goal}
Questions: {questions}
User's Answers: {answer}
Extracted Requirements: {requirements}

Please provide your feedback as a JSON object in the following format:
{{
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
  }},
  "validation_instructions": "instructions"
}}

If you consider the extracted requirements to be complete and aligned with the user's answers, set the "success" field in the feedback object to true. In the "message" field, provide a brief explanation of your feedback. Set the "validation_instructions" field to an empty string.

If you find the extracted requirements to be incomplete, unclear, or lacking coherence with the user's answers, set the "success" field in the feedback object to false. In the "message" field, provide specific feedback on the shortcomings of the extracted requirements, highlighting areas that need improvement or clarification. In the "validation_instructions" field, include clear and actionable instructions on how to enhance the requirements to better align them with the user's answers. These instructions should guide the AI agent in refining the requirements, ensuring they accurately capture the user's intent.

Your output should only contain the JSON object and no additional text!"""

merge_requirements_prompt = """Your task is to merge the following requirements into a single coherent list of requirements, which will be used to establish the scope of the project of an autonomous AI system. These requirements were extracted from the user's goal and answers to refining questions.
You will be provided with two sets of requirements extracted from the answers to refining questions. Since the second set are derived from questions that could overlap with the first set, you must merge them into a single coherent list of requirements without adding any additional information nor omitting any information provided by the user.

Old requirements: {requirements}
New requirements: {new_requirements}

Please output the merged requirements as a JSON object in the following format:
{{
    "requirements": [
        "requirement1",
        "requirement2",
        ...
        ]
}}

The requirements should not include any additional information, nor should they omit any information from the old and new requirements. Make sure to strictly follow this format and not include any additional text in your response. These merged requirements will be used to establish the scope of the project.
{validation_instructions}"""

validate_requirements_merged_prompt = """Your task is to validate the merged requirements extracted by an LLM agent from two sets of requirements, which will be used to establish the scope of the project of an autonomous AI system. These requirements were extracted from the user's goal and answers to refining questions.
The LLM agent was provided with two sets of requirements extracted from the answers to refining questions. Since the second set are derived from questions that could overlap with the first set, the LLM agent must merge them into a single coherent list of requirements without adding any additional information nor omitting any information provided by the user.
Since LLMs may sometimes produce descriptions that are overly verbose, include unnecessary details, or lack clarity, it is your responsibility to identify and address these issues to ensure a clear and concise list of requirements that maintain the integrity of the initial information.

Old Requirements: {requirements}
New requirements: {new_requirements}

To evaluate:
Merged Requirements: {merged_requirements}

Please provide your feedback as a JSON object in the following format:
{{
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
  }},
  "validation_instructions": "instructions"
}}

If you consider the merged requirements to be complete and aligned with the initial information, set the "success" field in the feedback object to true. In the "message" field, provide a brief explanation of your feedback. Set the "validation_instructions" field to an empty string.

If you find the merged requirements to be incomplete, unclear, or lacking coherence with the initial information, set the "success" field in the feedback object to false. In the "message" field, provide specific feedback on the shortcomings of the merged requirements, highlighting areas that need improvement or clarification. In the "validation_instructions" field, include clear and actionable instructions on how to enhance the requirements to better align them with the initial information. These instructions should guide the AI agent in refining the requirements, ensuring they accurately capture the user's intent."""

validate_scope_completeness_prompt = """As the validator of an autonomous AI system, your task is to validate the completeness of the scope of the project, which should contain the requirements for the user's goal. This is a preprocessing step for the planner, which will use the scope to create a plan to achieve the user's goal.
The requirements should only represent the contract between the user and the project, not the implementation details as the planner will take care of that and we don't want to bombard the user with too many questions of how to achieve their goal.
So for example, the requirements should not include information about what programming language they want a program to be based on, but it should include information about features of the final product that they want to see. Focus on what the user wants to see in the final product, not how it should be implemented.

Here are the information retrieved:

User's goal: {user_goal}
Requirements: {requirements}

Your task is to evaluate the completeness of the requirements for the user's goal. In other words, focus on the contract between the user and the final product, not the implementation details.

Output your feedback as a JSON object in the following format:

{{
  "feedback": {{
      "success": true/false,
      "message": "Your feedback message here"
      }},
  "validation_instructions": "Your validation instructions here"
}}

If you think the requirements are complete, please set the success field to True and provide a brief explanation of why you think so in the feedback message field and leave the validation instructions field with an empty string.

If you think the requirements are incomplete, please set the success field to False and provide a brief explanation of why you think so in the feedback message field. Additionally, please provide specific instructions that will serve as guidance for the AI agent on how to refine the requirements and to know what type of questions to ask the user in the validation instructions field.

Your output should only contain the JSON object and no additional text!"""

# Maybe add a format for this output since it could always add random stuff around the output
describe_scope_prompt = """Your task is to generate a coherent description of the user's goal and its requirements, which will be used to establish the scope of the project of an autonomous AI system. This description will be used by the planner to create a plan to achieve the user's goal.
The description should only include the information from the user's goal and requirements, without adding any additional information. It should be clear and concise, avoiding any unnecessary details or ambiguity. It should reflect the user's intent and desired outcome, ensuring that the AI agent can accurately understand the user's goal and requirements.

User's goal : {user_goal}
Requirements : {requirements}

You MUST include all the information from the user's goal and scope in your description, without adding any additional information.
{validation_instructions}"""

validate_scope_description_prompt = """As the validator for an autonomous AI system, your role is to review and assess the description of the project's scope generated by another AI agent. Your objective is to provide feedback on whether the description accurately reflects the user's goal and requirements, and if it is clear and concise. The description must not omit any information from the user's goal and requirements, nor should it include any additional information.

Given that the description is generated by an AI language model (LLM), it's important to exercise critical thinking and consider potential pitfalls. LLMs may sometimes produce descriptions that are overly verbose, add hallucinated details, or lack clarity. As a validator, it is your responsibility to identify and address these issues to ensure a clear and concise scope description.


User Goal: {user_goal}
Requirements: {requirements}

The AI agent generated the following description of the scope of the project:
{description}

Your task is to carefully evaluate the generated scope description and provide feedback in the form of a JSON object with the following structure:

{{
  "feedback": {{
    "success": true/false,
    "message": "feedback_message"
  }},
  "validation_instructions": "instructions"
}}

If you consider the description to be encapsulate well the information from the user's goal and requirements, set the "success" field in the feedback object to true. Provide your thoughts on the description in the "message" field, highlighting its strengths and alignment with the user's goal and requirements. Set the "validation_instructions" field to an empty string.

If you find the description to be incomplete, inaccurate, or unclear, set the "success" field in the feedback object to false. In the "message" field, provide specific feedback on the description's shortcomings, addressing any issues related to verbosity, unnecessary details, or lack of clarity. In the "validation_instructions" field, include clear and actionable instructions on how the AI agent can improve the description in subsequent iterations. These instructions should guide the AI agent in refining the scope description, avoiding common LLM pitfalls, and ensuring clarity and conciseness.

Your output should only contain the JSON object and no additional text!"""

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


prompts = {'first_ask_user': first_ask_user_prompt,
           'next_ask_user': next_ask_user_prompt,
           'retrieve_requirements': retrieve_requirements_prompt,
           'retrieve_goal': retrieve_goal_prompt,
           'validate_scope_completeness': validate_scope_completeness_prompt,
           'describe_scope': describe_scope_prompt,
           'create_plan': create_plan_prompt,
           'update_plan': update_plan_prompt,
           'tool_selection': tool_selection_prompt,
           'turn_to_action': turn_to_action_prompt,
           'validate_scope_description': validate_scope_description_prompt,
           'validate_goal': validate_goal_prompt,
           'validate_requirements_retrieved': validate_requirements_retrieved_prompt}
