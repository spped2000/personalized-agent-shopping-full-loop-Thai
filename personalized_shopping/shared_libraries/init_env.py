# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gym
import os

gym.envs.registration.register(
    id="WebAgentTextEnv-v0",
    entry_point=(
        "personalized_shopping.shared_libraries.web_agent_site.envs.web_agent_text_env:WebAgentTextEnv"
    ),
)


def init_env(num_products, file_path=None):
    # Use smaller data file for faster loading
    if file_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if num_products and num_products <= 1000:
            file_path = os.path.join(base_dir, "data/items_shuffle_1000.json")
        elif num_products and num_products <= 10000:
            # Use 1000 item file and let the environment slice to 10k
            # This is faster than loading the full 5.2GB file
            file_path = os.path.join(base_dir, "data/items_shuffle_1000.json")
        else:
            file_path = os.path.join(base_dir, "data/items_shuffle.json")

    env = gym.make(
        "WebAgentTextEnv-v0",
        observation_mode="text",
        num_products=num_products,
        file_path=file_path,
    )
    return env


num_product_items = 1000  # Use 1,000 items for fast performance
_webshop_env = None


def get_webshop_env():
    """Lazy-load the webshop environment on first access."""
    global _webshop_env
    if _webshop_env is None:
        _webshop_env = init_env(num_product_items)
        _webshop_env.reset()
        print(f"Finished initializing WebshopEnv with {num_product_items} items.")
    return _webshop_env
