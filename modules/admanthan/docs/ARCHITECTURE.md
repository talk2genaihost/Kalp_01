# KALP AdManthan Architecture — v0.1 Working Implementation

Brief/Context → Strategy → Continuous VO → Scene Architect → Effect Intelligence → Visual/Audio Recipe → Storyboard → Production Bridge → QA/Delivery → Genie Handoff

### Effect Intelligence
The supplied workbook is the operational effect reference. It has 12 worksheets and 50 shortcut rows per worksheet (600 rows total). The implementation imports rows without renaming shortcuts.

### 15s/6-frame contract
Exactly six 2.5-second scene slots. One master VO string is retained, while scene VO fragments form a continuous sentence. This is a timing scaffold, not an audio render.

### Provider boundary
The Production Bridge creates provider-neutral jobs. Actual image/video/audio provider integration remains an adapter task; no provider is falsely claimed as implemented.
