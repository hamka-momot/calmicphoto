# photovault/routes/montage.py

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from photovault.models import Photo
from photovault.extensions import db
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
import os
import io
import tempfile
from datetime import datetime

montage_bp = Blueprint('montage', __name__)

@montage_bp.route('/montage')
@login_required
def montage():
    """Montage creation page"""
    # Get user's photos for selection
    photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.created_at.desc()).all()
    return render_template('montage.html', photos=photos)

@montage_bp.route('/api/montage/create', methods=['POST'])
@login_required
def create_montage():
    """Create montage PDF from selected photos"""
    try:
        data = request.get_json()
        photo_ids = data.get('photo_ids', [])
        layout = data.get('layout', 'grid')  # grid, collage, etc.
        title = data.get('title', 'Photo Montage')
        
        if not photo_ids:
            return jsonify({'error': 'No photos selected'}), 400
        
        # Get the selected photos
        photos = Photo.query.filter(
            Photo.id.in_(photo_ids),
            Photo.user_id == current_user.id
        ).all()
        
        if not photos:
            return jsonify({'error': 'No valid photos found'}), 400
        
        # Create montage and PDF
        pdf_buffer = create_montage_pdf(photos, layout, title)
        
        # Create temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf_buffer.getvalue())
        temp_file.close()
        
        return jsonify({'success': True, 'download_url': f'/api/montage/download/{os.path.basename(temp_file.name)}'})
        
    except Exception as e:
        current_app.logger.error(f"Error creating montage: {str(e)}")
        return jsonify({'error': 'Failed to create montage'}), 500

@montage_bp.route('/api/montage/download/<filename>')
@login_required
def download_montage(filename):
    """Download the generated montage PDF"""
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(file_path):
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f'photovault_montage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
                mimetype='application/pdf'
            )
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error downloading montage: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

def create_montage_pdf(photos, layout='grid', title='Photo Montage'):
    """Create a PDF montage from selected photos"""
    buffer = io.BytesIO()
    
    # Create PDF with ReportLab
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, title)
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if layout == 'grid':
        # Grid layout - arrange photos in a grid
        create_grid_layout(c, photos, width, height)
    elif layout == 'collage':
        # Collage layout - more artistic arrangement
        create_collage_layout(c, photos, width, height)
    else:
        # Default to grid
        create_grid_layout(c, photos, width, height)
    
    c.save()
    buffer.seek(0)
    return buffer

def create_grid_layout(canvas_obj, photos, page_width, page_height):
    """Create a grid layout for photos"""
    margin = 50
    usable_width = page_width - (2 * margin)
    usable_height = page_height - 120  # Account for title area
    
    # Calculate grid dimensions based on number of photos
    num_photos = len(photos)
    if num_photos == 1:
        cols, rows = 1, 1
    elif num_photos <= 4:
        cols, rows = 2, 2
    elif num_photos <= 6:
        cols, rows = 3, 2
    elif num_photos <= 9:
        cols, rows = 3, 3
    else:
        cols, rows = 4, 3  # Max 12 photos
        num_photos = min(num_photos, 12)
    
    photo_width = usable_width / cols - 10  # 10pt spacing
    photo_height = usable_height / rows - 10
    
    # Keep aspect ratio, use smaller dimension
    final_size = min(photo_width, photo_height)
    
    for i, photo in enumerate(photos[:num_photos]):
        if not os.path.exists(photo.file_path):
            continue
            
        row = i // cols
        col = i % cols
        
        x = margin + col * (final_size + 10)
        y = page_height - 120 - (row + 1) * (final_size + 10)
        
        try:
            # Create a temporary resized image for the PDF
            temp_img = create_temp_image_for_pdf(photo.file_path, int(final_size))
            if temp_img:
                canvas_obj.drawImage(temp_img, x, y, width=final_size, height=final_size)
                # Clean up temp file
                os.unlink(temp_img)
        except Exception as e:
            # Skip problematic images
            current_app.logger.warning(f"Could not process image {photo.file_path}: {str(e)}")
            continue

def create_collage_layout(canvas_obj, photos, page_width, page_height):
    """Create a more artistic collage layout"""
    margin = 50
    usable_width = page_width - (2 * margin)
    usable_height = page_height - 120
    
    # For collage, vary the sizes and positions
    positions = [
        (margin, page_height - 220, 150, 150),  # Top left
        (margin + 180, page_height - 220, 120, 120),  # Top center
        (margin + 320, page_height - 200, 100, 100),  # Top right
        (margin + 20, page_height - 400, 180, 180),  # Middle left
        (margin + 220, page_height - 380, 140, 140),  # Middle right
        (margin + 380, page_height - 420, 110, 110),  # Right
        (margin, page_height - 600, 120, 120),  # Bottom left
        (margin + 140, page_height - 620, 160, 160),  # Bottom center
        (margin + 320, page_height - 580, 130, 130),  # Bottom right
    ]
    
    for i, photo in enumerate(photos[:len(positions)]):
        if not os.path.exists(photo.file_path):
            continue
            
        x, y, w, h = positions[i]
        
        try:
            temp_img = create_temp_image_for_pdf(photo.file_path, int(max(w, h)))
            if temp_img:
                canvas_obj.drawImage(temp_img, x, y, width=w, height=h)
                os.unlink(temp_img)
        except Exception as e:
            current_app.logger.warning(f"Could not process image {photo.file_path}: {str(e)}")
            continue

def create_temp_image_for_pdf(image_path, max_size=400):
    """Create a temporary resized image file for PDF insertion"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize while maintaining aspect ratio
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG', quality=85)
            return temp_file.name
    except Exception as e:
        current_app.logger.error(f"Error processing image {image_path}: {str(e)}")
        return None