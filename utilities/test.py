import os
import google.auth
import vertexai
from vertexai.generative_models import GenerativeModel


def test_google_auth():
    print("--- 1. Checking Environment Variables ---")
    adc_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {adc_path or 'Not set (using default gcloud login)'}")

    print("\n--- 2. Fetching Google Credentials ---")
    try:
        credentials, project_id = google.auth.default()
        print(f"Project ID: {project_id}")
        print(f"Credential Type: {type(credentials).__name__}")
    except Exception as e:
        print(f"❌ Failed to retrieve credentials: {e}")
        return

    print("\n--- 3. Testing Vertex AI API Call ---")
    try:
        # Initialize Vertex AI
        vertexai.init(project=project_id, credentials=credentials)

        # Test basic call
        model = GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Hello, reply with 'Auth successful!'")

        print("✅ SUCCESS! Vertex AI response received:")
        print(f"Response: {response.text}")

    except Exception as e:
        print("❌ FAILED! Error details:")
        print(e)


if __name__ == "__main__":
    test_google_auth()