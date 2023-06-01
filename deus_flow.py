from model.deus_flow_model import ContextManager
from model.workflow_model import Workflow, WorkflowStep, WorkflowExecutor
from model.feedback_model import Feedback, FeedbackBundle, DataBundle
import traceback

# @flow(log_prints=True)
# def deus_flow(user_query: str) -> str:
#     # Store the task, requirements, constraints in a global variable.
#     context_manager = establish_scope(user_query)
#     result = core_loop(context_manager)
#     return result

def establish_scope(user_query: str) -> ContextManager:
    context_manager = ContextManager(user_query)
    context_manager.set_scope()
    return context_manager

# @flow(log_prints=True)
# def core_loop(context_manager: ContextManager):
#     while (context_manager.context.finished!=True):
#         context_manager.planner()
#         context_manager.task_handler()
#         context_manager.add_iteration()

def establish_scope_step(data: DataBundle) -> Feedback:
    try:
        data['context_manager'] = establish_scope(data['user_query'])
        return Feedback(success=True, message="Scope established")
    except Exception as e:
        print(traceback.format_exc(e))
        return Feedback(success=False, message="Scope not established: " + traceback.format_exc(e))

def establish_scope_condition(data: DataBundle) -> WorkflowStep:
    workflow_feedback = data.feedback_bundle.get_last_feedback()
    if workflow_feedback.success:
        print("Establish scope successful")
        return planning_workflow_step
    else:
        print("Establish scope unsuccessful")
        return establish_scope_workflow_step

def planning_step(data: DataBundle) -> Feedback:
    try:
        context_manager = data['context_manager']
        context_manager.planner()
        return Feedback(success=True, message="Planning successful")
    except Exception as e:
        return Feedback(success=False, message="Planning unsuccessful: " + traceback.format_exc(e))
    
def planning_condition(data: DataBundle) -> WorkflowStep:
    workflow_feedback = data.feedback_bundle.get_last_feedback()
    if workflow_feedback.success:
        return task_handling_workflow_step
    else:
        return planning_workflow_step
    
def task_handling_step(data: DataBundle) -> Feedback:
    try:
        context_manager = data['context_manager']
        context_manager.task_handler()
        context_manager.add_iteration()
        return Feedback(success=True, message="Task handling successful")
    except Exception as e:
        return Feedback(success=False, message="Task handling unsuccessful: " + traceback.format_exc(e))
    
def task_handling_condition(data: DataBundle) -> WorkflowStep:
    context_manager = data['context_manager']
    if context_manager.context.finished:
        return None
    return planning_workflow_step

establish_scope_workflow_step = WorkflowStep("Establish scope", "Establish the scope of the user's query", establish_scope_step, establish_scope_condition)
planning_workflow_step = WorkflowStep("Planning", "Plan to achieve the user's goal", planning_step, planning_condition)
task_handling_workflow_step = WorkflowStep("Task handling", "Handle the task", task_handling_step, task_handling_condition)

deus_flow = Workflow([establish_scope_workflow_step, planning_workflow_step, task_handling_workflow_step])

executor = WorkflowExecutor()
data = DataBundle(data={"user_query": "Make me a program that can play chess"},
                  feedback=FeedbackBundle())
executor.execute_workflow(deus_flow, data)