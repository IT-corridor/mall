from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as vp
from rest_framework import serializers


class UserPasswordSerializer(serializers.ModelSerializer):
    """ Serializer for resetting user`s password """
    confirm_password = serializers.CharField(allow_blank=False,
                                             write_only=True)
    new_password = serializers.CharField(allow_blank=False, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password':
                                                   _('Passwords do not match')})
        return attrs

    def validate_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError(_('Wrong password'))
        #vp(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    class Meta:
        model = get_user_model()
        fields = ('password', 'confirm_password', 'new_password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('username',)


class UserSetPasswordSerializer(serializers.ModelSerializer):
    """ Serializer for resetting user`s password """
    confirm_password = serializers.CharField(allow_blank=False,
                                             write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({'confirm_password':
                                                   _('Passwords do not match')})
        return attrs

    def validate_password(self, value):
        vp(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    class Meta:
        model = get_user_model()
        fields = ('password', 'confirm_password')
        write_only_fields = ('password',)