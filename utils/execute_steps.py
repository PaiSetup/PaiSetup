from steps.step import Step
from utils.dependency_dispatcher import (
    DependencyDispatcher,
    DependencyResolutionMode,
    DependencyType,
)


def execute_steps(
    steps,
    filtered_steps=None,
    dependency_resolution_mode=DependencyResolutionMode.pull_and_push,
    list_steps=False,
    list_packages=False,
    pause=False,
):
    # Filter steps by command line args
    Step._logger.log("Filtering steps")
    if filtered_steps != None:
        allowed_names = [x.lower() for x in filtered_steps]
        for step in steps:
            if step.name.lower() not in allowed_names:
                step.set_enabled(False)

    # Setup env
    Step._logger.log("Setting up environment variables")
    for step in steps:
        step.register_env_variables()

    # Handle cross-step dependencies
    Step._logger.log("Handling steps dependencies")
    dependencies = DependencyDispatcher(dependency_resolution_mode)
    for step in steps:
        dependencies.register_handlers(step)
    dependencies.resolve_dependencies(steps)

    # List steps
    if list_steps:
        for step in steps:
            if step.is_enabled():
                print(step.name)
        return

    # List packages
    if list_packages:
        with dependencies.enable_external_dependency_pulling():
            packages = dependencies.query_installed_packages()
        packages = "\n".join(packages)
        print(packages)
        return

    # Run the steps
    with Step._logger.indent("Executing steps"):
        for step in steps:
            if step.is_enabled() and step.is_method_overriden(Step.perform):
                if pause:
                    input()
                Step._logger.log(f"Performing step: {step.name}", short_message=f"{step.name}Step")
                with Step._logger.indent():
                    step.perform()

    # Finalize services
    Step.finalize_services()
