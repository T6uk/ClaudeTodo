# app/routes/utils.py
"""
Enhanced utility routes for various tools and utilities
"""
import os
from flask import Blueprint, render_template, request, flash, current_app, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
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


@utils_bp.route("/flip-image", methods=["POST"])
@login_required
def flip_image():
    """API endpoint for flipping an image horizontally or vertically"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Get flip direction
            flip_direction = request.form.get('flip_direction', '')

            # Apply the flip
            if flip_direction == 'horizontal':
                img = ImageOps.mirror(img)
            elif flip_direction == 'vertical':
                img = ImageOps.flip(img)
            else:
                return jsonify({"error": "Invalid flip direction"}), 400

            # Save the flipped image to a buffer
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
            import traceback
            traceback.print_exc()  # Print the error to the server console
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400


# Add the watermark-image endpoint
@utils_bp.route("/watermark-image", methods=["POST"])
@login_required
def watermark_image():
    """API endpoint for adding a text watermark to an image"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Create an RGBA copy to work with transparency
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Get watermark parameters
            text = request.form.get('text', 'Watermark')
            size = int(request.form.get('size', 24))
            opacity = float(request.form.get('opacity', 0.5))
            position = request.form.get('position', 'bottom-right')
            color = request.form.get('color', '#ffffff')

            # Create a transparent overlay
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))

            # Prepare to draw
            draw = ImageDraw.Draw(overlay)

            # Load a font (fallback to default if not available)
            try:
                # Try to use a nice font if installed on system
                font = ImageFont.truetype("Arial", size)
            except IOError:
                # Fallback to default
                font = ImageFont.load_default()

            # Calculate text size
            try:
                # For newer PIL versions (>= 9.2.0)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except AttributeError:
                # For older PIL versions
                text_width, text_height = draw.textsize(text, font=font)

            # Determine position
            padding = 15
            if position == 'top-left':
                position = (padding, padding)
            elif position == 'top-right':
                position = (img.width - text_width - padding, padding)
            elif position == 'bottom-left':
                position = (padding, img.height - text_height - padding)
            elif position == 'center':
                position = ((img.width - text_width) // 2, (img.height - text_height) // 2)
            else:  # bottom-right or default
                position = (img.width - text_width - padding, img.height - text_height - padding)

            # Convert hex color to RGB
            r, g, b = tuple(int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

            # Draw the text with transparency
            try:
                # For newer PIL versions
                draw.text(position, text, font=font, fill=(r, g, b, int(255 * opacity)))
            except TypeError:
                # Fallback method for older PIL
                draw.text(position, text, font=font, fill=(r, g, b))

            # Composite the images
            img = Image.alpha_composite(img, overlay)

            # Convert back to RGB for saving in common formats
            img = img.convert('RGB')

            # Save the watermarked image to a buffer
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
            import traceback
            traceback.print_exc()  # Print the error to the server console
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400


# Add the export-image endpoint
@utils_bp.route("/export-image", methods=["POST"])
@login_required
def export_image():
    """API endpoint for exporting an image with a specific format"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)

            # Get export format
            export_format = request.form.get('format', 'original').lower()

            # Determine output format and filename
            if export_format == 'original':
                output_format = file.filename.rsplit('.', 1)[1].upper()
                if output_format == 'JPG':
                    output_format = 'JPEG'
                filename = f"edited_image.{output_format.lower()}"
            else:
                output_format = export_format.upper()
                if output_format == 'JPG':
                    output_format = 'JPEG'
                filename = f"edited_image.{export_format}"

            # Prepare the image for the specific format
            img = prepare_image_for_saving(img, output_format)

            # Save the image to a buffer
            buffer = io.BytesIO()

            # Set quality for JPEG
            if output_format == 'JPEG':
                img.save(buffer, format=output_format, quality=95)
            elif output_format == 'WEBP':
                img.save(buffer, format=output_format, quality=90)
            else:
                img.save(buffer, format=output_format)

            buffer.seek(0)

            # Convert to base64 for sending back to the client
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            mime_type = f"image/{export_format.lower()}"
            if export_format == 'JPEG':
                mime_type = "image/jpeg"
            img_src = f"data:{mime_type};base64,{img_base64}"

            return jsonify({
                "success": True,
                "image": img_src,
                "filename": filename
            })
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the error to the server console
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400
