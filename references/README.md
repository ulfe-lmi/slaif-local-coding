# Reference-only material

`qwen38_vision_image_cap_proxy.py` is the proven local workaround supplied from
the current deployment. It recursively retains only the newest Responses/Chat
image item. It is **not** the product runtime and must not be installed as a
second client-side proxy by this repository.

Objective 000 ports its pure transformation behavior into the common private
adapter, adds route policy, async/SSE correctness, security bounds, tests, and
configuration. The supplied proxy is reference code only; no deployed port-18021
service is assumed on the target machine.
