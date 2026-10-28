---
name: optimize-setup
description: Workflow for finding and removing slow parts of a setup.py run (execution speed / performance). Use ONLY when the user explicitly asks to optimize or speed up the setup - never on your own initiative.
---

# Optimizing setup.py execution speed

`setup.py` is idempotent and run often, so the goal is a fast *repeated* run: steps should notice the work
is already done and skip it. Follow the workflow below in order.

## 1. Run the entire setup

Always run the full setup - no `--step_whitelist`/`--step_blacklist`, no `--strict_*` flags (they disable the
existing shortcuts and distort the measurement). Steps influence each other through the dependency
dispatcher and the FileWriter, so a partial run doesn't represent a real one.

```bash
python setup.py 2>&1 | tee <scratchpad>/setup_before.log
```

Run it in the foreground (not in the background) with a long timeout, directly in the main repo
checkout - never in a git worktree, since the setup configures the real machine from this repo. Run it as the regular
user - not as `sudo python setup.py`; steps invoke `sudo` themselves for the commands that need it, so
the user needs passwordless `sudo` privileges. If it blocks on a password prompt anyway, ask the user to
run it themselves with `! python setup.py 2>&1 | tee <path>`.
If the run did real one-time work (installed packages, built something new), run it once more - the
second run is the baseline to optimize.

## 2. Read the log

Every line is prefixed with the time elapsed since the **previous** log line. So the number on a line is
**not** the cost of that line - it is the cost of whatever the line *above* it was doing. To find what's
slow, find a big number and look one line up.

Indentation comes from `self._logger.indent(...)` (and from the engine, which indents each step's
`perform()`). The time of a parent line is spread over its children's deltas: the first child's delta is
the parent's own prologue, and the line *after* the block (next step, dedented) carries the time of the
last child's work.

### Example

Code (simplified `LightDmStep` and `PackagesStep`):

```python
def perform(self):                       # LightDmStep
    self._enable_service()
    self._configure()

def _enable_service(self):
    service_name = "lightdm.service"
    self._logger.log(f"Enabling {service_name}")
    run_command(f"sudo systemctl enable {service_name}")

def _configure(self):
    self._logger.log(f"Setting up config files in {config_path}")
    run_command(f"sudo cp ...")

def _install_packages(self):             # PackagesStep
    with self._logger.indent(f"Installing packages: {self._packages}"):
        missing_packages = self._get_missing_packages(self._packages)
        if not missing_packages:
            self._logger.log("All packages are already installed.")
```

Output:

```
[             ] Initializing steps
[   +412.08ms] Filtering steps
[     +0.31ms] Handling steps dependencies
[    +18.77ms] Executing steps
[     +0.02ms]     Performing step: Packages
[     +0.05ms]         Installing packages: ['git', 'lightdm', ...]
[  +1843.50ms]             All packages are already installed.
[     +3.12ms]     Performing step: LightDm
[     +0.04ms]         Enabling lightdm.service
[  +2210.66ms]         Setting up config files in /usr/share/lightdm
[    +35.20ms]     Performing step: Shell
```

Interpretation:

- `+412.08ms` on `Filtering steps` is the cost of `Initializing steps` (constructing all steps).
- `+1843.50ms` on `All packages are already installed.` is the cost of the line above it - the
  `_get_missing_packages()` query inside the `Installing packages` block. Its children start with
  `+0.05ms`, so the parent line itself did nothing expensive before the block.
- `+2210.66ms` on `Setting up config files` is the cost of `Enabling lightdm.service`, i.e.
  `systemctl enable` - run every time even though the service is long enabled. This is the prime
  candidate.
- `+35.20ms` on `Performing step: Shell` is the cost of the last LightDm line (the `cp` calls) - the
  next step's header carries the tail of the previous step.

## 3. Add logs when it's inconclusive

If a big delta covers several commands (e.g. a whole `perform()` with only one log line), you don't know
what's slow yet. Don't guess - add more log lines splitting the region, rerun the **entire** setup and read
again. Repeat until the slow thing is a single command or call.

- Use `self._logger.log(...)` for measurement points.
- Wrap groups in `with self._logger.indent("..."):` to see a subtree's breakdown.
- Remove purely diagnostic log lines once the investigation is done, unless they're worth keeping.

## 4. Find a way not to run the slow thing

Once the culprit is known, preferably avoid running it at all:

- **Query whether it's already done.** A read-only query is usually much faster than the action, and
  then we skip the action. This is what `LightDmStep` does now:

  ```python
  def _enable_service(self):
      # Check, if we can skip
      try:
          out = run_command("systemctl status display-manager", stdout=Stdout.return_back()).stdout
          out = out.splitlines()
          out = out[0]
          if "lightdm.service" in out:
              return
      except CommandError:
          # No display manager detected
          pass

      service_name = "lightdm.service"
      self._logger.log(f"Enabling {service_name}")
      run_command(f"sudo systemctl enable {service_name}")
  ```

  Similar patterns: compare file contents before copying, check `git rev-parse HEAD` before fetching,
  check if a binary/version exists before building, query installed packages before installing.
- **Look for faster arguments of the same command** - e.g. skipping refreshes/upgrades, `--quiet`
  modes, limiting scope (`--depth 1`, a single target instead of everything), batching many
  invocations into one.
- **Respect `self._flags`.** A shortcut that skips downloading/building/installing must be disabled by
  the matching `--strict_*` flag (`strict_download`, `strict_build`, `strict_install`), so the user can
  still force the full work.
- **Never write temporary cache/marker files** to remember that something was already done. They go
  stale and are too error prone. Always ask the real system for its actual state.

## 5. Propose, then ask

Present a table of proposed optimizations and ask the user which ones to implement (use
`AskUserQuestion` with `multiSelect: true`). Don't implement anything before the answer.

| # | Step | Slow operation | Current cost | Proposed change | Expected cost | Risk |
|---|------|----------------|--------------|-----------------|---------------|------|
| 1 | LightDm | `sudo systemctl enable lightdm.service` | 2210 ms | Skip if `systemctl status display-manager` shows lightdm | ~20 ms | Low |

## 6. Implement, rerun, report

Implement the chosen optimizations, following the `paisetup-step` skill. Then run the **entire** setup
again (`tee` to `setup_after.log`), verify it still succeeds and produces no new warnings, and report the
results in a second table:

| # | Step | Optimization | Before | After | Saved |
|---|------|--------------|--------|-------|-------|
| 1 | LightDm | Skip `systemctl enable` when already active | 2210 ms | 18 ms | 2192 ms |
|   | **Total run** | | 41.3 s | 39.1 s | 2.2 s |

Take "Before"/"After" from the same log lines in both runs. If an optimization didn't help as much as
expected, say so.
