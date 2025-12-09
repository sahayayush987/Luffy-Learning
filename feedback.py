
def safe_child_friendly_feedback(errors):
    if not errors:
        return "Great job! You read everything correctly. Keep it up! ⭐"

    message = "Nice work reading! Here are a few words you can practice:\n\n"
    for w in errors:
        message += f"• **{w}**\n"

    message += "\nYou're improving every time you read! 😊"
    return message
