ask_user_prompt = """As the agent defining the scope of a task for an autonomous AI system, gather necessary information from the user by asking relevant questions about their query:
    {user_query}
    The scope that needs to be determined must contain the following information:
    Requirements: The specific needs of the task that must be fulfilled by the AI system.
    Constraints: The limitations of the task that must be considered by the AI system.
    Resources: The resources available to the AI system to complete the task.

    You must output your questions as a JSON object in the following format:
    \{questions: [question1, question2, ...]\}"""

parse_scope_prompt = """Extract the requirements, constraints, and resources for an autonomous AI system to achieve the following user goal. Parse the following prompt and retrieve only these three types of information. If a particular type of information is not provided in the prompt, leave the corresponding field as an empty list.

    user_goal: {user_goal}
    user_refinement: {answer}

    You must output the requirements, constraints, and resources as a JSON object in the following format:
    \{requirements: [requirement1, requirement2, ...], constraints: [constraint1, constraint2, ...], resources: [resource1, resource2, ...]\}
    Make sure to strictly follow this format and not include any additional text in your response."""

retrieve_goal_prompt = """Extract the user's goal from the following user query: {user_query}
    You MUST output the user goal as a JSON object in the following format:
    \{user_goal: user_goal\}"""

validate_scope_prompt = """Are the following requirements, constraints, and resources correct for the user goal {user_goal}? 
    Here is the logs of the questions and answers that were asked to the user: {history}
    Here is the scope that was extracted from the user's answers: {scope}
    If the scope is correct, type "yes". If the scope is incorrect, type "no" and the agent will ask the user for more information."""

describe_scope_prompt = """Generate a coherent description of these requirements, constraints, and resources for the user goal {user_goal}: {scope}
    You MUST include all the information from the user's goal and scope in your description, without adding any additional information."""

create_plan_prompt = """As the planner for an autonomous AI system, create a plan to achieve the following goal: {description}
    You MUST output the plan as a JSON object in the following format:
    \{step_1: desc_1, step_2: desc_2, step_3: desc_3\}"""

prompts = {'ask_user': ask_user_prompt,
    'parse_scope': parse_scope_prompt,
    'retrieve_goal': retrieve_goal_prompt,
    'validate_scope': validate_scope_prompt,
    'describe_scope': describe_scope_prompt,
    'create_plan': create_plan_prompt}

