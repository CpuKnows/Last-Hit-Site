from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .forms import DotaUserCreationForm
from .models import Player, Hero, Game, DotaUser
from .rank_logic import delete_update_hero_rank


class PlayerAdmin(admin.ModelAdmin):
	fieldsets = (
		(None,  {'fields': [('player_acct')]}),
		('Stats', {'fields': [('overall_rank', 'avg_last_hits', 'avg_gpm')]}),)
	list_display = ('player_acct', 'overall_rank', 'avg_last_hits', 'avg_gpm')
	search_fields = ['player_acct']


class HeroAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {'fields': [('hero_name_underscored', 'hero_name')]}),)
	list_display = ('hero_name_underscored', 'hero_name')
	search_fields = ['hero_name']


class GameAdmin(admin.ModelAdmin):
	fieldsets = (
		('Player',               {'fields': ['player']}),
		('Game', {'fields': [('hero', 'last_hits', 'gpm')]}),
		('Rank',               {'fields': ['rank_number']}),)
	list_display = ('player', 'hero', 'last_hits', 'gpm', 'pub_date', 'rank_number')
	actions = ['delete_model']
	
	#Django's stupid solution
	def get_actions(self, request):
		actions = super(GameAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions
	
	def delete_model(self, request, queryset):
		for obj in queryset:
			delete_update_hero_rank(obj)
		queryset.delete()
	delete_model.short_description = 'Delete selected'


class DotaChangeForm(forms.ModelForm):
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = DotaUser

	def clean_password(self):
		return self.initial["password"]


class DotaUserAdmin(UserAdmin):
	add_form = DotaUserCreationForm
	form = DotaChangeForm

	list_display = ("gamer_tag", "email", "is_staff", "gamer_tag")
	list_filter = ("is_staff", "is_superuser", "is_active", "groups")
	search_fields = ("email", "gamer_tag")
	ordering = ("gamer_tag",)
	filter_horizontal = ("groups", "user_permissions")
	fieldsets = (
		(None, {"fields": ("gamer_tag", "email", "password")}),
		("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
	)

	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("gamer_tag", "email", "password1", "password2")}),
	)


admin.site.register(Player, PlayerAdmin)
admin.site.register(Hero, HeroAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(DotaUser, DotaUserAdmin)