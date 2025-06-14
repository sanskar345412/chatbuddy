import google.generativeai as genai

# Replace with your actual API key
genai.configure(api_key="AIzaSyB5x9bY6KAqZUCv70mMVRgGbhN5fHkQm3Q")

models = genai.list_models()
for model in models:
    print(model.name, "→", model.supported_generation_methods)
