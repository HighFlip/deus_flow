from prefect import flow, task
from model.flow_model import ContextManager


@flow(log_prints=True)
def deus_flow(user_query: str) -> str:
    # Store thje task, requirements, constraints in a global variable.
    context_manager = establish_scope(user_query)
    result = core_loop(context_manager)
    return result

@task
def establish_scope(user_query: str) -> ContextManager:
    context_manager = ContextManager(user_query)
    ask_user_flow(context_manager)
    return context_manager


@task
def ask_user_flow(context_manager: ContextManager):
    while (context_manager.validate_scope()!=True):
        context_manager.ask_user_llm_call()

@flow(log_prints=True)
def core_loop(context_manager: ContextManager):
    while (context_manager.current_context.finished!=True):
        context_manager.planner()
        context_manager.task_handler()
        context_manager.add_iteration()

    







