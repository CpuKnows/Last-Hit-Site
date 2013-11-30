from django.db.models import F, Q, Max, Min, Avg

from .models import Player, Hero, Game


def add_update_hero_ranking(game_in):
	replaced_rank = 0

	hero_rank_list = Game.objects.ranked(hero=game_in.hero)
	
	# First game with hero by any player
	if len(hero_rank_list) == 0:
		game_in.rank_number = 1
		game_in.save()
		return

	hero_rank_list = hero_rank_list.filter(player=game_in.player)

	# A previously ranked game exists
	if len(hero_rank_list) != 0:
		if (hero_rank_list[0].last_hits < game_in.last_hits or (hero_rank_list[0].last_hits == game_in.last_hits and hero_rank_list[0].gpm < game_in.gpm)):
			worse_games = Game.objects.worse_rank(hero_rank_list[0].hero, hero_rank_list[0].rank_number)
			hero_rank_list[0].rank_number = None
			hero_rank_list[0].save()
			worse_games.update(rank_number=F('rank_number') - 1)
			for game in worse_games:
				game.save()
			return add_update_hero_ranking(game_in)
		else:
			# Submitted game is not better than currently ranked game
			return

	worse_games = Game.objects.worse_games(game_in.hero, game_in.last_hits, game_in.gpm)
	worse_games.order_by('-last_hits', '-gpm', '-pub_date')

	# No worse games
	if len(worse_games) == 0:
		lowest_rank = Game.objects.ranked(hero=game_in.hero).aggregate(Max('rank_number'))
		game_in.rank_number = lowest_rank['rank_number__max'] + 1
		game_in.save()
		return

	else:
		#new_game_rank = hero_rank_list[0].rank_number
		worse_games.update(rank_number=F('rank_number') + 1)
		for game in worse_games:
			game.save()

		new_rank = worse_games.aggregate(Min('rank_number'))
		game_in.rank_number = new_rank['rank_number__min'] - 1
		game_in.save()


def delete_update_hero_rank(game_in):
	
	if game_in.rank_number is not None:
		hero_rank_list = Game.objects.worse_rank(game_in.hero, game_in.rank_number)
		hero_rank_list.update(rank_number=F('rank_number') - 1)
		
		for game in hero_rank_list:
			game.save()
			
		game_in.rank_number = None
		game_in.last_hits = 0
		game_in.gpm = 0
		game_in.save()

		game_to_rank = Game.objects.filter(hero=game_in.hero, player=game_in.player)
		game_to_rank = game_to_rank.order_by('-last_hits', '-gpm', '-pub_date')
		
		if len(game_to_rank) != 0:
			add_update_hero_ranking(game_to_rank[0])


def add_update_player_rank(player_in):
	
	all_player_games = Game.objects.filter(player=player_in).order_by('-pub_date')
	num_games = all_player_games.count()

	if num_games < 10:
		weighted_game_num = num_games
	else:
		weighted_game_num = 10
	
	weighted_games = all_player_games[:weighted_game_num]
	
	averages = all_player_games.aggregate(Avg('last_hits'), Avg('gpm'))
	avg_last_hits_new = averages['last_hits__avg']
	avg_gpm_new = averages['gpm__avg']

	if avg_last_hits_new is None or avg_gpm_new is None:
		avg_last_hits_new = 0
		avg_gpm_new = 0
	
	for x in range(weighted_game_num):
		avg_last_hits_new += (weighted_games[x].last_hits * (2.0 - (x * 0.1)))
		avg_gpm_new += (weighted_games[x].gpm * (2.0 - (x * 0.1)))
	
	player_in.avg_last_hits = avg_last_hits_new
	player_in.avg_gpm = avg_gpm_new
	
	worse_player_list = Player.objects.worse_avg(avg_last_hits_new, avg_gpm_new)
	worse_player_list = worse_player_list.order_by('-avg_last_hits', '-avg_gpm', 'overall_rank')
	
	if len(worse_player_list) == 0:
		lowest_rank = Player.objects.ranked().aggregate(Max('overall_rank'))
		if num_games == 0:
			player_in.overall_rank = None
		elif lowest_rank['overall_rank__max'] is not None:
			player_in.overall_rank = lowest_rank['overall_rank__max'] + 1
		else:
			player_in.overall_rank = 1
		player_in.save()
		return
	
	worse_player_list.update(overall_rank=F('overall_rank') + 1)
	
	player_in.overall_rank = worse_player_list[0].overall_rank - 1
	player_in.save()
	
	for player in worse_player_list:
		player.save()


def delete_update_player_rank(player_in):

	if player_in.overall_rank is not None:
		worse_player_list = Player.objects.worse_rank(player_in.overall_rank)
		worse_player_list.update(overall_rank=F('overall_rank') - 1)

		for player in worse_player_list:
			player.save()

		player_in.overall_rank = None
		player_in.save()
		add_update_player_rank(player_in)