from django import forms
from django.forms import ModelForm, ValidationError

from .models import Player, Hero, Game, DotaUser


class PlayerForm(ModelForm):
	class Meta:
		model = Player


class HeroForm(ModelForm):
	class Meta:
		model = Hero


class GameForm(ModelForm):
	class Meta:
		model = Game
		fields = ['hero', 'last_hits', 'gpm']


class DotaUserCreationForm(ModelForm):
	password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
	password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

	class Meta:
		model = DotaUser
		fields = ("email", "gamer_tag")

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1")
		password2 = self.cleaned_data.get("password2")

		if password1 and password2 and password1 != password2:
			msg = "Passwords don't match"
			raise ValidationError(msg)
		return password2

	def save(self, commit=True):
		user = super(DotaUserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
			player = Player.objects.create_player(user)
			player.save()
		return user