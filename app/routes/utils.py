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
import numpy as np
import cv2

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
    """Enhanced API endpoint for applying filters to an image"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)
            original_mode = img.mode

            # Get filter type
            filter_type = request.form.get('filter_type', '')

            # Apply the filter
            if filter_type == 'grayscale':
                img = ImageOps.grayscale(img)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
            elif filter_type == 'sepia':
                # Create sepia effect with enhanced algorithm
                img = img.convert('RGB')
                w, h = img.size
                pixels = img.load()
                for i in range(w):
                    for j in range(h):
                        r, g, b = pixels[i, j]
                        # Enhanced sepia conversion with better color tones
                        tr = min(255, int(0.393 * r + 0.769 * g + 0.189 * b))
                        tg = min(255, int(0.349 * r + 0.686 * g + 0.168 * b))
                        tb = min(255, int(0.272 * r + 0.534 * g + 0.131 * b))
                        pixels[i, j] = (tr, tg, tb)
            elif filter_type == 'blur':
                # Use a more pleasing Gaussian blur
                img = img.filter(ImageFilter.GaussianBlur(radius=2))
            elif filter_type == 'contour':
                # Create a more defined contour with a subsequent brightness adjustment
                img = img.filter(ImageFilter.CONTOUR)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.2)
            elif filter_type == 'emboss':
                # Enhanced emboss effect with contrast adjustment
                img = img.filter(ImageFilter.EMBOSS)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
            elif filter_type == 'sharpen':
                # Enhanced sharpen with custom kernel
                sharpen_kernel = (
                    -1, -1, -1,
                    -1, 9, -1,
                    -1, -1, -1
                )
                img = img.filter(ImageFilter.Kernel((3, 3), sharpen_kernel, scale=1, offset=0))
            elif filter_type == 'smooth':
                img = img.filter(ImageFilter.SMOOTH_MORE)
            elif filter_type == 'edge_enhance':
                # Improved edge enhancement
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
            elif filter_type == 'invert':
                img = ImageOps.invert(img.convert('RGB'))

            # Save the filtered image to a buffer
            buffer = io.BytesIO()
            img_format = file.filename.rsplit('.', 1)[1].upper()
            if img_format == 'JPG':
                img_format = 'JPEG'

            # Handle proper image formatting for saving
            img = prepare_image_for_saving(img, img_format)

            # Save with optimized settings
            if img_format == 'JPEG':
                img.save(buffer, format=img_format, quality=95, optimize=True)
            elif img_format == 'PNG':
                img.save(buffer, format=img_format, optimize=True)
            else:
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
            error_details = traceback.format_exc()
            current_app.logger.error(f"Error in apply_filter: {error_details}")
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
    """Enhanced API endpoint for applying image adjustments with better error handling and performance"""
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        # Read the image with proper error handling
        try:
            img = Image.open(file)
        except Exception as e:
            return jsonify({"error": f"Failed to open image: {str(e)}"}), 400

        # Ensure image is in RGB mode for adjustments
        original_mode = img.mode
        if original_mode != 'RGB' and original_mode != 'RGBA':
            img = img.convert('RGB')

        # Get adjustment parameters with proper validation
        try:
            brightness = max(0, min(2, float(request.form.get('brightness', 1.0))))
            contrast = max(0, min(2, float(request.form.get('contrast', 1.0))))
            saturation = max(0, min(2, float(request.form.get('saturation', 1.0))))
            sharpness = max(0, min(2, float(request.form.get('sharpness', 1.0))))
        except ValueError:
            return jsonify({"error": "Invalid adjustment values"}), 400

        # Log adjustment values for debugging
        current_app.logger.debug(f"Adjusting image with: brightness={brightness}, contrast={contrast}, "
                                f"saturation={saturation}, sharpness={sharpness}")

        # Apply adjustments in an optimal order
        enhancers = [
            (ImageEnhance.Brightness(img), brightness),
            (ImageEnhance.Contrast(img), contrast),
            (ImageEnhance.Color(img), saturation),
            (ImageEnhance.Sharpness(img), sharpness)
        ]

        # Apply each enhancement
        for enhancer, value in enhancers:
            if abs(value - 1.0) > 0.01:  # Only apply if there's a significant change
                img = enhancer.enhance(value)

        # Save the adjusted image to a buffer
        buffer = io.BytesIO()
        img_format = file.filename.rsplit('.', 1)[1].upper()
        if img_format == 'JPG':
            img_format = 'JPEG'

        # Handle output image mode based on format
        img = prepare_image_for_saving(img, img_format)

        # Save with optimized quality settings
        if img_format == 'JPEG':
            img.save(buffer, format=img_format, quality=95, optimize=True)
        elif img_format == 'PNG':
            img.save(buffer, format=img_format, optimize=True)
        else:
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
        error_details = traceback.format_exc()
        current_app.logger.error(f"Error in adjust_image: {error_details}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


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


@utils_bp.route("/inpaint-image", methods=["POST"])
@login_required
def inpaint_image():
    """Advanced API endpoint for removing objects with seamless inpainting"""
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if 'mask' not in request.form:
        return jsonify({"error": "No mask provided"}), 400

    if file and allowed_file(file.filename):
        try:
            # Read the image
            img = Image.open(file)
            img_format = file.filename.rsplit('.', 1)[1].upper()
            if img_format == 'JPG':
                img_format = 'JPEG'

            # Convert PIL Image to OpenCV format
            img_array = np.array(img)
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:  # Has alpha channel
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGRA)
                has_alpha = True
            elif len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                has_alpha = False
            else:
                return jsonify({"error": "Unsupported image format"}), 400

            # Get mask data
            mask_data = request.form.get('mask')
            if ',' in mask_data:
                mask_data = mask_data.split(',')[1]

            mask_bytes = base64.b64decode(mask_data)
            mask_array = np.frombuffer(mask_bytes, np.uint8)
            mask = cv2.imdecode(mask_array, cv2.IMREAD_UNCHANGED)

            # Convert mask to grayscale if needed
            if len(mask.shape) > 2:
                if mask.shape[2] == 4:  # If RGBA
                    # Use alpha channel or convert to grayscale
                    mask = cv2.cvtColor(mask, cv2.COLOR_BGRA2GRAY)
                else:  # If RGB
                    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

            # Ensure mask is binary (255 for area to inpaint, 0 for area to keep)
            _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

            # Resize mask to match image dimensions
            mask = cv2.resize(mask, (img_array.shape[1], img_array.shape[0]), interpolation=cv2.INTER_NEAREST)

            # Get inpainting parameters
            inpaint_method = int(request.form.get('method', '1'))  # 0 for INPAINT_NS, 1 for INPAINT_TELEA
            inpaint_radius = int(request.form.get('radius', '10'))

            # Improve mask with morphological operations for better edge handling
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask_dilated = cv2.dilate(mask, kernel, iterations=2)
            mask_edge = cv2.subtract(mask_dilated, mask)

            # Create enhanced inpainting with multi-scale approach
            # Step 1: Perform initial inpainting with standard algorithm
            if inpaint_method == 0:
                result = cv2.inpaint(img_array, mask, inpaint_radius, cv2.INPAINT_NS)
            else:
                result = cv2.inpaint(img_array, mask, inpaint_radius, cv2.INPAINT_TELEA)

            # Step 2: Create a smaller version for large-scale structure inpainting
            scale_factor = 0.5
            small_img = cv2.resize(img_array, None, fx=scale_factor, fy=scale_factor,
                                   interpolation=cv2.INTER_AREA)
            small_mask = cv2.resize(mask, None, fx=scale_factor, fy=scale_factor,
                                    interpolation=cv2.INTER_NEAREST)

            # Apply inpainting to smaller image (captures larger structures)
            if inpaint_method == 0:
                small_result = cv2.inpaint(small_img, small_mask,
                                           int(inpaint_radius * scale_factor * 1.5), cv2.INPAINT_NS)
            else:
                small_result = cv2.inpaint(small_img, small_mask,
                                           int(inpaint_radius * scale_factor * 1.5), cv2.INPAINT_TELEA)

            # Resize back to original size
            large_structure = cv2.resize(small_result, (img_array.shape[1], img_array.shape[0]),
                                         interpolation=cv2.INTER_CUBIC)

            # Step 3: Create a smaller version for texture synthesis
            if inpaint_method == 1:  # Only use texture synthesis with Telea method
                # Create a texture mask from the dilated mask (excluding the edges)
                texture_mask = cv2.subtract(mask_dilated, mask_edge)

                # Gaussian blur to help with texture blending
                texture_result = cv2.inpaint(result, texture_mask, inpaint_radius // 2, cv2.INPAINT_TELEA)

                # Apply bilateral filter to preserve edges while smoothing textures
                texture_result = cv2.bilateralFilter(texture_result, 9, 75, 75)

                # Blend together based on mask_edge
                alpha = mask_edge.astype(float) / 255.0
                alpha = cv2.GaussianBlur(alpha, (21, 21), 0)
                alpha = np.expand_dims(alpha, axis=2)
                result = (1 - alpha) * result + alpha * texture_result

            # Step 4: Blend the multi-scale results
            # Use original result for details, large structure for overall consistency
            mask_float = mask.astype(float) / 255.0
            mask_float = cv2.GaussianBlur(mask_float, (31, 31), 0)
            mask_float = np.expand_dims(mask_float, axis=2)

            # Combine results with a weighted blending
            beta = 0.7  # Weight for large structure contribution
            final_result = (1 - mask_float) * img_array + mask_float * ((1 - beta) * result + beta * large_structure)
            final_result = final_result.astype(np.uint8)

            # Step 5: Apply seamless cloning to smooth boundaries
            # Create a mask slightly smaller than the original for seamless cloning
            kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            mask_small = cv2.erode(mask, kernel_small, iterations=2)

            # Find center of the mask for seamless cloning
            if np.sum(mask_small) > 0:  # Only if mask is not empty
                moments = cv2.moments(mask_small)
                if moments["m00"] != 0:
                    center_x = int(moments["m10"] / moments["m00"])
                    center_y = int(moments["m01"] / moments["m00"])
                    center = (center_x, center_y)

                    # Apply seamless cloning for smoother transitions
                    try:
                        normal_clone = cv2.seamlessClone(
                            final_result, img_array, mask_small, center, cv2.NORMAL_CLONE
                        )
                        # Blend seamless clone with final result for a more natural look
                        mask_edge_float = mask_edge.astype(float) / 255.0
                        mask_edge_float = cv2.GaussianBlur(mask_edge_float, (15, 15), 0)
                        mask_edge_float = np.expand_dims(mask_edge_float, axis=2)
                        final_result = (1 - mask_edge_float) * final_result + mask_edge_float * normal_clone
                        final_result = final_result.astype(np.uint8)
                    except:
                        # If seamless cloning fails, use the result without it
                        pass

            # Final noise reduction and detail preservation
            final_result = cv2.fastNlMeansDenoisingColored(final_result, None, 3, 3, 7, 21)

            # Convert back to PIL image
            if has_alpha:
                # Preserve original alpha channel
                alpha_channel = cv2.split(cv2.cvtColor(img_array, cv2.COLOR_BGRA2RGBA))[3]
                result_rgb = cv2.cvtColor(final_result, cv2.COLOR_BGR2RGB)
                result_rgba = cv2.merge([result_rgb[:, :, 0], result_rgb[:, :, 1], result_rgb[:, :, 2], alpha_channel])
                result_img = Image.fromarray(result_rgba)
            else:
                result_rgb = cv2.cvtColor(final_result, cv2.COLOR_BGR2RGB)
                result_img = Image.fromarray(result_rgb)

            # Save the inpainted image to a buffer
            buffer = io.BytesIO()
            result_img = prepare_image_for_saving(result_img, img_format)
            result_img.save(buffer, format=img_format)
            buffer.seek(0)

            # Convert to base64 for sending back to the client
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            img_src = f"data:image/{img_format.lower()};base64,{img_base64}"

            return jsonify({
                "success": True,
                "image": img_src,
                "width": result_img.width,
                "height": result_img.height
            })
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            current_app.logger.error(f"Error in inpaint_image: {error_details}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400
