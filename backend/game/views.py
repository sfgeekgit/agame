import uuid
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from . import db


def _get_user_data(user_id):
    # Always use the db module for raw SQL to keep access centralized.
    row = db.fetch_one(
        "SELECT ul.user_id, ul.name, ul.created_at, p.points "
        "FROM user_login ul "
        "JOIN players p ON ul.user_id = p.user_id "
        "WHERE ul.user_id = %s",
        [user_id],
    )
    if row:
        return {
            'user_id': row[0],
            'name': row[1],
            'created_at': row[2].isoformat() if row[2] else None,
            'points': row[3],
        }
    return None


def _create_user():
    user_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO user_login (user_id) VALUES (%s)",
        [user_id],
    )
    db.execute(
        "INSERT INTO players (user_id, points) VALUES (%s, 0)",
        [user_id],
    )
    return user_id


@api_view(['GET'])
@ensure_csrf_cookie
def get_or_create_user(request):
    user_id = request.session.get('user_id')

    if user_id:
        data = _get_user_data(user_id)
        if data:
            return Response(data)

    user_id = _create_user()
    request.session['user_id'] = user_id

    data = _get_user_data(user_id)
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def add_points(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return Response(
            {'error': 'No user session. Call GET /api/user/me/ first.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    amount = request.data.get('amount', 1)
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return Response(
            {'error': 'amount must be an integer'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if amount < 1:
        return Response(
            {'error': 'amount must be positive'},
            status=status.HTTP_400_BAD_REQUEST
        )

    rowcount = db.execute(
        "UPDATE players SET points = points + %s WHERE user_id = %s",
        [amount, user_id],
    )
    if rowcount == 0:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    data = _get_user_data(user_id)
    return Response(data)
