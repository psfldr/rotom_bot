from invoke import Program
from .tasks import ns

__VERSION__ = "0.1.0"
app = Program(version=__VERSION__, namespace=ns)

if __name__ == "__main__":
    app.run()
