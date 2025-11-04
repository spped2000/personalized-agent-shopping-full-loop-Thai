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

import os
import base64
from google.adk.tools import ToolContext
from google.genai import types


async def show_payment_qr(tool_context: ToolContext) -> str:
    """Display QR code for payment after user confirms purchase.

    Args:
      tool_context(ToolContext): The function context.

    Returns:
      str: Confirmation message that QR code is displayed.
    """
    # Get the QR code image path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qr_path = os.path.join(base_dir, "..", "qr_payments", "qr1.jpg")

    # Normalize the path
    qr_path = os.path.normpath(qr_path)

    print(f"Displaying payment QR code from: {qr_path}")

    # Check if file exists
    if not os.path.exists(qr_path):
        return f"Error: QR code file not found at {qr_path}"

    # Read the image file and encode as base64
    try:
        with open(qr_path, "rb") as image_file:
            image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

        # Show QR code as artifact in the UI using inline data
        await tool_context.save_artifact(
            "payment_qr",
            types.Part.from_bytes(
                data=image_data,
                mime_type="image/jpeg"
            ),
        )
        return "QR code for payment has been displayed. Please scan to complete your purchase."
    except Exception as e:
        return f"Error displaying QR code: {str(e)}"
