from flask import Flask, request, jsonify
from model_utils import generate_answer
from tds_utils import load_tds_content
from PIL import Image
import pytesseract
import base64
from io import BytesIO

app = Flask(__name__)

# Load TDS notes and discourse content at startup
tds_content = load_tds_content()

@app.route("/", methods=["GET"])
def index():
    return """
        <h2>TDS Virtual TA 🤖</h2>
        <input type="text" id="question" placeholder="Ask your question here..." size="60"/><br><br>
        <input type="file" id="image" accept="image/*"/><br><br>
        <button onclick="submitQuestion()">Submit</button>
        <pre id="response" style="white-space: pre-wrap; background: #f5f5f5; padding: 10px;"></pre>
        <script>
        async function submitQuestion() {
            const question = document.getElementById("question").value;
            const imageFile = document.getElementById("image").files[0];
            const responseBox = document.getElementById("response");
            responseBox.textContent = "⏳ Generating answer...";

            let base64Image = null;

            if (imageFile) {
                const reader = new FileReader();
                reader.onloadend = async () => {
                    base64Image = reader.result;
                    await sendRequest(question, base64Image);
                };
                reader.readAsDataURL(imageFile);
            } else {
                await sendRequest(question, null);
            }

            async function sendRequest(questionText, imageData) {
                try {
                    const response = await fetch("/api/", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            question: questionText,
                            image: imageData
                        })
                    });
                    const result = await response.json();
                    if (result.answer) {
                        responseBox.textContent = "✅ " + result.answer;
                    } else if (result.error) {
                        responseBox.textContent = "❌ Error: " + result.error;
                    } else {
                        responseBox.textContent = "❌ Unexpected response.";
                    }
                } catch (error) {
                    responseBox.textContent = "❌ Request failed: " + error;
                }
            }
        }
        </script>
    """

@app.route("/api/", methods=["POST"])
def api():
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        base64_image = data.get("image", None)
        image_text = ""

        # Handle optional image
        if base64_image:
            if base64_image.startswith("data:image"):
                base64_image = base64_image.split(",")[1]
            image_bytes = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_bytes))
            image_text = pytesseract.image_to_string(image).strip()

        # Final question = text + OCR
        combined_question = question
        if image_text:
            combined_question += "\n\nAdditional info from attached image:\n" + image_text

        # Ensure some content exists
        if not combined_question.strip():
            return jsonify({"error": "No valid question or image content provided."}), 400

        # Generate answer
        answer = generate_answer(combined_question, tds_content)

        return jsonify({
            "answer": answer,
            "links": []
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
