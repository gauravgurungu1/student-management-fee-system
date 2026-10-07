from .models import Notice, NoticeRead


def notifications(request):
    if not request.user.is_authenticated:
        return {
            "unread_notice_count": 0,
            "notification_notices": [],
        }

    # Only teachers receive notifications.
    if not hasattr(request.user, "teacher_profile"):
        return {
            "unread_notice_count": 0,
            "notification_notices": [],
        }

    unread_notice_count = (
        Notice.objects
        .exclude(reads__teacher=request.user)
        .count()
    )

    # Show the latest notices in the dropdown.
    notification_notices = (
        Notice.objects
        .select_related("created_by")
        .order_by("-published_at")[:5]
    )

    return {
        "unread_notice_count": unread_notice_count,
        "notification_notices": notification_notices,
    }