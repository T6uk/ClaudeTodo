# app/routes/utils.py
"""
Utility routes for various tools and utilities
"""
import os
from flask import Blueprint, render_template, request, flash, current_app, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64

utils_bp = Blueprint("utils", __name__, url_prefix="/utils")

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@utils_bp.route("/photo-editing")
@login_required
def photo_editing():
    """Photo editing utility page"""
    return render_template("utils/photo_editing.html", title="Photo Editing")


@utils_bp.route("/scale-image", methods=["POST"])
@login_required
def scale_image():
    """API endpoint for scaling an image"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Get scaling parameters
            width = request.form.get('width', type=int)
            height = request.form.get('height', type=int)
            maintain_aspect = request.form.get('maintain_aspect', 'false') == 'true'

            if width and height:
                if maintain_aspect:
                    # Calculate new dimensions while maintaining aspect ratio
                    img_width, img_height = img.size
                    aspect = img_width / img_height

                    if width / height > aspect:
                        # Width is the constraining factor
                        width = int(height * aspect)
                    else:
                        # Height is the constraining factor
                        height = int(width / aspect)

                # Resize the image
                img = img.resize((width, height), Image.LANCZOS)

                # Save the resized image to a buffer
                buffer = io.BytesIO()
                img_format = file.filename.rsplit('.', 1)[1].upper()
                if img_format == 'JPG':
                    img_format = 'JPEG'
                img.save(buffer, format=img_format)
                buffer.seek(0)

                # Convert to base64 for sending back to the client
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                img_src = f"data:image/{img_format.lower()};base64,{img_base64}"

                return jsonify({
                    "success": True,
                    "image": img_src,
                    "width": width,
                    "height": height,
                    "original_width": img.width,
                    "original_height": img.height
                })
            else:
                return jsonify({"error": "Width and height must be provided"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400