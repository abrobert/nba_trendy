from flask import render_template, request
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action
from flask import redirect
from flask_appbuilder import ModelView
from .models import Play


class PlayModelView(ModelView):

    datamodel = SQLAInterface(Play)

    label_columns = {'away_moneyline':'Away ML Price', 'home_moneyline': 'Home ML Price', 'away_team': 'Away Team', 'home_team': 'Home Team', 'home_spread': 'Spread(Home)', 
    'away_score': 'Away Score', 'home_score': 'Home Score', 'bet': 'Bet Placed', 'wager': 'Wager', 'result': 'Bet Result', 'profit': 'Net Profit'}
    list_columns = ['date','away_team','home_team', 'home_spread', 'away_score', 'home_score','bet', 'result', 'profit']


    show_fieldsets = [
        ( 
            'Game', 
            {
                'fields': ['date', 'away_team', 'home_team', 'away_score', 'home_score']
            }
        ),
        ( 
            'Odds Info', 
            {
                'fields': ['home_spread', 'home_spread_price', 'away_moneyline', 'home_moneyline'],
                "expanded": False
            }, 
        ),
        ( 
            'Bet', 
            {
                'fields': ['bet', 'wager' 'result', 'profit'], 
                'expanded': False 
            }
        )
    ]
