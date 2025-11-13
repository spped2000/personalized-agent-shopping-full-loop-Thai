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

from google.adk.tools import ToolContext
from google.genai import types

from ..shared_libraries.init_env import get_webshop_env


async def click(button_name: str, tool_context: ToolContext) -> str:
    """Click the button with the given name.

    Args:
      button_name(str): The name of the button to click.
      tool_context(ToolContext): The function context.

    Returns:
      str: The webpage after clicking the button with enhanced product details including images and ASIN.
    """
    from bs4 import BeautifulSoup

    webshop_env = get_webshop_env()
    status = {"reward": None, "done": False}
    action_string = f"click[{button_name}]"
    _, status["reward"], status["done"], _ = webshop_env.step(action_string)

    ob = webshop_env.observation
    index = ob.find("Back to Search")
    if index >= 0:
        ob = ob[index:]

    # Extract product details from HTML if on product page
    html = webshop_env.state["html"]
    soup = BeautifulSoup(html, "html.parser")

    # Check if we're on a product page (item_page)
    product_image = soup.find(id="product-image")
    if product_image:
        # Extract product information from the product page
        image_url = product_image.get("src")

        # Extract ASIN from URL or page
        current_url = webshop_env.state["url"]
        asin = None
        if "/item_page/" in current_url:
            url_parts = current_url.split("/")
            if len(url_parts) > 4:
                asin = url_parts[4]

        # Extract title
        title_elem = soup.find("h2")
        title = title_elem.get_text().strip() if title_elem else "N/A"

        # Extract price
        price_elem = soup.find("h3")
        price = price_elem.get_text().strip() if price_elem else "N/A"

        # Extract rating
        rating_elem = soup.find("span", class_="rating")
        rating = rating_elem.get_text().strip() if rating_elem else "N/A"

        # Extract available options (colors, sizes)
        options = {}
        option_sections = soup.find_all("div", class_="radio-toolbar")
        for section in option_sections:
            option_name = section.find_previous("h4")
            if option_name:
                option_type = option_name.get_text().strip().rstrip(":")
                option_values = [label.get_text().strip() for label in section.find_all("label")]
                if option_values:
                    options[option_type] = option_values

        # Enhance observation with structured product details
        enhanced_ob = ob + "\n\n=== PRODUCT DETAILS ===\n"
        if asin:
            enhanced_ob += f"🔖 Product ID (ASIN): {asin}\n"
        enhanced_ob += f"📦 Title: {title}\n"
        enhanced_ob += f"💰 Price: {price}\n"
        enhanced_ob += f"⭐ Rating: {rating}\n"
        if image_url:
            enhanced_ob += f"🖼️ Image URL: {image_url}\n"

        if options:
            enhanced_ob += "\n📋 Available Options:\n"
            for option_type, values in options.items():
                enhanced_ob += f"   {option_type}: {', '.join(values)}\n"

        ob = enhanced_ob

    print("#" * 50)
    print("Click result:")
    print(f"status: {status}")
    print(f"observation: {ob}")
    print("#" * 50)

    if button_name == "Back to Search":
        webshop_env.server.assigned_instruction_text = "Back to Search"

    # Show artifact in the UI.
    try:
        await tool_context.save_artifact(
            "html",
            types.Part.from_uri(
                file_uri=webshop_env.state["html"], mime_type="text/html"
            ),
        )
    except ValueError as e:
        print(f"Error saving artifact: {e}")
    return ob
