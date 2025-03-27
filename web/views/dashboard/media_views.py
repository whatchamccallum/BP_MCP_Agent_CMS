"""
Media views.
"""
import os
import tempfile
from flask import render_template, redirect, url_for, request, flash, current_app, send_file, jsonify
from api.models import db
from api.models.media import Media
from api.models.test_run import TestRun
from datetime import datetime

from .utils import get_current_user, normalize_user_id
from . import dashboard_blueprint

@dashboard_blueprint.route('/media')
def media():
    """Media page."""
    # Get media
    media_files = Media.query.order_by(Media.created_at.desc()).all()
    
    # Get test runs for the upload form
    test_runs = TestRun.query.order_by(TestRun.created_at.desc()).all()
    
    return render_template(
        'dashboard/media.html',
        media_files=media_files,
        test_runs=test_runs
    )

@dashboard_blueprint.route('/media/upload', methods=['POST'])
def upload_media():
    """Upload a new media file."""
    try:
        # Get current user
        current_user = normalize_user_id(get_current_user())
        
        if 'media_file' not in request.files:
            flash('No file provided', 'error')
            return redirect(url_for('dashboard.media'))
            
        file = request.files['media_file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('dashboard.media'))
        
        # Get form data
        name = request.form.get('media_name') or file.filename
        description = request.form.get('media_description', '')
        test_run_id = request.form.get('test_run_id')
        
        # Detect media type
        content_type = file.content_type
        if not content_type:
            try:
                import magic
                content_type = magic.from_buffer(file.read(1024), mime=True)
                file.seek(0)  # Reset file pointer
            except ImportError:
                # If python-magic is not available, use simple extension-based detection
                _, ext = os.path.splitext(file.filename)
                if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    content_type = f'image/{ext.lower()[1:]}'
                elif ext.lower() in ['.mp4', '.avi', '.mov']:
                    content_type = f'video/{ext.lower()[1:]}'
                else:
                    content_type = 'application/octet-stream'
        
        media_type = 'other'
        if content_type.startswith('image/'):
            media_type = 'image'
        elif content_type.startswith('video/'):
            media_type = 'video'
        
        # Save the file
        storage = current_app.storage
        file_path = f"media/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        
        # Save the file to storage
        stored_path = storage.save_file(file, file_path)
        
        # Create the media record
        media = Media(
            test_run_id=test_run_id if test_run_id else None,
            name=name,
            description=description,
            media_type=media_type,
            content_type=content_type,
            file_path=stored_path,
            created_by=current_user
        )
        
        db.session.add(media)
        db.session.commit()
        
        flash('Media uploaded successfully', 'success')
        return redirect(url_for('dashboard.media'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error uploading media: {str(e)}', 'error')
        return redirect(url_for('dashboard.media'))

@dashboard_blueprint.route('/media/<int:id>/view')
def view_media(id):
    """View a media file."""
    media = Media.query.get_or_404(id)
    
    try:
        # Get the file from storage
        storage = current_app.storage
        file_data, content_type = storage.get_file(media.file_path)
        
        # Create a temporary file for viewing
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_data.read())
        temp_file.close()
        
        # Return the file for viewing
        return send_file(
            temp_file.name,
            mimetype=content_type,
            as_attachment=False
        )
    except Exception as e:
        flash(f'Error viewing media: {str(e)}', 'error')
        return redirect(url_for('dashboard.media'))
    finally:
        # Clean up the temporary file
        if 'temp_file' in locals():
            os.unlink(temp_file.name)

@dashboard_blueprint.route('/media/<int:id>/download')
def download_media(id):
    """Download a media file."""
    media = Media.query.get_or_404(id)
    
    try:
        # Get the file from storage
        storage = current_app.storage
        file_data, content_type = storage.get_file(media.file_path)
        
        # Create a temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_data.read())
        temp_file.close()
        
        # Return the file for download
        return send_file(
            temp_file.name,
            mimetype=content_type,
            as_attachment=True,
            download_name=os.path.basename(media.file_path)
        )
    except Exception as e:
        flash(f'Error downloading media: {str(e)}', 'error')
        return redirect(url_for('dashboard.media'))
    finally:
        # Clean up the temporary file
        if 'temp_file' in locals():
            os.unlink(temp_file.name)

@dashboard_blueprint.route('/media/<int:id>/delete', methods=['POST'])
def delete_media(id):
    """Delete a media file."""
    try:
        media = Media.query.get_or_404(id)
    
        # Delete the file from storage
        storage = current_app.storage
        storage.delete_file(media.file_path)
        
        # Delete the media record
        db.session.delete(media)
        db.session.commit()
        
        flash('Media deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting media: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.media'))
