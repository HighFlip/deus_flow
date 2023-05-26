from typing import List, Dict

class Feedback:
    message: str
    success: bool

    def __init__(self, message: str, success: bool):
        self.message = message
        self.success = success
    
    def copy(self):
        return Feedback(self.message, self.success)

    def __str__(self):
        return self.message   
    
class FeedbackBundle:
    bundle: List[Feedback]
    summary: str
    success: bool

    def __init__(self, bundle: List[Feedback]|Feedback = None, summary: str = None, success: bool = None):
        if isinstance(bundle, Feedback):
            self.bundle = [bundle]
        elif bundle is None:
            self.bundle = []
        else:
            self.bundle = bundle
        self.summary = summary
        self.success = all([feedback.success for feedback in self.bundle]) if success is None else success

    def append(self, feedback: Feedback):
        self.bundle.append(feedback)
        self.success = all([feedback.success for feedback in self.bundle])

    def copy(self):
        return FeedbackBundle(self.bundle.copy(), self.summary, self.success)
    
    def get_last_feedback(self):
        return self.bundle[-1]
    
    def __str__(self):
        return self.summary if self.summary is not None else "\n".join([str(feedback) for feedback in self.bundle])
    
class DataBundle:
    data: Dict
    feedback_bundle: FeedbackBundle

    def __init__(self, data: Dict, feedback: Feedback|FeedbackBundle = None):
        self.data = data
        self.feedback_bundle = FeedbackBundle([feedback]) if isinstance(feedback, Feedback) else feedback

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            return None
        
