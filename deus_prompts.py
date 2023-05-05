ask_user_prompt = """As an agent responsible for defining the scope of a task for an autonomous AI system, your task is to gather necessary information from the user by asking relevant questions about their query. Please use the following user query to generate refining questions:

{user_query}

Please output your refining questions as a JSON object in the following format:
{{"questions": ["question1", "question2", ...]}}

These refining questions will help us establish the scope of the project, which should contain the requirements and constraints for the user's goal."""

parse_scope_prompt = """As an agent responsible for defining the scope of a task for an autonomous AI system, your task is to extract the requirements needed to achieve the following user goal based on the answers provided to the refining questions:
User goal: {user_goal}
Answers: {answer}
Please output the extracted requirements as a JSON object in the following format:
{{"requirements": ["requirement1", "requirement2", ...]}}

Make sure to strictly follow this format and not include any additional text in your response. These extracted requirements will be used to establish the scope of the project."""

retrieve_goal_prompt = """Extract the user's goal from the following user query: {user_query}
You MUST output the user goal as a JSON object in the following format:
{{user_goal: user_goal}}"""

validate_scope_prompt = """Are the following requirements, constraints, and resources correct for the user goal {user_goal}? 
Here is the logs of the questions and answers that were asked to the user: {history}
Here is the scope that was extracted from the user's answers: {scope}
If the scope is correct, type "yes". If the scope is incorrect, type "no" and the agent will ask the user for more information."""

describe_scope_prompt = """Generate a coherent description of these requirements for the user goal {user_goal}: {scope}
You MUST include all the information from the user's goal and scope in your description, without adding any additional information."""

create_plan_prompt = """As the planner for an autonomous AI system, create a plan to achieve the following goal: {description}
You MUST output the plan as a JSON object in the following format:
{{"step_1": "desc_1", "step_2": "desc_2", "step_3": "desc_3"}}"""

update_plan_prompt = """As the planner for an autonomous AI system, update the plan based on the current scope, previous plan, and feedback from the task handler.

The current scope is as follows:
{scope}

The previous plan is as follows:
{previous_plan}

The feedback received from the task handler is as follows:
{feedback}

You may refine the plan based on the feedback, but note that the overall structure of the plan should remain the same.

You MUST output the updated plan as a JSON object in the following format:
{{"step_1": "desc_1", "step_2": "desc_2", "step_3": "desc_3"}}"""

tool_selection_prompt = """As the tool selector for an autonomous AI system, select the best tool or combination of tools to accomplish the following step:

{step}

Based on the step description, the following candidate tools have been identified as potentially suitable for this task:

{candidate_tools}

After careful consideration, please choose the tool or combination of tools that you believe would work best for this task, create a feedback object with an explanation of your thought process. Output your selection as a JSON object in the following format:

{
  "tool": tool_name, 
  "feedback": {
    "success": True/False, 
    "message": "feedback_message"
    }
}

If none of the candidate tools would be suitable for this task, please output a feedback object with the success field set to False and an explanation of why the task cannot be accomplished with the given tools.

Make sure to strictly follow these formats and not include any additional text in your response."""

turn_to_action_prompt = """As the operator for an autonomous AI system, turn the following step into an actionable plan using the tool(s) described below:

Step: {step}

Tool Descriptions:
{tool_descriptions}

Using the selected tool(s), provide an input to complete the step, and output the result as a JSON object in the following format:

{
  "input": {
    "tool_1": "input_1", 
    "tool_2": "input_2",
    ...
    },
  "feedback": {
    "success": True|False,
    "message": "feedback_message"
    }
}

Make sure to strictly follow this format and not include any additional text in your response. If the tool(s) cannot be used to complete the step, set the `success` field in the feedback object to `False` and provide an explanation in the `message` field."""


prompts = {'ask_user': ask_user_prompt,
    'parse_scope': parse_scope_prompt,
    'retrieve_goal': retrieve_goal_prompt,
    'validate_scope': validate_scope_prompt,
    'describe_scope': describe_scope_prompt,
    'create_plan': create_plan_prompt,
    'update_plan': update_plan_prompt,
    'tool_selection': tool_selection_prompt,
    'turn_to_action': turn_to_action_prompt}

