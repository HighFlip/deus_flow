from typing import List, Callable
import copy

class Scope:
    user_query: str
    user_goal: str
    requirements: List[str]
    description: str

    def __init__(self, user_query: str, user_goal: str, requirements: List[str] = [], description: str = None):
        self.user_query = user_query
        self.user_goal = user_goal
        self.requirements = requirements
        self.description = description

    def add_requirements(self, requirements: List[str]):
        self.requirements.extend(requirements)

    def copy(self):
        return Scope(self.user_query, self.user_goal, self.requirements.copy(), self.description)

    def __str__(self):
        return f"User's query = {self.user_query}\nGoal = {self.user_goal}\nRequirements = {self.requirements}"

class Step:
    id: int
    name: str
    goal: str
    tools: List[Tool]
    action: Action
    feedback: Feedback
    accomplished: bool = False
    

    def __init__(self, id: int,
                 name: str, 
                 goal: str,
                 tools: List[Tool] = [],
                 blocked_by: List[Step] = [],
                 blocking: List[Step] = [],
                 action: Action = None,
                 feedback: Feedback = None,
                 accomplished: bool = False):
        self.id = id
        self.name = name
        self.goal = goal
        self.tools = tools
        self.blocked_by = blocked_by
        self.blocking = blocking
        self.action = action
        self.feedback = feedback
        self.accomplished = accomplished
    
    def copy(self):
        return Step(self.id, self.tools.copy(), self.goal, self.action, self.feedback, self.accomplished)


class Tool:
    id: str
    name: str
    description: str
    func: Callable
    input_format: str

    def __init__(self, id: str, name: str, description: str, func: Callable, input_format: str):
        self.id = id
        self.name = name
        self.description = description
        self.func = func
        self.input_format = input_format

    def copy(self):
        return Tool(self.id, self.name, self.description, self.func, self.input_format)

class Feedback:
    messages: List[str]
    summary: str
    success: bool

    def __init__(self, messages: List[str] | str, summary: str = None, success: bool = False):
        if isinstance(messages, str):
            self.messages = [messages]
        else:
            self.messages = messages
        self.summary = summary
        self.success = success
    
    def copy(self):
        return Feedback(self.messages.copy(), self.summary, self.success)
    
    def append(self, feedback):
        if isinstance(feedback, Feedback):
            self.messages.extend(feedback.messages)
        elif isinstance(feedback, str):
            self.messages.append(feedback)
        else:
            raise Exception("Invalid feedback type")    

class Action:
    id: str
    name: str
    description: str
    step: Step
    tool: Tool
    tool_input: str
    output: str
    feedback: Feedback

    def __init__(self, id: str, 
                 name: str, 
                 description: str, 
                 step: Step, 
                 tool: Tool, 
                 tool_input: str, 
                 output: str = None, 
                 feedback: Feedback = None):
        self.id = id
        self.name = name
        self.description = description
        self.step = step
        self.tool = tool
        self.tool_input = tool_input
        self.output = output
        self.feedback = feedback

class Plan:
    steps: List[Step]

    def __init__(self, steps: List[Step]):
        self.steps = steps

    def get_current_step(self):
        for step in self.steps:
            if step.accomplished == False:
                return step
    
    def check_accomplished(self):
        return all(step.accomplished for step in self.steps)

    def copy(self):
        return Plan(copy.deepcopy(self.steps))