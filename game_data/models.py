from django.db import models
from django.forms import ModelForm
from django.core.urlresolvers import reverse, reverse_lazy

class Player(models.Model):
	player_name = models.CharField(max_length = 20)
	player_name_underscored = models.CharField(max_length = 25)
	overall_rank = models.PositiveIntegerField(blank = True, null = True)
	avg_last_hits = models.DecimalField(max_digits = 6, decimal_places = 2, blank = True)
	avg_gpm = models.DecimalField(max_digits = 6, decimal_places = 2, blank = True)
	
	def __unicode__(self):
		return self.player_name
	
class Hero(models.Model):
	hero_name_underscored = models.CharField(max_length = 60)
	hero_name = models.CharField(max_length = 50)
	
	def __unicode__(self):
		return self.hero_name_underscored
	
class Games(models.Model):
	player = models.ForeignKey(Player)
	hero = models.ForeignKey(Hero)
	last_hits = models.PositiveIntegerField()
	gpm = models.PositiveIntegerField()
	pub_date = models.DateTimeField(auto_now_add = True)
	rank_number = models.PositiveIntegerField(null = True)
	
	def __unicode__(self):
		return u'%s %s'%(self.hero.hero_name, self.player.player_name)
	
	def get_absolute_url(self):
		return reverse('game_data:successful_submit')
		
class PlayerForm(ModelForm):
	class Meta:
		model = Player
		
class HeroForm(ModelForm):
	class Meta:
		model = Hero
		
class GameForm(ModelForm):
	class Meta:
		model = Games
		fields = ['player', 'hero', 'last_hits', 'gpm']