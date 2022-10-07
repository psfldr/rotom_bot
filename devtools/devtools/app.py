from invoke import Program
from .main_tasks import ns
from .run_test_tasks import run_test_ns

__VERSION__ = "0.1.0"
ns.add_collection(run_test_ns)
app = Program(version=__VERSION__, namespace=ns)

if __name__ == "__main__":
    app.run()
