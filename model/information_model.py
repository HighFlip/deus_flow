from __future__ import annotations
from typing import List, Callable
import copy

from model.feedback_model import Feedback, FeedbackBundle
from model.workflow_model import Workflow
from deus_utils import get_step_id, get_action_id

class Scope:
    user_query: str
    user_goal: str
    requirements: Requirements
    description: str

    def __init__(self, user_query: str, user_goal: str, requirements: Requirements = None, description: str = None):
        self.user_query = user_query
        self.user_goal = user_goal
        self.requirements = requirements
        self.description = description

    def set_requirements(self, requirements: Requirements):
        self.requirements = requirements

    def copy(self):
        return Scope(self.user_query, self.user_goal, self.requirements.copy(), self.description)

    def __str__(self):
        return f"User's query = {self.user_query}\nGoal = {self.user_goal}\nRequirements = {self.requirements}"

class Step:
    id: str
    name: str
    goal: str
    action: Action
    feedback: Feedback|FeedbackBundle
    accomplished: bool = False
    

    def __init__(self,
                 name: str, 
                 goal: str,
                 tools: List[Tool] = [],
                 blocked_by: List[Step] = [],
                 blocking: List[Step] = [],
                 action: Action = None,
                 feedback: Feedback = None,
                 accomplished: bool = False):
        self.id = get_step_id()
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
    id: int
    name: str
    description: str
    workflow: Workflow
    input_format: str

    def __init__(self, id: str, name: str, description: str, func: Callable, input_format: str):
        self.id = id
        self.name = name
        self.description = description
        self.func = func
        self.input_format = input_format

    def copy(self):
        return Tool(self.id, self.name, self.description, self.func, self.input_format)

class Action:
    id: str
    step: Step
    tool: Tool
    tool_input: str
    feedback: Feedback|FeedbackBundle

    def __init__(self, 
                 step: Step, 
                 tool: Tool, 
                 tool_input: str,  
                 feedback: Feedback = None):
        self.id = get_action_id(step.id)
        self.step = step
        self.tool = tool
        self.tool_input = tool_input
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
    
class Requirements:
    requirements: List[str]

    def __init__(self, requirements: List[str]):
        self.requirements = requirements

    def copy(self):
        return Requirements(self.requirements.copy())
    
    def update(self, requirements: List[str]):
        self.requirements = requirements
    
    def __str__(self):
        return str(self.requirements)