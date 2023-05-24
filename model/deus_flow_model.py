from __future__ import annotations

import copy
import json
from typing import Dict, List, Tuple, Callable

from deus_utils import llm_call
from deus_prompts import prompts

from model.information_model import Scope, Tool, Action, Step, Plan
from model.feedback_model import Feedback, FeedbackBundle, DataBundle
from model.log_model import Log

class CandidateToolsLog(Log):
    candidate_tools: Dict[int:Tool]

    def __init__(self, candidate_tools: Dict[int:Tool], feedback: Feedback|FeedbackBundle = None):
        super().__init__(feedback=feedback)
        self.candidate_tools = candidate_tools

class ExecutionLog(Log):
    action: Action
    data: DataBundle

    def __init__(self, action: Action, data: DataBundle, feedback: Feedback|FeedbackBundle = None):
        super().__init__(feedback=feedback)
        self.action = action
        self.data = data
    
class LLMLog(Log):
    prompt: str
    response: str
    role: str

    def __init__(self, prompt: str, response: str, role: str, feedback: Feedback|FeedbackBundle = None):
        super().__init__(feedback=feedback)
        self.prompt = prompt
        self.response = response
        self.role = role
    
    def __str__(self):
        return f"{self.timestamp}: \nPrompt = {self.prompt},\nResponse = {self.response}\nFeedback = {self.feedback}"

class ValidationLog(LLMLog):
    validation_instructions: str

    def __init__(self, prompt: str, response: str, feedback: Feedback, validation_instructions: str):
        super().__init__(prompt, response, 'validation', feedback=feedback)
        self.validation_instructions = validation_instructions

class RetrievalLog(LLMLog):
    data: Dict

    def __init__(self, prompt: str, response: str, data: Dict):
        super().__init__(prompt, response, 'retrieval')
        self.data = data

class RefinementLog(LLMLog):
    question: str
    answer: str
    requirements: List[str]

    def __init__(self, prompt: str, question: str, answer: str, requirements: List[str], feedback: Feedback|FeedbackBundle = None):
        super().__init__(prompt, question, "refinement", feedback=feedback)
        self.question = question
        self.answer = answer
        self.requirements = requirements
    
    def __str__(self):
        return f"{self.timestamp}: \nQuestion = {self.question},\nAnswer = {self.answer}"
    
class GoalUpdateLog(Log):
    previous_goal: str
    goal: str

    def __init__(self, previous_goal: str, goal: str, feedback: Feedback|FeedbackBundle = None):
        super().__init__(feedback=feedback)
        self.previous_goal = previous_goal
        self.goal = goal
    
    def __str__(self):
        return f"{self.timestamp}: new_goal = {self.goal}"
    
class PlanUpdateLog(LLMLog):
    previous_plan: Plan
    plan: Plan

    def __init__(self, prompt: str, response: str, previous_plan: Plan, plan: Plan, feedback: Feedback|FeedbackBundle = None):
        super().__init__(prompt, response, 'planner', feedback=feedback)
        self.previous_plan = previous_plan
        self.plan = plan

class ToolSelectionLog(LLMLog):
    tool: Tool

    def __init__(self, prompt: str, response: str, tool: Tool, feedback: Feedback|FeedbackBundle = None):
        super().__init__(prompt, response, "tool_selection", feedback=feedback)
        self.tool = tool

class TurnToActionLog(LLMLog):
    action: Action

    def __init__(self, prompt: str, response: str, action: Action, feedback: Feedback|FeedbackBundle = None):
        super().__init__(prompt, response, "turn_to_action", feedback=feedback)
        self.action = action
    
    
class IterationLog(Log):
    context: Context
    logs: List[Log]

    def __init__(self, context: Context = None, logs: List[Log] = None, feedback: Feedback|FeedbackBundle = None):
        super().__init__(feedback=feedback)
        self.context = context
        self.logs = logs or []
        self.feedback = feedback

    def append(self, log: Log):
        self.logs.append(log)

    def clear(self):
        self.logs = []

class Logger:
    logs: List[IterationLog]

    def __init__(self, logs: List[IterationLog] = None, context: Context = None):
        self.logs = logs or [IterationLog()]
        if logs is None and context is not None:
            self.add_context(context)

    def add_context(self, context: Context):
        self.logs[-1].context = context

    def get_questions_answers(self) -> List[str]:
        return "\n".join("\n".join([log.question, log.answer]) for log in self.logs[0] if isinstance(log, RefinementLog))

    def clear_logs(self):
        self.logs = []

    def add_iteration(self):
        old_iteration = self.logs[0]
        self.logs.insert(0, copy.deepcopy(old_iteration))
        self.logs[-1].clear()

    def log(self, log: Log):
        print(log)
        self.logs[-1].append(log)

class Context:
    scope: Scope
    plan: Plan
    current_step: Step
    finished: bool
    current_feedback: Feedback|FeedbackBundle
    data: DataBundle

    def __init__(self, scope: Scope, 
                 plan: Plan = None, 
                 current_step: Step = None, 
                 finished: bool = False, 
                 current_feedback: Feedback|FeedbackBundle = None, 
                 data: DataBundle = None):
        self.scope = scope
        self.plan = plan
        self.current_step = current_step
        self.finished = finished
        self.current_feedback = current_feedback
        self.data = data
    
    def deep_copy(self):
        return Context(self.scope.copy(), self.plan.copy(), self.current_step.copy(), self.finished)

class ContextManager:
    context: Context
    logger: Logger
    prompts = prompts

    def __init__(self, user_query: str = None, context: Context = None, logger: Logger = None):
        self.logger = logger or Logger()
        if context is not None:
            self.context = context
        elif user_query is not None:
            user_goal = self._get_user_goal(user_query)
            self.context = Context(Scope(user_query, user_goal))
        self.logger.add_context(self.context)

    def ask_user_llm_call(self):
        prompt = self.prompts['ask_user'].format(user_query=self.context.scope.user_query)
        questions = self.llm_call(prompt)
        user_answer = input(questions)
        self._add_requirements(prompt, questions, user_answer)

    def _add_requirements(self, prompt: str, questions: str, answer: str):
        requirements = self._update_requirements(answer)
        self.context.scope.add_requirements(requirements)
        self._log(RefinementLog(prompt, questions, answer, requirements))
    
    def validate_scope(self) -> bool:
        feedback = self._validate_scope_llm_call(self.context.scope.user_goal, 
                                                 self.logger.get_questions_answers(), self.context.scope, "")
        if feedback.success:
            self.context.scope.description = self._get_scope_description(self.context.scope.user_goal, self.context.scope)
            return True
        else:
            return False

    def planner(self):
        previous_plan = self.context.plan
        if previous_plan is None:
            plan = self._create_plan_llm_call(self.context.scope.description)
        else:
            plan = self._get_plan_update(self.context.scope.description, 
                                         self.context.current_feedback, 
                                         previous_plan)
        self.context.plan = plan
        self.context.current_step = plan.get_current_step()
    
    def task_handler(self):
        active_step = self.context.current_step
        if active_step:
            data = DataBundle({'active_step': active_step}, FeedbackBundle())
            self.get_candidate_tools(data)
            self.tool_selection(data)
            self.turn_to_action(data)
            self.execute_action(data)
            active_step.feedback = data.feedback_bundle
            self.context.data = data
            if data.feedback_bundle.success:
                active_step.accomplished = True
                if self.context.plan.check_accomplished():
                    self.context.finished = True
        else:
            feedback = Feedback("No active step found", success=False)

        self.context.current_feedback = feedback
        self.logger.logs[-1].feedback = feedback

    def get_candidate_tools(self, step: Step) -> DataBundle:
        #Semantic search to find potential tools
        pass

    def tool_selection(self, step: Step, candidate_tools: List[Tool]) -> Tuple[List[Tool], Feedback]:
        prompt = self.prompts['tool_selection'].format(step=step, candidate_tools=candidate_tools)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        tool = self._retrieve_tool(json_obj)
        feedback = self._retrieve_feedback(json_obj)
        feedback_bundle = FeedbackBundle(feedback)
        self._log(ToolSelectionLog(prompt, response, tool, feedback=feedback))
        return tool, feedback_bundle

    def turn_to_action(self, step: Step, tool: Tool, feedback_bundle: FeedbackBundle) -> Action:
        prev_feedback = feedback_bundle.get_last_feedback()
        if prev_feedback.success:
            prompt = self.prompts['turn_to_action'].format(step=step, tool=tool)
            response = self.llm_call(prompt)
            json_obj = self._parse_response(response)
            action = self._retrieve_action(json_obj)
            step.action = action
            feedback = self._retrieve_feedback(json_obj)
            self._log(TurnToActionLog(prompt, response, action, feedback=feedback))
            feedback_bundle.append(feedback)
            return action
        else:
            return None

    def execute_action(self, action: Action, feedback_bundle: FeedbackBundle):
        if action:
            data = self.monitor(action.tool.func, action.tool_input)
            feedback = data.feedback_bundle.get_last_feedback()
            # TODO: Figure out how to store data and what to do with it
            self.context.data = data
        else:
            feedback = Feedback("No action to execute", success=False)
        self._log(ExecutionLog(action, data, feedback=feedback))
        feedback_bundle.append(feedback)

    def monitor(self, func: Callable, input: str) -> DataBundle:
        # TODO: Implement monitoring
        data = func(input)
        return data
        
    def _parse_response(self, response: str):
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
        return json_obj
    
    def _validate_scope_llm_call(self, user_goal: str, history: List[str], scope: Scope) -> Feedback:
        prompt = self.prompts['validate_scope'].format(user_goal=user_goal, 
                                                       history=history,
                                                       scope=scope)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        feedback = self._retrieve_feedback(json_obj)
        return feedback
    
    def _get_scope_description(self, user_goal: str, scope: Scope) -> str:
        validation_instructions = ""
        is_valid = False
        while is_valid != True:
            description = self._describe_scope_llm_call(user_goal, scope, validation_instructions)
            data = self._validate_scope_description_llm_call(user_goal, scope, description)
            feedback = data.feedback_bundle.get_last_feedback()
            validation_instructions = data['validation_instructions']
            is_valid = feedback.success

    def _describe_scope_llm_call(self, user_goal: str, scope: Scope, validation_instructions: str) -> str:
        prompt = self.prompts['describe_scope'].format(user_goal=user_goal, 
                                                       scope=scope,
                                                       validation_instructions=validation_instructions)
        response = self.llm_call(prompt)
        self._log(LLMLog(prompt, response, 'describe_scope'))
        return response
    
    def _validate_scope_description_llm_call(self, user_goal: str, scope: Scope, description: str):
        prompt = self.prompts['validate_scope_description'].format(user_goal=user_goal, 
                                                                   scope=scope, 
                                                                   description=description)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        feedback = self._retrieve_feedback(json_obj)
        validation_instructions = self._retrieve_validation_instructions(json_obj)
        data = DataBundle({"validation_instructions": validation_instructions}, feedback)
        self._log(ValidationLog(prompt, response, feedback, data.data))
        return data
            
    def _get_user_goal(self, user_query) -> str:
        # TODO: Set a limit on the number of times this can be called
        validation_instructions = ""
        is_valid = False
        while is_valid != True:
            user_goal = self._retrieve_goal_llm_call(user_query, validation_instructions)
            data = self._validate_goal_llm_call(user_query, user_goal)
            feedback = data.feedback_bundle.get_last_feedback()
            validation_instructions = data['validation_instructions']
            is_valid = feedback.success
        self._log(GoalUpdateLog(None, user_goal))
        return user_goal
    
    def _retrieve_goal_llm_call(self, user_query: str, validation_instructions: str = ""):
        print(user_query)
        prompt = self.prompts['retrieve_goal'].format(user_query=user_query,
                                                      validation_instructions=validation_instructions)
        response = self.llm_call(prompt)
        try:
            json_obj = self._parse_response(response)
            if "user_goal" in json_obj:
                user_goal = json_obj["user_goal"]
            else:
                user_goal = None
            self._log(RetrievalLog(prompt, response, {"user_goal": user_goal}))
        except json.JSONDecodeError:
            user_goal = response
            self._log(RetrievalLog(prompt, response, {"user_goal": user_goal}))
        return user_goal
    
    def _validate_goal_llm_call(self, user_query: str, user_goal: str) -> DataBundle:
        prompt = self.prompts['validate_goal'].format(user_query=user_query, 
                                                      user_goal=user_goal)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        feedback = self._retrieve_feedback(json_obj)
        validation_instructions = self._retrieve_validation_instructions(json_obj)
        data = DataBundle({"validation_instructions": validation_instructions}, feedback)
        self._log(ValidationLog(prompt, response, feedback, data.data))
        return data
             
    def _update_requirements(self, answer: str) -> List[str]:
        validation_instructions = ""
        is_valid = False
        user_goal = self.context.scope.user_goal
        while is_valid != True:
            requirements = self._retrieve_requirements_llm_call(user_goal, answer, validation_instructions)
            data = self._validate_requirements(requirements, user_goal, answer)
            feedback = data.feedback_bundle.get_last_feedback()
            validation_instructions = data['validation_instructions']
            is_valid = feedback.success
        return requirements
    
    def _retrieve_requirements_llm_call(self, user_goal: str, answer: str, validation_instructions: str):
        prompt = self.prompts['retrieve_requirements'].format(user_goal=user_goal, 
                                                              answer=answer,
                                                              validation_instructions=validation_instructions)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        if "requirements" in json_obj:
            requirements = json_obj["requirements"]
            # print(requirements)
        else:
            requirements = None
        self._log(RetrievalLog(prompt, response, {"requirements": requirements})) 
        return requirements
    
    def _validate_requirements(self, requirements: List[str], user_goal: str, answer: str) -> DataBundle:
        prompt = self.prompts['validate_requirements'].format(user_goal=user_goal, 
                                                              requirements=requirements,
                                                              answer=answer)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        feedback = self._retrieve_feedback(json_obj)
        validation_instructions = self._retrieve_validation_instructions(json_obj)
        data = DataBundle({"validation_instructions": validation_instructions}, feedback)
        self._log(ValidationLog(prompt, response, feedback, data.data))
        return data
    
    def _get_plan_creation(self, description: str, validation_instructions: str = "") -> Plan:
        is_valid = False
        while is_valid != True:
            plan = self._create_plan_llm_call(description, validation_instructions)
            data = self._validate_create_plan_llm_call(plan, description)
            feedback = data.feedback_bundle.get_last_feedback()
            validation_instructions = data['validation_instructions']
            is_valid = feedback.success
        return plan
    
    def _get_plan_update(self, description: str, feedback: Feedback, previous_plan: Plan, validation_instructions: str = "") -> Plan:
        is_valid = False
        while is_valid != True:
            plan = self._update_plan_llm_call(description, 
                                              feedback, 
                                              previous_plan, 
                                              validation_instructions)
            data = self._validate_update_plan_llm_call(plan, description)
            feedback = data.feedback_bundle.get_last_feedback()
            validation_instructions = data['validation_instructions']
            is_valid = feedback.success
        return plan
    
    def _create_plan_llm_call(self, description: str, validation_instructions: str = "") -> Plan:
        prompt = self.prompts['create_plan'].format(description=description,
                                                    validation_instructions=validation_instructions)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        plan = self._retrieve_plan(json_obj)
        self._log(PlanUpdateLog(prompt, response, None, plan))
        return plan
    
    def _update_plan_llm_call(self, description: str, feedback: Feedback, previous_plan: Plan, validation_instructions: str = "") -> Plan:
        prompt = self.prompts['update_plan'].format(description=description, 
                                                    feedback=feedback,
                                                    previous_plan=previous_plan,
                                                    validation_instructions=validation_instructions)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        plan = self._retrieve_plan(json_obj)
        self._log(PlanUpdateLog(prompt, response, previous_plan, plan))
        return plan
    
    def _validate_create_plan_llm_call(self, plan: Plan, description: str) -> DataBundle:
        prompt = self.prompts['validate_create_plan'].format(plan=plan, description=description)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        feedback = self._retrieve_feedback(json_obj)
        validation_instructions = self._retrieve_validation_instructions(json_obj)
        data = DataBundle({"validation_instructions": validation_instructions}, feedback)
        self._log(ValidationLog(prompt, response, feedback, data.data))
        return data
    
    def _validate_update_plan_llm_call(self, plan: Plan, description: str) -> DataBundle:
        prompt = self.prompts['validate_update_plan'].format(plan=plan, description=description)
        response = self.llm_call(prompt)
        json_obj = self._parse_response(response)
        feedback = self._retrieve_feedback(json_obj)
        validation_instructions = self._retrieve_validation_instructions(json_obj)
        data = DataBundle({"validation_instructions": validation_instructions}, feedback)
        self._log(ValidationLog(prompt, response, feedback, data.data))
        return data

    def _retrieve_feedback(self, json_obj: Dict[str, str]) -> Feedback:
        # retrieve the feedback from the JSON object
        if "feedback" in json_obj:
            feedback_dict = json_obj["feedback"]
            message = feedback_dict["message"]
            success = feedback_dict["success"]
            feedback = Feedback(message, success=success)
            print(feedback)
        else:
            feedback = None
        return feedback
    
    def _retrieve_validation_instructions(self, json_obj: Dict[str, str]) -> str:
        if "validation_instructions" in json_obj:
            validation_instructions = json_obj["validation_instructions"]
            print(validation_instructions)
        else:
            validation_instructions = None
        return validation_instructions
    
    def _retrieve_plan(self, json_obj: Dict[str, str]) -> Plan:
        if "plan" in json_obj:
            plan_dict = json_obj['plan']
            steps = []
            for step_name, description in plan_dict.items():
                step = Step(step_name, description)
                steps.append(step)
            plan = Plan(steps)
            print(plan)
        else:
            plan = None
        return plan
    
    def _retrieve_tool(self, json_obj: Dict[str, str]) -> Tool:
        if "tool" in json_obj:
            tool_dict = json_obj['tool']
            tool = self.query_tool(tool_dict)
            print(tool)
        else:
            tool = None
        return tool
    
    def _retrieve_action(self, json_obj: Dict[str, str], step: Step, tool: Tool) -> Action:
        if "action" in json_obj:
            action_dict = json_obj['action']
            tool_input = action_dict['tool_input']
            action = Action(step, tool, tool_input)
            print(action)
        else:
            action = None
        return action

    def query_tool(self, tool_dict: Dict[str, str]) -> List[Tool]:
        # query the database for the tools
        pass

    def llm_call(self, prompt: str) -> str:
        return llm_call(prompt)
    
    def add_iteration(self):
        self.logger.add_iteration()

    def _log(self, log: Log):
        #print(log)
        self.logger.log(log)

