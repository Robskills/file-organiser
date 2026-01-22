<<<<<<< HEAD
# File Organizer Pro

**File Organizer Pro** is a modern, AI-enhanced desktop application designed to declutter your digital life. It automatically classifies and organizes files into a logical hierarchy using a combination of deterministic rules and semantic AI analysis.

## Features

*   **Smart Hierarchical Organization**: Classifies files into groups (e.g., Documents, Images) and subcategories (e.g., Finance, Personal) based on file extensions and keyword matching.
*   **AI-Powered Classification**: Integrates with OpenAI (GPT-3.5/4) to semantically classify files that don't match strict rules, ensuring even ambiguous filenames are sorted correctly.
*   **AI Space Audit**: Analyzes your directories to identify cleanup opportunities (e.g., old installers, temporary files) and suggests new folder structures based on file clusters.
*   **Modern GUI**: A clean, responsive interface featuring:
    *   Dark and Light theme support.
    *   Real-time log output.
    *   Tabbed settings and about pages.
*   **Secure Configuration**: API keys are stored securely using local obfuscation, ensuring they are never saved in plain text.
*   **Fully Customizable**: Edit taxonomy rules (JSON) directly within the app to tailor the organization logic to your needs.
*   **Safety First**: Includes a "Dry Run" mode to preview actions before moving any files, and handles duplicate files safely.

## Installation

### Option 1: Running from Source

1.  **Prerequisites**: Ensure you have Python 3.8 or higher installed.
2.  **Install Dependencies**:
    ```bash
    pip install openai pyinstaller
    ```
    *(Note: `tkinter` is usually included with standard Python installations)*
3.  **Run the Application**:
    ```bash
    python c:\Users\roone\organisr\gui.py
    ```

### Option 2: Building the Executable

You can create a standalone Windows executable (`.exe`) to run the app without Python installed.

1.  Run the included build script:
    ```bash
    python c:\Users\roone\organisr\build.py
    ```
2.  The build script will:
    *   Use **PyInstaller** to bundle the application.
    *   (Optional) Use **Inno Setup** (if installed) to generate an installer file.
3.  Find your executable in the `dist/` folder (e.g., `dist/FileOrganizerPro.exe`).

## Usage

1.  **Launch the App**: Open `FileOrganizerPro.exe` or run the python script.
2.  **Select Directories**:
    *   **Source Directory**: The folder you want to clean up (e.g., your Downloads folder).
    *   **Destination Directory**: The root folder where organized files will be moved.
3.  **Choose Mode**:
    *   **Dry Run**: Check this box to simulate the organization. The log will show what *would* happen without moving files.
    *   **Uncheck Dry Run** to perform the actual file moves.
4.  **AI Features**:
    *   **AI Space Audit**: Click this button to scan for space-saving opportunities without moving files.
    *   **Semantic Classification**: Go to the **Settings** tab and enter your OpenAI API Key. This enables the app to "read" filenames and infer context for better sorting.
5.  **Start**: Click **Start Organization** to begin.

## Configuration

### Taxonomy Rules
You can customize how files are sorted by navigating to the **Settings** tab. The rules are defined in JSON format:
*   **EXTENSION_GROUPS**: Define which file extensions belong to high-level groups (Documents, Video, etc.).
*   **CATEGORY_HIERARCHY**: Define keywords for specific categories (e.g., "invoice", "receipt" -> Finance).

### Updates
The application includes a lightweight update checker. Go to the **About** tab and click "Check for Updates" to see if a new version is available on GitHub.

## Project Structure

*   `gui.py`: Main entry point for the graphical interface.
*   `main.py`: Core logic orchestration.
*   `taxonomy.py`: Default classification rules and configuration persistence.
*   `ai_service.py`: Handles communication with OpenAI.
*   `ai_optimizer.py`: Logic for space auditing and structure inference.
*   `build.py`: Script to compile the application.
=======
# file-organiser
this app tracks your files and weekly organizes them into folders it is my first project with room for improvement especially adding on AI.
>>>>>>> 6e8bc6d9104d541c807c758c9aacebc87babc3e3
