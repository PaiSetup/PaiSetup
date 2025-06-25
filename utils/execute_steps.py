from steps.step import FrameworkStep, Step
from utils.dependency_dispatcher import (
    DependencyDispatcher,
    DependencyResolutionMode,
    DependencyType,
)


def find_step_by_name(steps, name):
    for step in steps:
        if step.name.lower() == name.lower():
            return step
    raise ValueError(f'Cannot find step named "{name}"')


def execute_steps(
    root_dir,
    services,
    steps,
    step_whitelist,
    step_blacklist,
    dependency_resolution_mode,
    allow_unsatisfied_push_dependencies,
    list_steps,
    list_packages,
    pause,
):
    # Filter steps by command line args
    Step._logger.log("Filtering steps")
    if step_whitelist and step_blacklist:
        raise ValueError("Cannot pass both whitelist and blacklist")
    if step_whitelist:
        for step in steps:
            step.set_enabled(False)
        for step_name in step_whitelist:
            find_step_by_name(steps, step_name).set_enabled(True)
    if step_blacklist:
        for step_name in step_blacklist:
            find_step_by_name(steps, step_name).set_enabled(False)

    # Add framework step
    steps.insert(0, FrameworkStep(root_dir))

    # Setup env
    Step._logger.log("Setting up environment variables")
    for step in steps:
        step.register_env_variables()

    # Handle cross-step dependencies
    Step._logger.log("Handling steps dependencies")
    dependencies = DependencyDispatcher(dependency_resolution_mode, allow_unsatisfied_push_dependencies, services.get_logger())
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
