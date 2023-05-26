from __future__ import annotations

import time

from typing import List, Dict, Tuple, Callable, Optional
from model.feedback_model import Feedback, FeedbackBundle, DataBundle
from deus_utils import get_workflow_id, get_workflow_step_id


class WorkflowStep:
    id: str
    name: str
    description: str
    func: Callable
    next_step_condition: Callable

    def __init__(self,
                 name: str, 
                 description: str,
                 func: Callable,
                 next_step_condition: Callable):
        self.id = get_workflow_step_id()
        self.name = name
        self.description = description
        self.func = func
        self.next_step_condition = next_step_condition

class Workflow:
    id: str
    steps: List[WorkflowStep]

    def __init__(self, steps: List[WorkflowStep]):
        self.id = get_workflow_id()
        self.steps = steps

class WorkflowExecutor:
    current_step: WorkflowStep

    def execute_workflow(self, workflow: Workflow, data: DataBundle) -> FeedbackBundle:
        self.current_step = step = workflow.steps[0]
        while step is not None:
            feedback = self.execute_step(step, data)
            data.feedback_bundle.append(feedback)
            self.current_step = step = self.compute_next_step(step, data)
            time.sleep(1)
            
    def execute_step(self, step: WorkflowStep, data: DataBundle) -> Feedback:
        print(f"Executing step: {step.id} ({step.name})")
        feedback = self.monitor(step.func, data)
        return feedback

    def monitor(self, func: Callable, data) -> Feedback:
        feedback = func(data)
        return feedback

    def compute_next_step(self, step: WorkflowStep, data: DataBundle) -> WorkflowStep:
        return step.next_step_condition(data)