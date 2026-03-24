from datetime import datetime


def format_date(dt):
    if not dt:
        return 'N/A'
    return dt.strftime('%d %b %Y')


def format_datetime(dt):
    if not dt:
        return 'N/A'
    return dt.strftime('%d %b %Y, %I:%M %p')


def time_ago(dt):
    if not dt:
        return 'N/A'
    diff = datetime.utcnow() - dt
    days = diff.days
    if days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            return f'{minutes}m ago' if minutes > 0 else 'Just now'
        return f'{hours}h ago'
    if days == 1:
        return 'Yesterday'
    if days < 30:
        return f'{days}d ago'
    return format_date(dt)
