from datetime import datetime
from model.feedback_model import Feedback, FeedbackBundle

class Log:
    timestamp: datetime
    feedback: Feedback|FeedbackBundle
    
    def __init__(self, feedback: Feedback = None):
        self.timestamp = datetime.now()
        self.feedback = feedback