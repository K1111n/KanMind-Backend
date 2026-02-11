from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = 'auth_app'

    def ready(self):
        from django.contrib.auth import apps as auth_apps
        auth_apps.AuthConfig.verbose_name = 'Users'
