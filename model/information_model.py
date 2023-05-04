from typing import List, Dict, Callable
from log_model import Log
import copy


class Scope:
    user_query: str
    user_goal: str
    constraints: List[str]
    requirements: List[str]
    resources: List[str]
    description: str

    def __init__(self, user_query: str, user_goal: str, constraints: List[str] = [], requirements: List[str] = [], resources: List[str] = [], description: str = None):
        self.user_query = user_query
        self.user_goal = user_goal
        self.constraints = constraints
        self.requirements = requirements
        self.resources = resources
        self.description = description

    def add_refinements(self, refinements: Dict[str: List[str]]):
        self.constraints.extend(refinements['constraints'])
        self.requirements.extend(refinements['requirements'])
        self.resources.extend(refinements['resources'])

    def copy(self):
        return Scope(self.user_query, self.user_goal, self.constraints.copy(), self.requirements.copy(), self.resources.copy(), self.description)

    def __str__(self):
        return f"Constraints = {self.constraints}\nRequirements = {self.requirements}\nResources = {self.resources}\n"

class Step:
    id: int
    tools: List[Tool]
    goal: str
    action: Action
    feedback: Feedback
    accomplished: bool = False
    

    def __init__(self, id: int, 
                 tools: List[Tool],
                 goal: str,
                 blocked_by: List[Step] = [],
                 blocking: List[Step] = [],
                 action: Action = None,
                 feedback: Feedback = None,
                 accomplished: bool = False):
        self.id = id
        self.tools = tools
        self.goal = goal
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
    message: str

    def __init__(self, message: str):
        self.message = message



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
            
    def copy(self):
        return Plan(copy.deepcopy(self.steps))