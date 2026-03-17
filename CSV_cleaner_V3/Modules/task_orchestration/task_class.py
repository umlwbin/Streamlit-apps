class Task:
    """
    A simple container for task information.
    """
    
    def __init__(self, name, func, widget, description, type="single", summary_renderer=None):
        self.name = name
        self.func = func
        self.widget = widget
        self.description = description
        self.type = type
        self.summary_renderer = summary_renderer

