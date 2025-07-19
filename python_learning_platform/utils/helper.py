def calculate_score(user_answers, correct_answers):
    return sum(1 for user, correct in zip(user_answers, correct_answers) if user == correct)
