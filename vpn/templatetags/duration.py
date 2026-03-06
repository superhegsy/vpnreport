from django import template

register = template.Library()


@register.filter
def duration_format(seconds):

    if not seconds:
        return "-"

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"

    return f"{minutes}m"
