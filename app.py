from flask import Flask, render_template, request, send_file, jsonify
from rembg import remove
from PIL import Image
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer
from reportlab.lib.pagesizes import A4
import os
import math

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    try:
        file = request.files.get("image")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        color = request.form.get("color", "#87CEEB")

        # open image
        input_image = Image.open(file).convert("RGBA")

        # remove background (FREE AI)
        output = remove(input_image)

        # apply background color
        bg = Image.new("RGBA", output.size, color)
        final = Image.alpha_composite(bg, output)

        # resize to passport size (300 DPI)
        passport = final.resize((413, 531))

        # number of copies
        copies = 8

        # save temp images
        img_paths = []
        for i in range(copies):
            path = f"temp_{i}.png"
            passport.save(path)
            img_paths.append(path)

        # create PDF
        pdf_path = "passport_output.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)

        elements = []

        per_page = 4
        index = 0

        for i in range(math.ceil(copies / per_page)):
            for j in range(per_page):
                if index >= copies:
                    break

                elements.append(RLImage(img_paths[index], width=150, height=200))
                elements.append(Spacer(10, 10))
                index += 1

            elements.append(Spacer(10, 20))

        doc.build(elements)

        # cleanup temp files
        for path in img_paths:
            if os.path.exists(path):
                os.remove(path)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Processing failed"}), 500


if __name__ == "__main__":
    app.run(debug=True)
