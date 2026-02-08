import uuid
from django.db import connection
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from .throttling import LoggingScopedRateThrottle


def _get_user_data(user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ul.user_id, ul.name, ul.created_at, p.points "
            "FROM user_login ul "
            "JOIN players p ON ul.user_id = p.user_id "
            "WHERE ul.user_id = %s",
            [user_id]
        )
        row = cursor.fetchone()
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
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO user_login (user_id) VALUES (%s)",
            [user_id]
        )
        cursor.execute(
            "INSERT INTO players (user_id, points) VALUES (%s, 0)",
            [user_id]
        )
    return user_id


@api_view(['GET'])
@throttle_classes([LoggingScopedRateThrottle])
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
@throttle_classes([LoggingScopedRateThrottle])
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

    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE players SET points = points + %s WHERE user_id = %s",
            [amount, user_id]
        )
        if cursor.rowcount == 0:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    data = _get_user_data(user_id)
    return Response(data)


get_or_create_user.throttle_scope = 'user_me'
add_points.throttle_scope = 'points'
