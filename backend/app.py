from flask import Flask, render_template, request, send_file, jsonify
from rembg import remove
from PIL import Image, ImageEnhance
import io, base64

app = Flask(__name__)

SUGGESTED_COLORS = {
    "White": (255, 255, 255),
    "Light Gray": (240, 240, 240),
    "Soft Blue": (200, 220, 255),
    "Beige": (245, 235, 220)
}

@app.route("/")
def index():
    return render_template("index.html", colors=SUGGESTED_COLORS)


@app.route("/process", methods=["POST"])
def process_image():
    try:
        file = request.files["image"]
        bg_color = request.form.get("bg_color")

        img = Image.open(file.stream)

        # 1. Remove background
        img_no_bg = remove(img)

        # 2. Enhance sharpness & brightness
        sharpener = ImageEnhance.Sharpness(img_no_bg)
        enhanced = sharpener.enhance(1.8)

        brightener = ImageEnhance.Brightness(enhanced)
        final = brightener.enhance(1.2)

        # 3. Add background color (optional)
        if bg_color:
            bg = Image.new("RGB", final.size, SUGGESTED_COLORS[bg_color])
            bg.paste(final, mask=final.split()[3])
            final = bg

        img_bytes = io.BytesIO()
        final.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # Convert image → Base64 so frontend can show it
        encoded_img = base64.b64encode(img_bytes.getvalue()).decode("utf-8")

        return jsonify({"image": encoded_img})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
