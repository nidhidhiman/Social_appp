# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from socialbot.models import UserModel, PostModel, LikeModel, CommentModel

from django.contrib import admin

# Register your models here.
admin.site.register(UserModel)
admin.site.register(PostModel)
admin.site.register(LikeModel)
admin.site.register(CommentModel)
