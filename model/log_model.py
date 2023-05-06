from datetime import datetime
from typing import Dict, List
from deus_utils import llm_call
from model.flow_model import Context, Action, Plan, Tool
from model.information_model import Feedback
import copy

class Log:
    timestamp: datetime
    feedback: Feedback
    
    def __init__(self, feedback: Feedback = None):
        self.timestamp = datetime.now()
        self.feedback = feedback

class CandidateToolsLog(Log):
    candidate_tools: Dict[int:Tool]

    def __init__(self, candidate_tools: Dict[int:Tool], feedback: Feedback = None):
        super().__init__(feedback=feedback)
        self.candidate_tools = candidate_tools

class ExecutionLog(Log):
    action: Action
    input: str
    output: str

    def __init__(self, action: Action, feedback: Feedback = None):
        super().__init__(feedback=feedback)
        self.action = action
    
class LLMLog(Log):
    prompt: str
    response: str
    role: str

    def __init__(self, prompt: str, response: str, role: str, feedback: Feedback = None):
        super().__init__(response, feedback=feedback)
        self.prompt = prompt
        self.response = response
        self.role = role
    
    def __str__(self):
        return f"{self.timestamp}: \nPrompt = {self.prompt},\nResponse = {self.response}\nFeedback = {self.feedback}"
    
class RefinementLog(LLMLog):
    question: str
    answer: str
    refinements: Dict[str:List[str]]

    def __init__(self, prompt: str, question: str, answer: str, refinements: Dict[str:List[str]], feedback: Feedback = None):
        super().__init__(prompt, question, "refinement", feedback=feedback)
        self.question = question
        self.answer = answer
        self.refinements = refinements
    
    def __str__(self):
        return f"{self.timestamp}: \nQuestion = {self.question},\nAnswer = {self.answer}"
    
class GoalUpdateLog(LLMLog):
    previous_goal: str
    goal: str

    def __init__(self, prompt: str, response: str, previous_goal: str, goal: str, feedback: Feedback = None):
        super().__init__(prompt, response, "goal_update", feedback=feedback)
        self. previous_goal = previous_goal
        self.goal = goal
    
    def __str__(self):
        return f"{self.timestamp}: \nGoal = {self.goal}"
    
class PlanUpdateLog(LLMLog):
    previous_plan: Plan
    plan: Plan

    def __init__(self, prompt: str, response: str, previous_plan: Plan, plan: Plan, feedback: Feedback = None):
        super().__init__(prompt, response, 'planner', feedback=feedback)
        self.previous_plan = previous_plan
        self.plan = plan

class ToolSelectionLog(LLMLog):
    tool: Tool

    def __init__(self, prompt: str, response: str, tool: Tool, feedback: Feedback = None):
        super().__init__(prompt, response, "tool_selection", feedback=feedback)
        self.tool = tool

class TurnToActionLog(LLMLog):
    action: Action

    def __init__(self, prompt: str, response: str, action: Action, feedback: Feedback = None):
        super().__init__(prompt, response, "turn_to_action", feedback=feedback)
        self.action = action
    
    
class IterationLog(Log):
    context: Context
    logs: List[Log]

    def __init__(self, context: Context, logs: List[Log] = [], feedback: Feedback = None):
        super().__init__(feedback=feedback)
        self.context = context
        self.logs = logs
        self.feedback = feedback

    def append(self, log: Log):
        self.logs.append(log)

    def clear(self):
        self.logs = []

class Logger:
    logs: List[IterationLog]

    def __init__(self, context: Context = None, logs: List[IterationLog] = None):
        self.logs = logs or []
        if logs is None and context is not None:
            self.logs.append(IterationLog(context))

    def get_questions_answers(self) -> List[str]:
        return "\n".join("\n".join([log.question, log.answer]) for log in self.logs[0] if isinstance(log, RefinementLog))

    def clear_logs(self):
        self.logs = []

    def add_iteration(self):
        old_iteration = self.logs[0]
        self.logs.insert(0, copy.deepcopy(old_iteration))
        self.logs[-1].clear()