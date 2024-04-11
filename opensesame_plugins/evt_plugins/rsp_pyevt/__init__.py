"""Plugin to collect input from a RSP-12x responsebox"""

authors = ["M. Stokroos"]
category = "RUG/BSS hardware"
help_url = 'https://github.com/MartinStokroos/evt-plugins'

# Defines the GUI controls
controls = [
    {
        "type": "combobox",
        "var": "_device",
        "label": "Select device :",
        "options": [
            "Keyboard"
        ],
        "name": "device_widget",
        "tooltip": "Select the desired RSP-device"
    },
    {
        "type": "line_edit",
        "var": "correct_response",
        "label": "Correct response :",
        "name": "correct_response_widget",
        "tooltip": "Choose the correct response, button (1-8)"
    },
    {
        "type": "line_edit",
        "var": "allowed_responses",
        "label": "Allowed responses :",
        "name": "allowed_response_widget",
        "tooltip": "Allowed responses (buttons 1-8) seperated by ';'"
    },
    {
        "type": "line_edit",
        "var": "timeout",
        "label": "Timeout period :",
        "name": "timeout_widget",
        "tooltip": "Expecting a value in milliseconds or 'infinite'"  
    }
]
