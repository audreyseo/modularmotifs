
import base64
from flask import Flask, Response, jsonify, make_response
from PIL import Image, ImageDraw
from modularmotifs.motiflibrary.examples import motifs
from modularmotifs.core.util import motif_to_image
import io
from markupsafe import escape

app = Flask(__name__)

def generate_image():
    """Generate a simple PIL image and return as bytes."""
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], outline="black", width=5)
    draw.text((60, 80), "Hello!", fill="black")

    # Save image to a byte stream
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return img_io

def serve_pil_image(img: Image.Image) -> io.BytesIO:
    img_io = io.BytesIO()
    img.save(img_io, 'png', quality=100)
    img_io.seek(0)
    # img_str = base64.b64encode(img_io.getvalue()).decode('ascii')
    return img_io #img_str

def add_frontend_access(response: Response):
    # response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:3000')
    # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Origin', "*")


@app.route("/motifs")
def serve_motifs():
    response = make_response(jsonify(data=list(motifs.keys()), motifs={k: v.to_json() for k,v in motifs.items()}), 200)
    add_frontend_access(response)
    return response
    

@app.route("/motif/<motif_name>")
def serve_motif(motif_name: str):
    if motif_name in motifs:
        img = motif_to_image(motifs[motif_name], square_size=30)
        motif_io = serve_pil_image(img)
    
        response = make_response(jsonify(data=base64.b64encode(motif_io.getvalue()).decode('ascii')), 200)
        add_frontend_access(response)
        # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        return response
    else:
        response = make_response(f"no motif called {motif_name} found", 404)
        add_frontend_access(response)
        return response
    # return Response(motif_io.getvalue(), mimetype="image/png")

@app.route("/image")
def serve_image():
    """Flask route to return an image as a byte response."""
    img_io = generate_image()
    return Response(img_io.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True, port=5000)