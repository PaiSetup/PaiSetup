#!/usr/bin/env python3

import utils
from steps.step import Step
from tests.push_chain import test_in_order_chain, test_reverse_order_chain

# Setup services.
Step.setup_external_services("root", None, False, False)

test_reverse_order_chain()
test_in_order_chain()
