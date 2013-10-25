from django.contrib import admin

from game_data.models import *
from game_data.rank_logic import *

class PlayerAdmin(admin.ModelAdmin):
	fieldsets = [
        (None,  {'fields': [('player_name', 'player_name_underscored')]}),
		('Stats', {'fields': [('overall_rank', 'avg_last_hits', 'avg_gpm')]}),
    ]
	list_display = ('player_name', 'player_name_underscored', 'overall_rank', 'avg_last_hits', 'avg_gpm')
	search_fields = ['player_name']

class HeroAdmin(admin.ModelAdmin):
	fieldsets = [
        (None,               {'fields': [('hero_name_underscored', 'hero_name')]}),
    ]
	list_display = ('hero_name_underscored', 'hero_name')
	search_fields = ['hero_name']
	
class GamesAdmin(admin.ModelAdmin):
	fieldsets = [
        ('Player',               {'fields': ['player']}),
		('Game', {'fields': [('hero', 'last_hits', 'gpm')]}),
		('Rank',               {'fields': [('rank_number')]}),
    ]
	list_display = ('player', 'hero', 'last_hits', 'gpm', 'pub_date', 'rank_number')
	actions = ['delete_model']
	
	#Django's stupid solution
	def get_actions(self, request):
		actions = super(GamesAdmin, self).get_actions(request)
		del actions['delete_selected']
		return actions
	
	def delete_model(self, request, queryset):
		for obj in queryset:
			delete_update_hero_rank(obj)
		queryset.delete()
	delete_model.short_description = 'Delete selected'
		
	#search_fields = ['player']
	#date_hierarchy = ['pub_date']

admin.site.register(Player, PlayerAdmin)
admin.site.register(Hero, HeroAdmin)
admin.site.register(Games, GamesAdmin)