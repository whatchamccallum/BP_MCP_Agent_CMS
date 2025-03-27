"""
Report API routes.
"""

from flask import Blueprint, jsonify, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import tempfile

from api.models import db
from api.models.test_run import TestRun
from api.models.report import Report
from api.controllers.bp_agent import BPAgentController

report_blueprint = Blueprint('report', __name__)


@report_blueprint.route('', methods=['GET'])
@jwt_required()
def get_reports():
    """Get all reports."""
    reports = Report.query.all()
    return jsonify([report.to_dict() for report in reports])


@report_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_report(id):
    """Get report by ID."""
    report = Report.query.get_or_404(id)
    return jsonify(report.to_dict())


@report_blueprint.route('', methods=['POST'])
@jwt_required()
def create_report():
    """Generate a new report."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['test_run_id', 'report_type', 'file_format']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Get the test run
    test_run = TestRun.query.get_or_404(data['test_run_id'])
    
    # Get current user
    user = get_jwt_identity()
    
    # Create BP Agent controller
    bp_agent = BPAgentController(current_app)
    
    try:
        # Generate the report
        report_path, report_filename = bp_agent.generate_report(
            test_run=test_run,
            report_type=data['report_type'],
            file_format=data['file_format']
        )
        
        # Create the report record
        report = Report(
            test_run_id=test_run.id,
            name=data.get('name', f"{test_run.test_configuration.name} - {data['report_type']} Report"),
            description=data.get('description'),
            report_type=data['report_type'],
            file_format=data['file_format'],
            file_path=report_path,
            created_by=user
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@report_blueprint.route('/<int:id>/download', methods=['GET'])
@jwt_required()
def download_report(id):
    """Download a report."""
    report = Report.query.get_or_404(id)
    
    try:
        # Get the file from storage
        storage = current_app.storage
        file_data, content_type = storage.get_file(report.file_path)
        
        # Create a temporary file for download
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_data.read())
        temp_file.close()
        
        # Return the file for download
        return send_file(
            temp_file.name,
            mimetype=content_type,
            as_attachment=True,
            download_name=os.path.basename(report.file_path)
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        if 'temp_file' in locals():
            os.unlink(temp_file.name)


@report_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_report(id):
    """Delete a report."""
    report = Report.query.get_or_404(id)
    
    try:
        # Delete the file from storage
        storage = current_app.storage
        storage.delete_file(report.file_path)
        
        # Delete the report record
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
