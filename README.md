# CSV Chat App

This is a Streamlit application that allows you to upload a CSV file and chat with your data using the Gemini 2.0 Flash model.

## Files

- `app.py`: The main application file that orchestrates the different components.
- `engine.py`: Handles the interaction with the Gemini API and model.
- `utils.py`: Contains utility functions, such as processing the model's response.
- `layout.py`: Defines the Streamlit UI elements and layout.
- `config.py`: Stores configuration variables and handles API key retrieval.
- `requirements.txt`: Lists the necessary Python packages.
- `readme.md`: This file.

## Setup

1.  **Clone the repository** (or create these files manually).
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
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

## Running the Application

1.  Open your terminal in the directory where the files are saved.
2.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
3.  Your web browser will open with the application.

## Usage

1.  Upload your CSV file using the file uploader.
2.  Once the file is loaded, a preview will be shown.
3.  Use the chat input box at the bottom to ask questions about your data.
4.  The AI will respond with text, tables, or basic charts based on the data.

## Extending

- You can modify `layout.py` to change the application's appearance.
- Enhance `utils.py` to handle more complex response formats or generate different types of charts (e.g., using Altair or Plotly).
- Refine the instructions in `app.py` (or move them to a separate file) to guide the AI's responses more effectively.
