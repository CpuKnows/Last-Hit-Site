from django.contrib import admin
from game_data.models import Player
from game_data.models import Hero
from game_data.models import Games

class PlayerAdmin(admin.ModelAdmin):
	fieldsets = [
        (None,  {'fields': [('player_name', 'overall_rank')]}),
    ]
	list_display = ('player_name', 'overall_rank')

class HeroAdmin(admin.ModelAdmin):
	fieldsets = [
        (None,               {'fields': [('hero_name', 'hero_name_underscored')]}),
		('Rank / Player', {'fields': [('rank_number', 'player')]}),
    ]
	list_display = ('hero_name', 'hero_name_underscored', 'rank_number', 'player')
	search_fields = ['hero_name']
	
class GamesAdmin(admin.ModelAdmin):
	fieldsets = [
        ('Player',               {'fields': ['player']}),
		('Game', {'fields': [('hero', 'last_hits', 'gpm')]}),
    ]
	list_display = ('player', 'hero', 'last_hits', 'gpm', 'pub_date')
	#search_fields = ['player']
	#date_hierarchy = ['pub_date']

admin.site.register(Player, PlayerAdmin)
admin.site.register(Hero, HeroAdmin)
admin.site.register(Games, GamesAdmin)