"""
PhotoVault Main Routes Blueprint
This should only contain routes, not a Flask app
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
import os
import tempfile

# Create the main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@main_bp.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    try:
        # Calculate photo statistics for the current user
        from photovault.models import Photo
        
        total_photos = Photo.query.filter_by(user_id=current_user.id).count()
        # Count photos with edited versions
        edited_photos = Photo.query.filter_by(user_id=current_user.id)\
                              .filter(Photo.edited_filename.isnot(None))\
                              .count()
        # Original photos are those without edited versions
        original_photos = total_photos - edited_photos
        
        # Calculate total storage used (in MB)
        photos = Photo.query.filter_by(user_id=current_user.id).all()
        total_size_bytes = sum(photo.file_size or 0 for photo in photos)
        total_size_mb = round(total_size_bytes / 1024 / 1024, 2) if total_size_bytes > 0 else 0
        
        # Calculate storage usage percentage (assuming 1GB = 1024MB limit for demo)
        storage_limit_mb = 1024  # 1GB limit
        storage_usage_percent = (total_size_mb / storage_limit_mb * 100) if storage_limit_mb > 0 else 0
        
        stats = {
            'total_photos': total_photos,
            'edited_photos': edited_photos,
            'original_photos': original_photos,
            'total_size_mb': total_size_mb,
            'storage_usage_percent': storage_usage_percent
        }
        
        # Get recent photos for dashboard display (limit to 12 most recent)
        from photovault.models import VoiceMemo
        from photovault.extensions import db
        from sqlalchemy import func
        
        # Get photos with voice memo counts
        recent_photos = db.session.query(
            Photo,
            func.count(VoiceMemo.id).label('voice_memo_count')
        ).outerjoin(VoiceMemo).filter(
            Photo.user_id == current_user.id
        ).group_by(Photo.id).order_by(Photo.created_at.desc()).limit(12).all()
        
        # Convert to a format the template expects
        photos_with_memos = []
        for photo, memo_count in recent_photos:
            photo.voice_memo_count = memo_count
            photos_with_memos.append(photo)
        
        return render_template('dashboard.html', stats=stats, photos=photos_with_memos)
    except Exception as e:
        # Simple fallback for errors - just log to console
        print(f"Dashboard error: {str(e)}")
        # Return simple stats in case of error
        stats = {'total_photos': 0, 'edited_photos': 0, 'original_photos': 0, 'total_size_mb': 0, 'storage_usage_percent': 0}
        return render_template('dashboard.html', stats=stats, photos=[])

@main_bp.route('/upload')
@login_required
def upload():
    """Upload page"""
    return render_template('upload.html', user=current_user)

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Initialize with defaults
    stats = {
        'total_photos': 0,
        'edited_photos': 0,
        'total_size': 0,
        'member_since': 'Unknown'
    }
    
    try:
        # Calculate user statistics
        from photovault.models import Photo
        from datetime import datetime
        import os
        
        # Get all photos for current user
        user_photos = Photo.query.filter_by(user_id=current_user.id).all()
        
        # Calculate statistics - update file sizes if they're missing
        total_photos = len(user_photos)
        edited_photos = sum(1 for photo in user_photos if photo.edited_filename and photo.edited_filename.strip())
        
        # Calculate total size, and update database if file_size is missing
        total_size = 0
        for photo in user_photos:
            if photo.file_size and photo.file_size > 0:
                total_size += photo.file_size
            else:
                # Try to get file size from disk and update database
                try:
                    if os.path.exists(photo.file_path):
                        file_size = os.path.getsize(photo.file_path)
                        photo.file_size = file_size
                        total_size += file_size
                        # Don't commit yet - batch update
                except:
                    pass
        
        # Commit any file size updates
        try:
            from photovault.extensions import db
            db.session.commit()
        except:
            pass
        
        # Format member since date
        if current_user.created_at:
            member_since = current_user.created_at.strftime('%B %Y')
        else:
            member_since = 'Unknown'
            
        stats = {
            'total_photos': total_photos,
            'edited_photos': edited_photos, 
            'total_size': total_size,
            'member_since': member_since
        }
        
    except Exception as e:
        print(f"Profile error: {str(e)}")
        # stats already initialized with defaults above
        
    return render_template('profile.html', user=current_user, stats=stats)

@main_bp.route('/gallery')
@login_required
def gallery():
    """Gallery page"""
    try:
        from photovault.models import Photo
        
        # Get all photos for the current user with voice memo counts
        from photovault.models import VoiceMemo
        from photovault.extensions import db
        from sqlalchemy import func
        
        photos_with_counts = db.session.query(
            Photo,
            func.count(VoiceMemo.id).label('voice_memo_count')
        ).outerjoin(VoiceMemo).filter(
            Photo.user_id == current_user.id
        ).group_by(Photo.id).order_by(Photo.created_at.desc()).all()
        
        # Convert to a format the template expects
        photos_with_memos = []
        for photo, memo_count in photos_with_counts:
            photo.voice_memo_count = memo_count
            photos_with_memos.append(photo)
        
        return render_template('gallery/dashboard.html', photos=photos_with_memos, total_photos=len(photos_with_memos))
    except Exception as e:
        print(f"Gallery error: {str(e)}")
        return render_template('gallery/dashboard.html', photos=[], total_photos=0)

@main_bp.route('/photos/<int:photo_id>/edit')
@login_required
def edit_photo(photo_id):
    """Photo editor page"""
    try:
        from photovault.models import Photo
        
        # Get the photo and verify ownership
        photo = Photo.query.get_or_404(photo_id)
        if photo.user_id != current_user.id:
            return redirect(url_for('main.dashboard'))
            
        return render_template('editor.html', photo=photo)
    except Exception as e:
        print(f"Edit photo error: {str(e)}")
        return redirect(url_for('main.dashboard'))

@main_bp.route('/advanced-enhancement')
@login_required 
def advanced_enhancement():
    """Advanced Image Enhancement page with OpenCV-powered processing"""
    try:
        from photovault.models import Photo
        
        # Get user's photos for the enhancement interface
        user_photos = Photo.query.filter_by(user_id=current_user.id)\
                                .order_by(Photo.created_at.desc())\
                                .limit(20).all()
        
        return render_template('advanced_enhancement.html', photos=user_photos)
    except Exception as e:
        print(f"Advanced enhancement page error: {str(e)}")
        return redirect(url_for('main.dashboard'))

@main_bp.route('/api/photos/<int:photo_id>/enhance', methods=['POST'])
@login_required
def enhance_photo_api(photo_id):
    """API endpoint for applying image enhancements"""
    try:
        from photovault.models import Photo, db
        from photovault.utils.image_enhancement import enhancer
        
        # Get the photo and verify ownership
        photo = Photo.query.get_or_404(photo_id)
        if photo.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get enhancement type from request
        data = request.get_json()
        enhancement_type = data.get('enhancement_type')
        
        if not enhancement_type:
            return jsonify({'success': False, 'error': 'Enhancement type required'}), 400
        
        # Get photo file paths using the stored file_path
        original_path = photo.file_path
        
        if not os.path.exists(original_path):
            return jsonify({'success': False, 'error': 'Original photo not found'}), 404
        
        # Create temporary enhanced file with timestamp to avoid conflicts
        import time
        base_name, ext = os.path.splitext(photo.filename)
        timestamp = int(time.time())
        temp_filename = f"{base_name}_temp_enhanced_{enhancement_type}_{timestamp}{ext}"
        upload_folder = os.path.dirname(photo.file_path)
        enhanced_path = os.path.join(upload_folder, temp_filename)
        
        # Prepare enhancement settings based on type
        settings = enhancer.default_settings.copy()
        
        if enhancement_type == 'clahe':
            settings.update({'clahe_enabled': True, 'denoise': False, 'auto_levels': False})
        elif enhancement_type == 'denoise':
            settings.update({'denoise': True, 'clahe_enabled': False, 'auto_levels': False})
        elif enhancement_type == 'auto_levels':
            settings.update({'auto_levels': True, 'clahe_enabled': False, 'denoise': False})
        elif enhancement_type == 'brightness':
            settings.update({'brightness': 1.2, 'clahe_enabled': False, 'denoise': False, 'auto_levels': False})
        elif enhancement_type == 'contrast':
            settings.update({'contrast': 1.3, 'clahe_enabled': False, 'denoise': False, 'auto_levels': False})
        elif enhancement_type == 'color':
            settings.update({'color': 1.1, 'clahe_enabled': False, 'denoise': False, 'auto_levels': False})
        elif enhancement_type == 'auto_enhance':
            # Use optimal settings for old photos
            settings = enhancer.detect_and_enhance_old_photo(original_path)
        else:
            return jsonify({'success': False, 'error': 'Invalid enhancement type'}), 400
        
        # Apply enhancement
        enhanced_file_path, applied_settings = enhancer.auto_enhance_photo(
            original_path, enhanced_path, settings
        )
        
        # Generate URL for the enhanced image using existing secure route
        enhanced_url = f"/uploads/{current_user.id}/{temp_filename}"
        
        return jsonify({
            'success': True,
            'enhanced_url': enhanced_url,
            'enhancement_type': enhancement_type,
            'settings_applied': applied_settings
        })
        
    except Exception as e:
        print(f"Enhancement API error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/photos/<int:photo_id>/save-enhanced', methods=['POST'])
@login_required
def save_enhanced_api(photo_id):
    """API endpoint for saving enhanced photo permanently"""
    try:
        from photovault.models import Photo, db
        
        # Get the photo and verify ownership
        photo = Photo.query.get_or_404(photo_id)
        if photo.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        enhanced_url = data.get('enhanced_url')
        
        if not enhanced_url:
            return jsonify({'success': False, 'error': 'Enhanced URL required'}), 400
        
        # Extract filename from URL
        temp_filename = enhanced_url.split('/')[-1]
        upload_folder = os.path.dirname(photo.file_path)
        temp_path = os.path.join(upload_folder, temp_filename)
        
        if not os.path.exists(temp_path):
            return jsonify({'success': False, 'error': 'Enhanced photo not found'}), 404
        
        # Create permanent enhanced filename
        base_name, ext = os.path.splitext(photo.filename)
        enhanced_filename = f"{base_name}_enhanced{ext}"
        enhanced_path = os.path.join(upload_folder, enhanced_filename)
        
        # Move temp file to permanent location
        os.rename(temp_path, enhanced_path)
        
        # Update database record
        photo.edited_filename = enhanced_filename
        photo.has_edits = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Enhanced photo saved successfully',
            'enhanced_filename': enhanced_filename
        })
        
    except Exception as e:
        print(f"Save enhanced API error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/people')
@login_required
def people():
    """People management page"""
    try:
        from photovault.models import Person
        
        # Get all people for the current user with pagination
        page = request.args.get('page', 1, type=int)
        people = Person.query.filter_by(user_id=current_user.id).order_by(Person.name.asc()).paginate(
            page=page, per_page=12, error_out=False
        )
        
        return render_template('people.html', people=people)
    except Exception as e:
        print(f"People page error: {str(e)}")
        return render_template('people.html', people=None)

@main_bp.route('/people/add', methods=['POST'])
@login_required
def add_person():
    """Add a new person"""
    try:
        from photovault.models import Person, db
        
        name = request.form.get('name', '').strip()
        nickname = request.form.get('nickname', '').strip()
        relationship = request.form.get('relationship', '').strip()
        birth_year = request.form.get('birth_year')
        notes = request.form.get('notes', '').strip()
        
        if not name:
            flash('Name is required.', 'error')
            return redirect(url_for('main.people'))
        
        # Convert birth_year to int if provided
        birth_year_int = None
        if birth_year:
            try:
                birth_year_int = int(birth_year)
            except ValueError:
                flash('Birth year must be a valid number.', 'error')
                return redirect(url_for('main.people'))
        
        # Create new person
        person = Person(
            user_id=current_user.id,
            name=name,
            nickname=nickname if nickname else None,
            relationship=relationship if relationship else None,
            birth_year=birth_year_int,
            notes=notes if notes else None
        )
        
        db.session.add(person)
        db.session.commit()
        
        flash(f'{name} has been added successfully!', 'success')
        return redirect(url_for('main.people'))
        
    except Exception as e:
        print(f"Add person error: {str(e)}")
        flash('Error adding person. Please try again.', 'error')
        return redirect(url_for('main.people'))

@main_bp.route('/people/<int:person_id>/edit', methods=['POST'])
@login_required
def edit_person(person_id):
    """Edit an existing person"""
    try:
        from photovault.models import Person, db
        
        person = Person.query.get_or_404(person_id)
        
        # Verify ownership
        if person.user_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('main.people'))
        
        name = request.form.get('name', '').strip()
        nickname = request.form.get('nickname', '').strip()
        relationship = request.form.get('relationship', '').strip()
        birth_year = request.form.get('birth_year')
        notes = request.form.get('notes', '').strip()
        
        if not name:
            flash('Name is required.', 'error')
            return redirect(url_for('main.people'))
        
        # Convert birth_year to int if provided
        birth_year_int = None
        if birth_year:
            try:
                birth_year_int = int(birth_year)
            except ValueError:
                flash('Birth year must be a valid number.', 'error')
                return redirect(url_for('main.people'))
        
        # Update person
        person.name = name
        person.nickname = nickname if nickname else None
        person.relationship = relationship if relationship else None
        person.birth_year = birth_year_int
        person.notes = notes if notes else None
        
        db.session.commit()
        
        flash(f'{name} has been updated successfully!', 'success')
        return redirect(url_for('main.people'))
        
    except Exception as e:
        print(f"Edit person error: {str(e)}")
        flash('Error updating person. Please try again.', 'error')
        return redirect(url_for('main.people'))

@main_bp.route('/api', methods=['GET', 'HEAD'])
def api_health():
    """API health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'PhotoVault'})

@main_bp.route('/api/person/delete/<int:person_id>', methods=['DELETE'])
@login_required
def delete_person(person_id):
    """Delete a person"""
    try:
        from photovault.models import Person, db
        
        person = Person.query.get_or_404(person_id)
        
        # Verify ownership
        if person.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        name = person.name
        db.session.delete(person)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{name} deleted successfully'})
        
    except Exception as e:
        print(f"Delete person error: {str(e)}")
        return jsonify({'success': False, 'error': 'Error deleting person'}), 500