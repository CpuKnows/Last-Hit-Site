from django.db import models
from django.forms import ModelForm
from django.core.urlresolvers import reverse, reverse_lazy

class Player(models.Model):
	player_name = models.CharField(max_length = 50)
	overall_rank = models.PositiveIntegerField()
	
	def __unicode__(self):
		return self.player_name
	
class Hero(models.Model):
	player = models.ForeignKey(Player)
	hero_name = models.CharField(max_length = 50)
	rank_number = models.PositiveIntegerField()
	hero_name_underscored = models.CharField(max_length = 60)
	
	def __unicode__(self):
		return self.hero_name
	
class Games(models.Model):
	player = models.ForeignKey(Player)
	hero = models.ForeignKey(Hero)
	last_hits = models.PositiveIntegerField()
	gpm = models.PositiveIntegerField()
	pub_date = models.DateTimeField(auto_now_add = True)
	
	def get_absolute_url(self):
		return reverse('game_data:successful_submit')
	
class PlayerForm(ModelForm):
	class Meta:
		model = Player
		
class HeroForm(ModelForm):
	class Meta:
		model = Hero
		
#class GameForm(ModelForm):
#	class Meta:
#		model = Games