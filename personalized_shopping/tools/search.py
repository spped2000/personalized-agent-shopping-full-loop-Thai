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


async def search(keywords: str, tool_context: ToolContext) -> str:
    """Search for keywords in the webshop.

    Args:
      keywords(str): The keywords to search for.
      tool_context(ToolContext): The function context.

    Returns:
      str: The search result displayed in a webpage with product details including images and ASINs.
    """
    from bs4 import BeautifulSoup

    webshop_env = get_webshop_env()
    status = {"reward": None, "done": False}
    action_string = f"search[{keywords}]"
    webshop_env.server.assigned_instruction_text = f"Find me {keywords}."
    print(f"env instruction_text: {webshop_env.instruction_text}")
    _, status["reward"], status["done"], _ = webshop_env.step(action_string)

    ob = webshop_env.observation
    index = ob.find("Back to Search")
    if index >= 0:
        ob = ob[index:]

    # Extract product details from HTML
    html = webshop_env.state["html"]
    soup = BeautifulSoup(html, "html.parser")

    # Extract product information
    products_info = []
    product_links = soup.find_all(class_="product-link")

    for link in product_links:
        asin = link.get_text().strip()
        # Find the parent container to get associated product details
        product_container = link.find_parent("div", class_="item")
        if product_container:
            # Extract image
            img_tag = product_container.find("img")
            image_url = img_tag.get("src") if img_tag else None

            # Extract title
            title_tag = product_container.find("h4")
            title = title_tag.get_text().strip() if title_tag else "N/A"

            # Extract price
            price_tag = product_container.find("p")
            price = price_tag.get_text().strip() if price_tag else "N/A"

            products_info.append({
                "asin": asin,
                "title": title,
                "price": price,
                "image": image_url
            })

    # Enhance observation with product details
    if products_info:
        enhanced_ob = ob + "\n\n=== PRODUCT DETAILS ===\n"
        for i, product in enumerate(products_info, 1):
            enhanced_ob += f"\n{i}. Product ID (ASIN): {product['asin']}\n"
            enhanced_ob += f"   Title: {product['title']}\n"
            enhanced_ob += f"   Price: {product['price']}\n"
            if product['image']:
                enhanced_ob += f"   Image URL: {product['image']}\n"
        ob = enhanced_ob

    print("#" * 50)
    print("Search result:")
    print(f"status: {status}")
    print(f"observation: {ob}")
    print("#" * 50)

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
