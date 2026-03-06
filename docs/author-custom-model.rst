==========================
Custom Author Model (App)
==========================

A standalone Django app that provides **AuthorProfile** management for blog posts
powered by `djangocms-stories <https://github.com/django-cms/djangocms-stories>`_.
Instead of selecting raw Django users as post authors, editors pick from dedicated
author profiles with photos, bios, and social links.

Features
========

- **AuthorProfile** model with name, slug, photo, translatable role & bio (via django-parler)
- **SocialLink** model for social media, email, and phone links (managed as admin inlines)
- **Shadow user** -- each profile auto-creates an inactive Django ``User`` so
  djangocms-stories' foreign key to ``AUTH_USER_MODEL`` keeps working
- **PostAdmin override** -- replaces the default "Author (User)" dropdown with an
  "Author (AuthorProfile)" dropdown
- **Author card template** -- displays author info in the blog post detail sidebar

Requirements
============

- Django 5.x
- django-parler
- django-filer (for ``FilerImageField``)
- easy-thumbnails (for template image rendering)
- djangocms-stories

Setup
=====

1. Add ``"authors"`` to ``INSTALLED_APPS`` in your settings -- **after**
   ``djangocms_stories``:

   .. code-block:: python

      INSTALLED_APPS = [
          # ...
          "djangocms_stories",
          "authors",
          # ...
      ]

2. Run migrations:

   .. code-block:: bash

      python manage.py migrate authors

Models
======

AuthorProfile
-------------

``user`` — ``OneToOneField(User)``
   Auto-created shadow user (not editable).

``name`` — ``CharField(200)``
   Display name (language-independent).

``slug`` — ``SlugField``
   URL slug, unique (language-independent).

``photo`` — ``FilerImageField``
   Profile photo (optional).

``role`` — ``CharField(200)`` — **translatable**
   Job title or role.

``bio`` — ``TextField`` — **translatable**
   Biography.

**Shadow user creation:** On first save the model automatically creates an inactive
Django ``User`` with ``username=author-{slug}`` and ``is_active=False``. On subsequent
saves it syncs ``User.first_name`` with the profile name. This shadow user is what
djangocms-stories stores as ``Post.author``.

SocialLink
----------

``author`` — ``ForeignKey(AuthorProfile)``
   Parent profile.

``icon`` — ``CharField(100)``
   CSS icon class, e.g. ``bi bi-github`` or ``fa-brands fa-discord``.

``label`` — ``CharField(100)``
   Accessible label, e.g. "GitHub".

``url`` — ``CharField(500)``
   Link target -- supports URLs, ``mailto:`` and ``tel:`` schemes.

``sort_order`` — ``PositiveSmallIntegerField``
   Display order.

Admin
=====

AuthorProfile admin
-------------------

- Extends ``TranslatableAdmin`` from django-parler, providing **language tabs** for
  the translatable fields (``role``, ``bio``)
- ``SocialLinkInline`` (tabular) lets you add/remove social links directly on the
  profile page
- The ``slug`` field is auto-populated from ``name``

Post admin override
-------------------

The app automatically unregisters the default ``PostAdmin`` from djangocms-stories and
re-registers a ``CustomPostAdmin`` that:

1. Replaces the ``author`` (User) field with an ``author_profile`` (AuthorProfile)
   dropdown
2. On save, maps the selected profile back to its shadow user
   (``obj.author = profile.user``)
3. On load, pre-selects the profile matching the current post author

Templates
=========

Author card (post detail sidebar)
---------------------------------

**Path:** ``templates/blog/includes/author_card.html``

Included in ``templates/blog/post_detail.html`` inside the ``<aside>`` column.
Displays the author's photo, name, role, bio, and social link buttons. Styled to
match the ``related-people-card`` component.

**Template context:** expects ``post_content`` (the story/post object) in context.
Accesses the author profile via ``post_content.author.author_profile``.

Blog list card
--------------

**Path:** ``templates/blog/includes/card_author.html``

Shows a compact author line (photo + name) on blog list cards.

Usage
=====

1. Go to the Django admin > **Author Profiles** > **Add**
2. Fill in name, slug, photo, role, bio
3. Add social links (icon class + label + URL)
4. Switch language tabs to translate role and bio
5. Save -- a shadow user is created automatically
6. When creating/editing a **Post**, select the author from the "Author" dropdown
   (now showing author profiles instead of users)
7. The author card appears automatically on the post detail page
