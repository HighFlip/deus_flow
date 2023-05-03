
from prefect import flow

import openai

# Problems we are trying to solve
# The current agent tools cannot accomplish really complex tasks.
# Ability to use a lot of tools without over utilizing tokens.
# Ability to find exactly the right the tool for the task.
# Increase the number of tools that the system can use
# Agents do a ton of steps that are wasteful and not needed towards the actually goal.
# Agents don't know how to actually use the tools for the tasks because they don't understand the real world - and it can take a ton of tasks to figure out the right solution.
# If previous agents have completed several tasks, then when they need to do a new task, we actually might already have the data to accomplish the task more quickly and accurately.
# 





# Possible solutions
# Better finding of tools.
# Planning at a high-level the steps (to be able to complete complex tasks)

def llm_call(prompt: str, user_query: str, model: str = 'gpt-4'):
    messages = [
        {
        "role": "system", "content": prompt
        },
        {
        "role": "user", "content": user_query
        }]


    return openai.ChatCompletion.create(
            model=model, temperature=0, max_tokens=7000, messages=messages, stop="STOP")


@flow(log_prints=True)
def deus_flow(user_query: str) -> str:
    # Store thje task, requirements, constraints in a global variable.
    scope = establish_scope(user_query)



def plan_do_task_loop(user_query, scope, last_task_result=None):
    finished = False
    task_result = None
    while (finished != True):
      # Generate entire plan and includes the first step. (Will research different ways to achieve, come up with the best plan.)
      plan = executive_establish_plan(scope.query_summary, scope, task_result)
      if plan.has_next_step() is False:
          return plan

      # Will take the step. It will try to either have someone execute it or do research or break the task down in to something more granular.
      task_result = task_handler()
      beginning = False



class FEEDBACK_ENUM(Enum):
    NEEDS_TOOL = 'NEEDS_TOOL'
    NEEDS_BROKEN_DOWN = 'NEEDS_BROKEN_DOWN'


class TaskError:
    feedback: FEEDBACK_ENUM
    feedback_instructions: str

class TaskResults:
    success: bool
    result: str
    error: TaskError

@flow(log_prints=True)
def tool_executor(step) -> TaskResults:
    results = run_tool(step)
    if results.success is False:
        return TaskResults(success=False, error=TaskError(feedback=FEEDBACK_ENUM.TOOL_FAILED, feedback_instructions=f"Running the tool failed. These were the results: {results.error}"))
    assessment = assess_task_results(results)


@flow(log_prints=True)
def task_handler(overall_goal, step) -> str:
    if can_be_handled_by_single_agent:
        if has_tool:
          results = tool_executor(first_step)
          if results.success is False:
              return TaskResults(success=False, error=TaskError(feedback=FEEDBACK_ENUM.TOOL_FAILED, feedback_instructions=f"Running the tool failed. These were the results: {results.error}")
              
          return TaskResults(success=True, result=results)
        else:
            return TaskResults(success=False, error=TaskError(feedback=FEEDBACK_ENUM.NEEDS_TOOL, feedback_instructions="There is no available tool for this task. A possible tool could be X."))
    else:
        return executive_establish_plan.problem_step(scope.query_summary, scope, problem_step=step, feedback=FEEDBACK_ENUM.NEEDS_BROKEN_DOWN)


