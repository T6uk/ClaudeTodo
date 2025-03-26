# app/routes/utils.py
"""
Enhanced utility routes for various tools and utilities
"""
import os
from flask import Blueprint, render_template, request, flash, current_app, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import io
import base64
import math

utils_bp = Blueprint("utils", __name__, url_prefix="/utils")

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def prepare_image_for_saving(img, img_format):
    """Convert image to appropriate mode for saving in the given format"""
    if img_format == 'JPEG' or img_format == 'JPG':
        # JPEG doesn't support alpha channel, convert to RGB
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the image on the background using the alpha channel
            background.paste(img, mask=img.split()[3])
            return background
        elif img.mode != 'RGB':
            return img.convert('RGB')
    return img


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
                img = prepare_image_for_saving(img, img_format)
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


@utils_bp.route("/apply-filter", methods=["POST"])
@login_required
def apply_filter():
    """API endpoint for applying filters to an image"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Get filter type
            filter_type = request.form.get('filter_type', '')

            # Apply the filter
            if filter_type == 'grayscale':
                img = ImageOps.grayscale(img)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
            elif filter_type == 'sepia':
                # Create sepia effect
                img = img.convert('RGB')
                w, h = img.size
                pixels = img.load()
                for i in range(w):
                    for j in range(h):
                        r, g, b = pixels[i, j]
                        # Simple sepia conversion
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        if tr > 255: tr = 255
                        if tg > 255: tg = 255
                        if tb > 255: tb = 255
                        pixels[i, j] = (tr, tg, tb)
            elif filter_type == 'blur':
                img = img.filter(ImageFilter.BLUR)
            elif filter_type == 'contour':
                img = img.filter(ImageFilter.CONTOUR)
            elif filter_type == 'detail':
                img = img.filter(ImageFilter.DETAIL)
            elif filter_type == 'emboss':
                img = img.filter(ImageFilter.EMBOSS)
            elif filter_type == 'sharpen':
                img = img.filter(ImageFilter.SHARPEN)
            elif filter_type == 'smooth':
                img = img.filter(ImageFilter.SMOOTH)
            elif filter_type == 'edge_enhance':
                img = img.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_type == 'invert':
                img = ImageOps.invert(img.convert('RGB'))

            # Save the filtered image to a buffer
            buffer = io.BytesIO()
            img_format = file.filename.rsplit('.', 1)[1].upper()
            if img_format == 'JPG':
                img_format = 'JPEG'
            img = prepare_image_for_saving(img, img_format)
            img.save(buffer, format=img_format)
            buffer.seek(0)

            # Convert to base64 for sending back to the client
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            img_src = f"data:image/{img_format.lower()};base64,{img_base64}"

            return jsonify({
                "success": True,
                "image": img_src
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400


@utils_bp.route("/crop-image", methods=["POST"])
@login_required
def crop_image():
    """API endpoint for cropping an image"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Get crop coordinates
            left = request.form.get('left', type=float)
            top = request.form.get('top', type=float)
            right = request.form.get('right', type=float)
            bottom = request.form.get('bottom', type=float)

            # Ensure values are within image bounds
            width, height = img.size
            left = max(0, int(left * width))
            top = max(0, int(top * height))
            right = min(width, int(right * width))
            bottom = min(height, int(bottom * height))

            # Crop the image
            img = img.crop((left, top, right, bottom))

            # Save the cropped image to a buffer
            buffer = io.BytesIO()
            img_format = file.filename.rsplit('.', 1)[1].upper()
            if img_format == 'JPG':
                img_format = 'JPEG'
            img = prepare_image_for_saving(img, img_format)
            img.save(buffer, format=img_format)
            buffer.seek(0)

            # Convert to base64 for sending back to the client
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            img_src = f"data:image/{img_format.lower()};base64,{img_base64}"

            return jsonify({
                "success": True,
                "image": img_src,
                "width": img.width,
                "height": img.height
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400


@utils_bp.route("/rotate-image", methods=["POST"])
@login_required
def rotate_image():
    """API endpoint for rotating an image"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Get rotation angle
            angle = request.form.get('angle', type=float, default=0)

            # Rotate the image
            img = img.rotate(-angle, expand=True, resample=Image.BICUBIC)

            # Save the rotated image to a buffer
            buffer = io.BytesIO()
            img_format = file.filename.rsplit('.', 1)[1].upper()
            if img_format == 'JPG':
                img_format = 'JPEG'
            img = prepare_image_for_saving(img, img_format)
            img.save(buffer, format=img_format)
            buffer.seek(0)

            # Convert to base64 for sending back to the client
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            img_src = f"data:image/{img_format.lower()};base64,{img_base64}"

            return jsonify({
                "success": True,
                "image": img_src,
                "width": img.width,
                "height": img.height
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400


@utils_bp.route("/adjust-image", methods=["POST"])
@login_required
def adjust_image():
    """API endpoint for applying basic adjustments to an image"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Ensure image is in RGB mode for adjustments
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Get adjustment parameters
            brightness = request.form.get('brightness', type=float, default=1.0)
            contrast = request.form.get('contrast', type=float, default=1.0)
            saturation = request.form.get('saturation', type=float, default=1.0)
            sharpness = request.form.get('sharpness', type=float, default=1.0)

            # Apply adjustments
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)

            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)

            if saturation != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(saturation)

            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(sharpness)

            # Save the adjusted image to a buffer
            buffer = io.BytesIO()
            img_format = file.filename.rsplit('.', 1)[1].upper()
            if img_format == 'JPG':
                img_format = 'JPEG'
            img = prepare_image_for_saving(img, img_format)
            img.save(buffer, format=img_format)
            buffer.seek(0)

            # Convert to base64 for sending back to the client
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            img_src = f"data:image/{img_format.lower()};base64,{img_base64}"

            return jsonify({
                "success": True,
                "image": img_src
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400
