"""
Test Run API routes.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.models import db
from api.models.test_run import TestRun
from api.models.test_result import TestResult
from api.controllers.bp_agent import BPAgentController

test_run_blueprint = Blueprint('test_run', __name__)


@test_run_blueprint.route('', methods=['GET'])
@jwt_required()
def get_test_runs():
    """Get all test runs."""
    test_runs = TestRun.query.all()
    return jsonify([run.to_dict() for run in test_runs])


@test_run_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_test_run(id):
    """Get test run by ID."""
    test_run = TestRun.query.get_or_404(id)
    return jsonify(test_run.to_dict())


@test_run_blueprint.route('/<int:id>/status', methods=['GET'])
@jwt_required()
def get_test_run_status(id):
    """Get test run status."""
    test_run = TestRun.query.get_or_404(id)
    
    # If the test run is already completed or failed, return the current status
    if test_run.status in ['completed', 'failed']:
        return jsonify({'status': test_run.status})
    
    # Otherwise, check the current status from the BP Agent
    bp_agent = BPAgentController(current_app)
    try:
        status = bp_agent.get_test_status(test_run)
        
        # Update the test run status if it has changed
        if status != test_run.status:
            test_run.status = status
            db.session.commit()
        
        return jsonify({'status': status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_run_blueprint.route('/<int:id>/stop', methods=['POST'])
@jwt_required()
def stop_test_run(id):
    """Stop a test run."""
    test_run = TestRun.query.get_or_404(id)
    
    # Only stop tests that are running
    if test_run.status != 'running':
        return jsonify({'error': 'Test is not running'}), 400
    
    bp_agent = BPAgentController(current_app)
    try:
        bp_agent.stop_test(test_run)
        
        # Update the test run status
        test_run.status = 'stopped'
        db.session.commit()
        
        return jsonify({'message': 'Test stopped successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@test_run_blueprint.route('/<int:id>/result', methods=['GET'])
@jwt_required()
def get_test_run_result(id):
    """Get test run result."""
    test_run = TestRun.query.get_or_404(id)
    
    # Check if the test run has a result
    if test_run.test_result:
        return jsonify(test_run.test_result.to_dict())
    
    # If the test is complete but no result exists, fetch it from the BP Agent
    if test_run.status == 'completed':
        bp_agent = BPAgentController(current_app)
        try:
            result = bp_agent.get_test_results(test_run)
            
            # Create a new test result
            test_result = TestResult(
                test_run_id=test_run.id,
                result_data=result,
                summary=bp_agent.extract_result_summary(result)
            )
            
            db.session.add(test_result)
            db.session.commit()
            
            return jsonify(test_result.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # If the test is not complete, return an error
    return jsonify({'error': 'Test is not completed yet'}), 400


@test_run_blueprint.route('/<int:id>/reports', methods=['GET'])
@jwt_required()
def get_test_run_reports(id):
    """Get reports for a test run."""
    test_run = TestRun.query.get_or_404(id)
    
    # Get all reports for the test run
    reports = test_run.reports
    
    return jsonify([report.to_dict() for report in reports])


@test_run_blueprint.route('/<int:id>/media', methods=['GET'])
@jwt_required()
def get_test_run_media(id):
    """Get media files for a test run."""
    test_run = TestRun.query.get_or_404(id)
    
    # Get all media for the test run
    media_files = test_run.media
    
    return jsonify([media.to_dict() for media in media_files])
