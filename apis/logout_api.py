from flask import Blueprint, make_response, redirect

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout', methods=['GET'])
def logout():
    # Create response to delete the Authorization cookie
    response = make_response(redirect('/login'))
    response.delete_cookie('Authorization')
    return response