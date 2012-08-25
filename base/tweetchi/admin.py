from ..core.ext import admin, ModelView
from .models import Status


class StatusView(ModelView):
    column_filters = 'username', 'email'

admin.add_model(Status, ModelView)
