import pandas as pd
import numpy as np
import re

# For sanjana's conditional logic in questionnaire 
def should_display_question(question, saved_responses):
    """
    Determine whether a question should be displayed based on its dependencies.
    - `question` is an instance of CVD_risk_Questionnaire
    - `saved_responses` is a dict: {question_id: answer_value}
    """
    dependencies = question.trigger_questions.all()

    # If no dependencies, question is always shown
    if not dependencies:
        return True

    for dep in dependencies:
        trigger_qid = dep.triggering_question.question_id
        trigger_val = saved_responses.get(trigger_qid)

        if trigger_val is None:
            return False  # Dependency not met (triggering question unanswered)

        required_vals = str(dep.trigger_values).split(',')

        # Handle numeric expressions like >1, <=3
        match_found = False
        for val in required_vals:
            val = val.strip()
            try:
                if val.startswith('>'):
                    if float(trigger_val) > float(val[1:]):
                        match_found = True
                elif val.startswith('<'):
                    if float(trigger_val) < float(val[1:]):
                        match_found = True
                elif val.startswith('>='):
                    if float(trigger_val) >= float(val[2:]):
                        match_found = True
                elif val.startswith('<='):
                    if float(trigger_val) <= float(val[2:]):
                        match_found = True
                else:
                    # Exact match
                    if str(trigger_val) == val:
                        match_found = True
            except Exception as e:
                continue  # Ignore invalid expressions

        if not match_found:
            return False  # One dependency not satisfied

    return True  # All dependencies satisfied

