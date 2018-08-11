
class Renderer:

    def __init__(self, str, options):
        self.str = str
        self.options = options

    def render(self):
        return "Hello there!"


def render(str, options):
    return Renderer(str, options).render()
