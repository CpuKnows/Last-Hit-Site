from django.db.models import F, Q, Max, Avg

from .models import Player, Hero, Game


def add_update_hero_ranking(game_in):
	replaced_rank = 0
	
	ranked_game = Game.objects.ranked(player=game_in.player, hero=game_in.hero)
	
	# A previously ranked game exists
	if len(ranked_game) != 0:
		if (ranked_game[0].last_hits < game_in.last_hits or (ranked_game[0].last_hits == game_in.last_hits and ranked_game[0].gpm < game_in.gpm)):
			replaced_rank = ranked_game[0].rank_number
			ranked_game[0].rank_number = None
			ranked_game[0].save()
		else:
			# Submitted game is not better than currently ranked game
			return
	
	hero_rank_list = Game.objects.ranked(hero=game_in.hero)
	
	# First game with hero by any player
	if len(hero_rank_list) == 0:
		game_in.rank_number = 1
		game_in.save()
		return
		
	if replaced_rank != 0:
		hero_rank_list = hero_rank_list.worse_rank(replaced_rank)
	
	hero_rank_list = hero_rank_list.worse_games(game_in.last_hits, game_in.gpm)
	hero_rank_list = hero_rank_list.order_by('-last_hits', '-gpm', '-pub_date')
	
	# No worse games
	if len(hero_rank_list) == 0:
		lowest_rank = Game.objects.ranked().aggregate(Max('rank_number'))
		game_in.rank_number = lowest_rank['rank_number__max'] + 1
		game_in.save()
		return
	
	rows_updated = hero_rank_list.update(rank_number=F('rank_number') + 1)
	
	if rows_updated == 0:
		game_in.rank_number = replaced_rank
		game_in.save()
		return
		
	game_in.rank_number = hero_rank_list[0].rank_number - 1
	game_in.save()
	
	for game in hero_rank_list:
		game.save()


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


def update_player_rank(game_in):
	
	all_player_games = Game.objects.filter(player=game_in.player).order_by('-pub_date')
	num_games = all_player_games.count()
	if num_games < 10:
		weighted_game_num = num_games
	else:
		weighted_game_num = 10
	
	weighted_games = all_player_games[:weighted_game_num]
	
	averages = all_player_games.aggregate(Avg('last_hits'), Avg('gpm'))
	avg_last_hits_new = averages['last_hits__avg']
	avg_gpm_new = averages['gpm__avg']
	
	for x in range(weighted_game_num):
		avg_last_hits_new += (weighted_games[x].last_hits * (2.0 - (x * 0.1)))
		avg_gpm_new += (weighted_games[x].gpm * (2.0 - (x * 0.1)))
	
	game_in.player.avg_last_hits = avg_last_hits_new
	game_in.player.avg_gpm = avg_gpm_new
	
	worse_player_list = Player.objects.worse_avg(avg_last_hits_new, avg_gpm_new)
	worse_player_list = worse_player_list.order_by('-avg_last_hits', '-avg_gpm', 'overall_rank')
	
	if len(worse_player_list) == 0:
		lowest_rank = Player.objects.ranked().aggregate(Max('overall_rank'))
		if lowest_rank['overall_rank__max'] is not None:
			game_in.player.overall_rank = lowest_rank['overall_rank__max'] + 1
		else:
			game_in.player.overall_rank = 1
		game_in.player.save()
		return
	
	worse_player_list.update(overall_rank=F('overall_rank') + 1)
	
	game_in.player.overall_rank = worse_player_list[0].overall_rank - 1
	game_in.player.save()
	
	for player in worse_player_list:
		player.save()