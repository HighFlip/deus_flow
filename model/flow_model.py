import re
from datetime import datetime
from typing import Dict, List, Tuple, Callable
from enum import Enum

from deus_utils import llm_call
from deus_prompts import prompts

from information_model import Scope, Feedback, Tool, Action, Step, Plan
from log_model import (
    Log,
    LLMLog,
    RefinementLog,
    GoalUpdateLog,
    PlanUpdateLog,
    CandidateToolsLog,
    ToolSelectionLog,
    TurnToActionLog,
    ExecutionLog,
    IterationLog,
    Logger
)
class Context:
    scope: Scope
    plan: Plan
    finished: bool
    current_step: Step
    current_feedback: Feedback


    def __init__(self, scope: Scope, plan: Plan = None, current_step: Step = None, finished: bool = False):
        self.scope = scope
        self.plan = plan
        self.current_step = current_step
        self.finished = finished
    
    def deep_copy(self):
        return Context(self.scope.copy(), self.plan.copy(), self.current_step.copy(), self.finished)

class ContextManager:
    context: Context
    logger: Logger
    prompts = prompts

    def __init__(self, user_query: str, context: Context = None, logger: Logger = Logger()):
        user_goal = self.retrieve_user_goal(user_query)
        self.context = context or Context(Scope(user_query, user_goal))
        self.logger = logger(self.context)

    def add_iteration(self):
        self.logger.add_iteration()

    def log(self, log: Log):
        self.logger.logs[-1].append(log)

    def ask_user_llm_call(self):
        prompt = self.prompts['ask_user'].format(user_query=self.context.scope.user_query)
        question = self.llm_call(prompt)
        user_answer = ...
        self.add_refinements(prompt, question, user_answer)

    def add_refinements(self, prompt: str, question: str, answer: str):
        refinements = self.parse_refinement(answer)
        self.context.scope.add_refinements(refinements)
        self.log(RefinementLog(prompt, question, answer, refinements))

    def parse_refinement(self, answer: str):
        prompt = self.prompts['parse_scope'].format(user_goal=self.context.scope.user_goal, 
                                                    answer=answer)
        response = self.llm_call(prompt)
        refinement = self.parse_scope(response)
        return refinement

    def retrieve_user_goal(self, user_query: str) -> str:
        prompt = self.prompts['retrieve_goal'].format(user_query=user_query)
        response = llm_call(prompt)
        refinement = self.parse_scope(response)
        goal = refinement['user_goal'][0]
        if goal:
            self.log(GoalUpdateLog(prompt, response, None, goal))
            return goal
        else:
            self.log(GoalUpdateLog(prompt, response, None, "Goal not found"))
            return self.retrieve_user_goal(user_query)
        
    def parse_scope(self, result: str):
        result = result.lower()
        result = result.replace('\n', '').replace('\r', '')
        
        # Parse user goal
        goal_match = re.search(r'user_goal:\s*([\w\s]+)[.,]', result)
        if goal_match:
            goal = goal_match.group(1).strip()
        
        # Parse requirements, constraints, and resources
        req_match = re.search(r'requirements:\s*\[([^\]]*)\]', result)
        if req_match:
            requirements = [req.strip() for req in req_match.group(1).split(',')]
        
        # Handle edge cases for empty lists
        if not requirements or requirements == ['']:
            requirements = []
        
        # Handle edge cases for capitalization
        if goal:
            goal = goal.capitalize()
        if requirements:
            requirements = [req.capitalize() for req in requirements]

        return {'goal': goal,
                'requirements': requirements}
    
    def validate_scope(self) -> bool:
        prompt = self.prompts['validate_scope'].format(user_goal=self.context.scope.user_goal, 
                                                       history=self.logger.get_questions_answers(),
                                                       scope=self.context.scope)
        response = self.llm_call(prompt)
        if self.parse_bool(response):
            prompt = self.prompts['describe_scope'].format(user_goal=self.context.scope.user_goal, scope=self.context.scope)
            response = self.llm_call(prompt)
            self.context.scope.description = response
            return True
        else:
            return False

    def parse_bool(self, response: str) -> bool:
        response = response.lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            return False

    def planner(self):
        previous_plan = self.context.plan
        if previous_plan is None:
            prompt = self.prompts['create_plan'].format(description=self.context.scope.description)
            response = self.llm_call(prompt)

        else:
            prompt = self.prompts['update_plan'].format(description=self.context.scope.description, 
                                                        feedback=self.context.current_feedback,
                                                        previous_plan=self.context.plan)
            response = self.llm_call(prompt)
        self.context.plan = self.parse_plan(response)
        self.context.current_step = self.context.plan.get_current_step()
        self.log(PlanUpdateLog(prompt, response, previous_plan, self.context.plan))

    def parse_plan(self):
        pass

    def task_handler(self):
        active_step = self.context.current_step
        if active_step:
            candidate_tools = self.get_candidate_tools(active_step)
            relevant_tools, feedback = self.tool_selection(active_step, candidate_tools)
            action = self.turn_to_action(active_step, relevant_tools, feedback)
            self.execute(action, feedback)
            active_step.feedback = feedback
            self.context.current_feedback = feedback
            if feedback.success:
                active_step.accomplished = True
                if self.context.plan.check_accomplished():
                    self.context.finished = True
                
        else:
            feedback = Feedback(["No active step found"])

        self.context.current_feedback = feedback
        self.logger.logs[-1].feedback = feedback

    def get_candidate_tools(self, step: Step):
        #Semantic search to find potential tools
        pass

    def tool_selection(self, step: Step, candidate_tools: List[Tool]) -> Tuple[List[Tool], Feedback]:
        prompt = self.prompts['tool_selection'].format(step=step, candidate_tools=candidate_tools)
        response = self.llm_call(prompt)
        tools, feedback = self.parse_tools_and_feedback(response)
        self.log(ToolSelectionLog(prompt, response, tools, feedback=feedback))
        return tools, feedback

    def parse_tools_and_feedback(self, response: str) -> List[Tool]:
        pass

    def turn_to_action(self, step: Step, tools: List[Tool], prev_feedback: Feedback) -> Action:
        if prev_feedback.success:
            prompt = self.prompts['turn_to_action'].format(step=step, tools=tools)
            response = self.llm_call(prompt)
            action, feedback = self.parse_action_and_feedback(response)
            self.log(TurnToActionLog(prompt, response, action, feedback=feedback))
            prev_feedback.append(feedback)
            return action
        else:
            return None

    def parse_action_and_feedback(self, response: str) -> Tuple[Action, Feedback]:
        pass

    def execute(self, action: Action, prev_feedback: Feedback):
        if action:
            output, feedback = self.monitor(action.tool.func, action.tool_input, prev_feedback)
            self.log(ExecutionLog(action, action.tool_input, output, feedback))
            prev_feedback.append(feedback)


    def monitor(self, func: Callable, args: str, feedback: Feedback):
        pass

    def llm_call(self, prompt: str) -> str:
        return llm_call(prompt)
    