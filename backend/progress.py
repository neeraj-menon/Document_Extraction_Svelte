progress_data = {"percentage": 0, "status": ""}


# Update the progress function to store the current progress and status
def update_progress(percentage, status):
    global progress_data
    progress_data["percentage"] = percentage
    progress_data["status"] = status
