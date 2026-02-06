# INTUITION-Hackathon-
This repository contains the INTUITION Hackathon project by V SPRING team. The app analyzes screenshots, provides descriptions and interactions, and includes optional haptic feedback on Windows.

**Repository Structure**
- Main/: Main application modules and entrypoint
	- main.py: Application entrypoint (runs the UI/interaction loop)
	- ID_selector.py: Semantic ID selector helper
	- grid_based_screenshot.py: Screenshot utilities
	- converter.py: Speech/text conversion helpers
	- extract_feature.py / extract_feature_current.py: Page extraction utilities
	- haptics.py: Windows haptic feedback helper (uses winsound)
	- interaction.py: Interaction automation helpers
	- Response Model.py, Holo2 Model.py: model-related helpers
- screenshots/: Example screenshots
- ui_map.json: UI mapping used by `haptics.py` and ID selection

**Prerequisites**
- Python 3.10+ (the code uses modern typing and libraries)
- Windows recommended for `haptics.py` (uses `winsound` and `pyautogui`)
- (Optional) GPU + CUDA for running large vision-language models like `microsoft/Florence-2-large`

**Install**
1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

**Run (development / local)**
```powershell
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\sel_temp" for debug Google
```
Visit the debug-mode google for to test our following feature
Press F for describe the webpage (MORE_DETAILED_CAPTION)
Press G to read the webpage in detail (OCR)
Press J to execute action you want
