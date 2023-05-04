import re
from datetime import datetime
from typing import Dict, List, Tuple
from enum import Enum

from deus_utils import llm_call
from deus_prompts import prompts

from information_model import Scope, Feedback, Tool, Action, Step, Plan
from log_model import Log, LLMLog, ActionLog, RefinementLog, GoalUpdateLog, PlanUpdateLog, IterationLog, Logger
            

class Context:
    scope: Scope
    plan: Plan
    current_step: Step
    feedback: Feedback
    finished: bool

    def __init__(self, scope: Scope, plan: Plan = None, current_step: Step = None, finished: bool = False):
        self.scope = scope
        self.plan = plan
        self.current_step = current_step
        self.finished = finished
    
    def deep_copy(self):
        return Context(self.scope.copy(), self.plan.copy(), self.current_step.copy(), self.finished)

class ContextManager:
    current_context: Context
    iterations: List[IterationLog]
    logger: Logger
    prompts = prompts

    def __init__(self, user_query: str, context: Context = None, logger: Logger = Logger()):
        user_goal = self.retrieve_user_goal(user_query)
        self.current_context = context or Context(Scope(user_query, user_goal))
        self.logger = logger(self.current_context)

    def add_iteration(self):
        self.logger.add_iteration()

    def log(self, log: Log):
        self.logger.logs[-1].append(log)

    def ask_user_llm_call(self):
        prompt = self.prompts['ask_user'].format(user_query=self.current_context.scope.user_query)
        question = self.llm_call(prompt)
        user_answer = ...
        self.add_refinements(prompt, question, user_answer)

    def add_refinements(self, prompt: str, question: str, answer: str):
        refinements = self.parse_refinement(answer)
        self.current_context.scope.add_refinements(refinements)
        self.log(RefinementLog(prompt, question, answer, refinements))

    def parse_refinement(self, answer: str):
        prompt = self.prompts['parse_scope'].format(user_goal=self.current_context.scope.user_goal, 
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
        
        con_match = re.search(r'constraints:\s*\[([^\]]*)\]', result)
        if con_match:
            constraints = [con.strip() for con in con_match.group(1).split(',')]
        
        res_match = re.search(r'resources:\s*\[([^\]]*)\]', result)
        if res_match:
            resources = [res.strip() for res in res_match.group(1).split(',')]
        
        # Handle edge cases for empty lists
        if not requirements or requirements == ['']:
            requirements = []
        if not constraints or constraints == ['']:
            constraints = []
        if not resources or resources == ['']:
            resources = []
        
        # Handle edge cases for capitalization
        if goal:
            goal = goal.capitalize()
        if requirements:
            requirements = [req.capitalize() for req in requirements]
        if constraints:
            constraints = [con.capitalize() for con in constraints]
        if resources:
           resources = [res.capitalize() for res in resources]

        return {'goal': goal,
                'requirements': requirements, 
                'constraints': constraints,
                'resourses': resources}
    
    def validate_scope(self) -> bool:
        prompt = self.prompts['validate_scope'].format(user_goal=self.current_context.scope.user_goal, 
                                                       history=self.logger.get_questions_answers(),
                                                       scope=self.current_context.scope)
        response = self.llm_call(prompt)
        if self.parse_bool(response):
            prompt = self.prompts['describe_scope'].format(user_goal=self.current_context.scope.user_goal, scope=self.current_context.scope)
            response = self.llm_call(prompt)
            self.current_context.scope.description = response
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

    def planner(self, feedback: Feedback):
        previous_plan = self.current_context.plan
        if previous_plan is None:
            prompt = self.prompts['create_plan'].format(description=self.current_context.scope.description)
            response = self.llm_call(prompt)

        else:
            prompt = self.prompts['update_plan'].format(description=self.current_context.scope.description, 
                                                        feedback=self.current_context.current_step.feedback,
                                                        previous_plan=self.current_context.plan)
            response = self.llm_call(prompt)
        self.current_context.plan = self.parse_plan(response)
        self.current_context.current_step = self.current_context.plan.get_current_step()
        self.log(PlanUpdateLog(prompt, response, previous_plan, self.current_context.plan))

    def parse_plan(self):
        pass

    def task_handler(self) -> Feedback:
        active_step = self.current_context.current_step
        if active_step:
            candidate_tools = self.get_candidate_tools(active_step)
            relevant_tools, feedback = self.tool_selection(active_step, candidate_tools)
            action = self.turn_to_action(active_step, relevant_tools, feedback)
            self.execute(action, feedback)
        else:
            feedback = Feedback("No active step found")

    def get_candidate_tools(self, step: Step):
        #Semantic search to find potential tools
        pass

    def tool_selection(self, step: Step, candidate_tools: List[Tool]) -> Tuple[List[Tool], Feedback]:
        pass

    def turn_to_action(self, step: Step, tools: List[Tool], feedback: Feedback) -> Action:
        pass

    def execute(self, action: Action) -> Feedback:
        pass

    def llm_call(self, prompt: str) -> str:
        return llm_call(prompt)
    