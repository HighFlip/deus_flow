import re, json
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

    def retrieve_user_goal(self, user_query: str) -> str:
        prompt = self.prompts['retrieve_goal'].format(user_query=user_query)
        response = llm_call(prompt)
        result = self.parse_response(response)
        goal = result['user_goal']
        if goal:
            self.log(GoalUpdateLog(prompt, response, None, goal))
            return goal
        else:
            self.log(GoalUpdateLog(prompt, response, None, "Goal not found"))
            return self.retrieve_user_goal(user_query)
        
    def add_iteration(self):
        self.logger.add_iteration()

    def log(self, log: Log):
        self.logger.logs[-1].append(log)

    def ask_user_llm_call(self):
        prompt = self.prompts['ask_user'].format(user_query=self.context.scope.user_query)
        question = self.llm_call(prompt)
        user_answer = ...
        self.add_requirements(prompt, question, user_answer)

    def add_requirements(self, prompt: str, question: str, answer: str):
        requirements = self.retrieve_requirements(answer)
        self.context.scope.add_requirements(requirements)
        self.log(RefinementLog(prompt, question, answer, requirements))
    
    def validate_scope(self) -> bool:
        prompt = self.prompts['validate_scope'].format(user_goal=self.context.scope.user_goal, 
                                                       history=self.logger.get_questions_answers(),
                                                       scope=self.context.scope)
        response = self.llm_call(prompt)
        result = self.parse_response(response)
        feedback = result['feedback']
        if feedback.success:
            prompt = self.prompts['describe_scope'].format(user_goal=self.context.scope.user_goal, scope=self.context.scope)
            response = self.llm_call(prompt)
            self.context.scope.description = response
            return True
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
        result = self.parse_response(response)
        self.context.plan = result['plan']
        self.context.current_step = self.context.plan.get_current_step()
        self.log(PlanUpdateLog(prompt, response, previous_plan, self.context.plan))

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
            feedback = Feedback("No active step found", success=False)

        self.context.current_feedback = feedback
        self.logger.logs[-1].feedback = feedback

    def get_candidate_tools(self, step: Step):
        #Semantic search to find potential tools
        pass

    def tool_selection(self, step: Step, candidate_tools: List[Tool]) -> Tuple[List[Tool], Feedback]:
        prompt = self.prompts['tool_selection'].format(step=step, candidate_tools=candidate_tools)
        response = self.llm_call(prompt)
        result = self.parse_response(response)
        tools = result['tools']
        feedback = result['feedback']
        self.log(ToolSelectionLog(prompt, response, tools, feedback=feedback))
        return tools, feedback


    def turn_to_action(self, step: Step, tools: List[Tool], prev_feedback: Feedback) -> Action:
        if prev_feedback.success:
            prompt = self.prompts['turn_to_action'].format(step=step, tools=tools)
            response = self.llm_call(prompt)
            result = self.parse_response(response)
            action = result['action']
            feedback = result['feedback']
            self.log(TurnToActionLog(prompt, response, action, feedback=feedback))
            prev_feedback.append(feedback)
            return action
        else:
            return None


    def execute(self, action: Action, prev_feedback: Feedback):
        if action:
            output, feedback = self.monitor(action.tool.func, action.tool_input, prev_feedback)
            self.log(ExecutionLog(action, action.tool_input, output, feedback))
            prev_feedback.append(feedback)


    def monitor(self, func: Callable, args: str, feedback: Feedback) -> Tuple[str, Feedback]:
        pass

    def retrieve_requirements(self, answer: str) -> Dict[str, List[str]]:
        prompt = self.prompts['retrieve_requirements'].format(user_goal=self.context.scope.user_goal, 
                                                            answer=answer)
        response = self.llm_call(prompt)
        result = self.parse_response(response)
        return result['requirements']
        
    def parse_response(self, response: str):
        # parse the JSON object from the response
        try:
            # Remove leading/trailing whitespace and newlines
            response = response.strip()
            # Try parsing JSON from response as single line
            json_obj = json.loads(response)
        except json.JSONDecodeError:
            # Try parsing JSON from response as multiline
            try:
                json_obj = json.loads(response.replace('\n', ''))
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {str(e)}")
                # handle the error or exit the program
        
        result = {}

        # retrieve the "requirements" key from the dictionary, if present
        if "requirements" in json_obj:
            requirements = json_obj["requirements"]
            print(requirements)
            result['requirements'] = requirements
        if "user_goal" in json_obj:
            user_goal = json_obj["user_goal"]
            print(user_goal)
            result['user_goal'] = user_goal
        if "plan" in json_obj:
            plan_dict = json_obj["plan"]
            steps = []
            for step_name, description in plan_dict.items():
                step = Step(step_name, description)
                steps.append(step)
            plan = Plan(steps)
            print(plan)
            result['plan'] = plan
        if "tools" or "tool" in json_obj:
            tools_dict = json_obj["tools"]
            tools = self.query_tools(tools_dict)
            print(tools)
            result['tools'] = tools
        if "action" in json_obj:
            action = json_obj["action"]
            print(action)
            result['action'] = action
        if "feedback" in json_obj:
            feedback_dict = json_obj["feedback"]
            message = feedback_dict["message"]
            success = True if feedback_dict["success"].lower() in ["true", "t", "success"] else False
            feedback = Feedback(message, success=success)
            print(feedback)
            result['feedback'] = feedback
        
        return result

    def query_tools(self, tools_dict: Dict[str, str]) -> List[Tool]:
        # query the database for the tools
        pass

    def llm_call(self, prompt: str) -> str:
        return llm_call(prompt)
    