from invoke import task, Collection, run
from .main_tasks import sync_ssm_parameters_to_localstack


@task
def flake8(c):  # type: ignore
    """flake8のテストを実行します。"""
    run("flake8 --verbose")


@task
def black(c):  # type: ignore
    """blackのテストを実行します。"""
    run("black --check .")


@task
def isort(c):  # type: ignore
    """isortのテストを実行します。"""
    run("isort --check", pty=True)


@task
def mypy(c):  # type: ignore
    """mypyのテストを実行します。"""
    run("mypy", pty=True)


@task(sync_ssm_parameters_to_localstack)
def pytest(c):  # type: ignore
    """pytestのテストを実行します。"""
    run("pytest --cov", pty=True)


@task(flake8, black, mypy, pytest, default=True)  # type: ignore
def all(c):  # type: ignore
    """すべてのテストを実行します。"""
    pass


run_test_ns = Collection("run_test")
run_test_ns.add_task(all)
run_test_ns.add_task(isort)
run_test_ns.add_task(flake8)
run_test_ns.add_task(black)
run_test_ns.add_task(mypy)
run_test_ns.add_task(pytest)
