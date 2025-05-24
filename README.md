# Chatyfile

This is a Streamlit application, that allows you to upload a CSV file and chat with your data using the Gemini 2.0 Flash model, with a custom layout.

## Files

- `app.py`: The main application file that orchestrates the different components and handles the chat logic.
- `engine.py`: Contains the `ChatEngine` class for interacting with the Gemini model and processing questions.
- `utils.py`: Contains utility functions for parsing model responses and aiding visualization.
- `layout.py`: Defines the functions to configure the page, apply custom CSS styles, and display the header and footer.
- `config.py`: Stores configuration variables and handles API key retrieval.
- `requirements.txt`: Lists the necessary Python packages.
- `readme.md`: This file.

## Setup

1.  **Clone the repository** (or create these files manually).
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    **Note:** Ensure all listed libraries are installed.
3.  **Get a Gemini API Key:**
    - Go to [Google AI Studio](https://makersuite.google.com/).
    - Create an API key.
4.  **Configure your API Key:**
    - **Option 1 (Environment Variable):** Set the `GEMINI_API_KEY` environment variable with your API key.
      ```bash
      export GEMINI_API_KEY='YOUR_API_KEY'
      ```
      (Replace `YOUR_API_KEY` with your actual key)
    - **Option 2 (Streamlit Cloud Secrets):** If deploying to Streamlit Cloud, create a `.streamlit` folder and inside it, a `secrets.toml` file. Add your API key like this:
      ```toml
      GEMINI_API_KEY="YOUR_API_KEY"
      ```
      (Replace `YOUR_API_KEY` with your actual key)
5.  **Ensure you have a `logo.jpeg` file** in the same directory as `app.py` if you want the logo to be displayed in the header.

## Running the Application

1.  Open your terminal in the directory where the files are saved.
2.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
3.  Your web browser will open with the application.

## Usage

1.  Upload your CSV file using the file uploader in the sidebar.
2.  Once the file is loaded, a welcome message will appear in the chat.
3.  Use the text input box at the bottom to ask questions about your data.
4.  The AI will respond with text, tables, or basic charts based on the data.

## Extending

- You can modify the CSS in `layout.py` to further adjust the appearance.
- Enhance `utils.py` to handle more complex response formats or generate different types of charts (e.g., using Altair or Plotly instead of basic Streamlit charts).
- Refine the instructions in `engine.py` to guide the AI's responses more effectively.
