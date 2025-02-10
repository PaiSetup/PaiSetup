from steps.step import Step
from utils.dependency_dispatcher import DependencyDispatcher, DependencyType


def execute_steps(steps, filtered_steps=None, list_steps=False, list_packages=False):
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
    dependencies = DependencyDispatcher()
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
        dependencies.list_packages(True)
        return

    # Run the steps
    with Step._logger.indent("Executing steps"):
        for step in steps:
            if step.is_enabled() and step.is_method_overriden(Step.perform):
                Step._logger.log(f"Performing step: {step.name}", short_message=f"{step.name}Step")
                with Step._logger.indent():
                    step.transition_state(Step.State.Performed, None)

    # Finalize services
    Step.finalize_services()
