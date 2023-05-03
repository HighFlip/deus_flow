import re
from datetime import datetime
from typing import Dict, List, Callable
from deus_utils import llm_call
from deus_prompts import prompts
from enum import Enum

format_instructions = """"""

class Scope:

    def __init__(self, user_query: str, user_goal: str):
        self.user_query = user_query
        self.user_goal = user_goal
        self.constraints = []
        self.requirements = []
        self.resources = []
        self.description = None

    def add_refinements(self, refinements: Dict[str: List[str]]):
        self.constraints.extend(refinements['constraints'])
        self.requirements.extend(refinements['requirements'])
        self.resources.extend(refinements['resources'])

    def __str__(self):
        return f"Constraints = {self.constraints}\nRequirements = {self.requirements}\nResources = {self.resources}\n"

class Feedback:
    message: str
    

class Wisdom:
    description: str
    source: Log

class Tool:
    id: str
    name: str
    description: str
    func: Callable
    input_format: str

class Action:
    id: str
    name: str
    description: str
    step: Step
    tool: Tool
    tool_input: str
    output: str
    feedback: Feedback

    def __init__(self, id: str, name: str, description: str, step: Step, tool: Tool, tool_input: str, output: str = None, feedback: Feedback = None):
        self.id = id
        self.name = name
        self.description = description
        self.step = step
        self.tool = tool
        self.tool_input = tool_input
        self.output = output
        self.feedback = feedback

class Step:
    id: int
    tools: List[Tool]
    goal: str
    dependencies: List[Step]
    action: Action
    wisdom: Wisdom
    accomplished: bool = False
    feedback: Feedback

class Plan:
    steps: List[Step]

    def get_current_step(self):
        for step in self.steps:
            if step.accomplished == False:
                return step
            

class Context:
    scope: Scope
    plan: Plan
    current_step: Step
    finished: bool

    def __init__(self, scope: Scope, plan: Plan = None, current_step: Step = None, finished: bool = False):
        self.scope = scope
        self.plan = plan
        self.current_step = current_step
        self.finished = finished


class Log:
    timestamp: datetime
    message: str|None
    
    def __init__(self, message: str|None = None):
        self.timestamp = datetime.now()
        self.message = message

    def __str__(self):
        return f"{self.timestamp}: {self.message if self.message else ''}"
    
    def __repr__(self):
        return str(self)
    
class LLMLog(Log):
    prompt: str
    response: str
    role: str

    def __init__(self, prompt: str, response: str, role: str):
        super().__init__(response)
        self.prompt = prompt
        self.response = response
        self.role = role
    
    def __str__(self):
        return f"{self.timestamp}: \nPrompt = {self.prompt},\nResponse = {self.response}"
    
class ActionLog(Log):
    action: Action

    def __init__(self, action: Action):
        super().__init__(action.description)
        self.action = action
    
    def __str__(self):
        return f"{self.timestamp}: \nAction = {self.action}"
    
class RefinementLog(LLMLog):
    question: str
    answer: str
    refinements: Dict[str:List[str]]

    def __init__(self, prompt: str, question: str, answer: str, refinements: Dict[str:List[str]]):
        super().__init__(prompt, question, "refinement")
        self.question = question
        self.answer = answer
        self.refinements = refinements
    
    def __str__(self):
        return f"{self.timestamp}: \nQuestion = {self.question},\nAnswer = {self.answer}"
    
class GoalUpdateLog(LLMLog):
    previous_goal: str
    goal: str

    def __init__(self, prompt: str, response: str, previous_goal: str, goal: str):
        super().__init__(prompt, response, "goal_update")
        self. previous_goal = previous_goal
        self.goal = goal
    
    def __str__(self):
        return f"{self.timestamp}: \nGoal = {self.goal}"
    
class PlanUpdateLog(LLMLog):
    previous_plan: Plan
    plan: Plan

    def __init__(self, prompt: str, response: str, previous_plan: Plan, plan: Plan):
        super().__init__(prompt, response, 'planner')
        self.previous_plan = previous_plan
        self.plan = plan


    
class IterationLog(Log):
    context: Context
    logs: List[Log]

    def __init__(self, context: Context, logs: List[Log]):
        super().__init__()
        self.context = context
        self.logs = logs

    def add_log(self, log: str):
        self.logs.append(log)

    def get_logs(self) -> str:
        return '\n'.join(self.logs)
    
    def clear_logs(self):
        self.logs = []

class Logger:
    logs: List[List[Log]]

    def __init__(self, logs: List[List[Log]] = [[]]):
        self.logs = logs

    def get_questions_answers(self) -> List[str]:
        return "\n".join("\n".join([log.question, log.answer]) for log in self.logs if isinstance(log, RefinementLog))

class ContextManager:
    current_context: Context
    iterations: List[IterationLog]
    logger: Logger
    next_iteration: bool = False
    prompts = prompts

    def __init__(self, user_query: str, context: Context = None, iterations: List[IterationLog] = [], logger: Logger = Logger()):
        user_goal = self.retrieve_user_goal(user_query)
        self.current_context = context or Context(Scope(user_query, user_goal))
        self.iterations = iterations
        self.logger = logger

    def add_iteration(self):
        self.iterations.append(IterationLog(self.current_context, self.logger.logs[-1]))
        self.logger.logs.append([])

    def add_llm_log(self, prompt: str, response: str, role: str):
        self.logger.logs[-1].append(LLMLog(prompt, response, role))

    def add_action_log(self, action: Action):
        self.logger.logs[-1].append(ActionLog(action))

    def add_refinement_log(self, prompt: str, question: str, answer: str, refinements: Dict[str:List[str]]):
        self.logger.logs[-1].append(RefinementLog(prompt, question, answer, refinements))

    def add_goal_update_log(self, prompt: str, response: str, previous_goal: str, goal: str):
        self.logger.logs[-1].append(GoalUpdateLog(prompt, response, previous_goal, goal))

    def add_plan_update_log(self, prompt: str, response: str, previous_plan: Plan, plan: Plan):
        self.logger.logs[-1].append(PlanUpdateLog(prompt, response, previous_plan, plan))

    def add_log(self, log: Log):
        self.logger.logs[-1].append(log)

    def ask_user_llm_call(self):
        prompt = self.prompts['ask_user'].format(user_query=self.current_context.scope.user_query)
        question = self.llm_call(prompt)
        user_answer = ...
        self.add_refinements(prompt, question, user_answer)

    def add_refinements(self, prompt: str, question: str, answer: str):
        refinements = self.parse_refinement(answer)
        self.current_context.scope.add_refinements(refinements)
        self.add_refinement_log(prompt, question, answer, refinements)

    def parse_refinement(self, answer: str):
        prompt = self.prompts['parse_scope'].format(user_goal=self.current_context.scope.user_goal, 
                                                answer=answer, format_instructions=format_instructions)
        response = self.llm_call(prompt)
        refinement = self.parse_scope(response)
        return refinement

    def retrieve_user_goal(self, user_query: str) -> str:
        prompt = self.prompts['retrieve_goal'].format(user_query=user_query)
        response = llm_call(prompt)
        refinement = self.parse_scope(response)
        goal = refinement['user_goal'][0]
        if goal:
            self.add_goal_update_log(prompt, response, None, goal)
            return goal
        else:
            self.add_goal_update_log(prompt, response, None, "Goal not found")
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

    def llm_call(self, prompt: str) -> str:
        return llm_call(prompt)
    
    def planner(self):
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
        self.add_plan_update_log(prompt, response, previous_plan, self.current_context.plan)

    def parse_plan(self):
        pass

    def task_handler(self):
        active_step = self.current_context.current_step
        if active_step:
            candidate_tools = self.get_candidate_tools(active_step)
            relevant_tools = self.tool_selection(active_step, candidate_tools)
            action = self.turn_to_action(active_step, relevant_tools)
            self.execute(action)

    def get_candidate_tools(self, step: Step):
        #Semantic search to find potential tools
        pass

    def tool_selection(self, step: Step, candidate_tools: List[Tool]):
        pass

    def turn_to_action(self, step: Step, tools: List[Tool]):
        pass

    def execute(self, action: Action):
        pass
