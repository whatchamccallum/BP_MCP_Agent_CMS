"""
Media API routes.
"""

from flask import Blueprint, jsonify, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import tempfile
import magic

from api.models import db
from api.models.test_run import TestRun
from api.models.media import Media

media_blueprint = Blueprint('media', __name__)


@media_blueprint.route('', methods=['GET'])
@jwt_required()
def get_media_files():
    """Get all media files."""
    media_files = Media.query.all()
    return jsonify([media.to_dict() for media in media_files])


@media_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_media(id):
    """Get media by ID."""
    media = Media.query.get_or_404(id)
    return jsonify(media.to_dict())


@media_blueprint.route('', methods=['POST'])
@jwt_required()
def upload_media():
    """Upload a new media file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get form data
    test_run_id = request.form.get('test_run_id')
    if not test_run_id:
        return jsonify({'error': 'test_run_id is required'}), 400
    
    # Get the test run
    test_run = TestRun.query.get_or_404(test_run_id)
    
    # Get current user
    user = get_jwt_identity()
    
    # Get file info
    filename = file.filename
    name = request.form.get('name', filename)
    description = request.form.get('description', '')
    
    # Detect media type
    content_type = file.content_type
    if not content_type:
        content_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)  # Reset file pointer
    
    media_type = 'other'
    if content_type.startswith('image/'):
        media_type = 'image'
    elif content_type.startswith('video/'):
        media_type = 'video'
    
    # Save the file
    storage = current_app.storage
    file_path = f"media/{test_run_id}/{filename}"
    
    try:
        # Save the file to storage
        stored_path = storage.save_file(file, file_path)
        
        # Create the media record
        media = Media(
            test_run_id=test_run.id,
            name=name,
            description=description,
            media_type=media_type,
            content_type=content_type,
            file_path=stored_path,
            created_by=user
        )
        
        db.session.add(media)
        db.session.commit()
        
        return jsonify(media.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@media_blueprint.route('/<int:id>/download', methods=['GET'])
@jwt_required()
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
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        if 'temp_file' in locals():
            os.unlink(temp_file.name)


@media_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_media(id):
    """Delete a media file."""
    media = Media.query.get_or_404(id)
    
    try:
        # Delete the file from storage
        storage = current_app.storage
        storage.delete_file(media.file_path)
        
        # Delete the media record
        db.session.delete(media)
        db.session.commit()
        
        return jsonify({'message': 'Media deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
