def admin_delete_confirmation_defaults(request):
    """Supply defaults expected by Django's admin deletion templates.

    django CMS renders the admin deletion template from custom plugin views,
    whose context doesn't yet include Django 6.1's new display limit. ``None``
    is Django's default and means that the complete deletion tree is shown.
    """

    return {"delete_confirmation_max_display": None}
