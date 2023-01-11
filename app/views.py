from flask import render_template, request
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterEqual, FilterGreater, BaseFilter, FilterSmaller
from flask_appbuilder.models.sqla import filters
from sqlalchemy import or_, and_
from sqlalchemy.sql import text
from flask_appbuilder.actions import action
from flask import redirect
from flask_appbuilder import ModelView, ModelRestApi, BaseView, expose, has_access, DirectByChartView, GroupByChartView
from .models import Play
from flask_appbuilder.models.group import aggregate_avg, aggregate_sum, aggregate_count
from .widgets import MyListWidget
from . import appbuilder, db
from datetime import datetime, timedelta
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Float
from sqlalchemy.sql import func

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

class CustomPlayModelView(ModelView):
    # sql = db.text('''
    # select * from plays WHERE date >= "2022-11-30" and date <= "2022-12-05";
    # ''')
    # db.session.execute(sql)
    # db.session.commit()
    
    #query = db.session.query(Play)
    #route_base = '/table'
    datamodel = SQLAInterface(Play)
    base_order = ['id', 'desc']

    # select  plays.id as id,
    sql = ''' 
    SELECT
    SUM ( 
            CASE  
                WHEN (plays.result = 'Win') THEN 1
                            
             END 
        ) AS total_wins,
    SUM ( 
            CASE  
                WHEN (plays.result = 'Loss') THEN 1                            
            END 
        ) AS total_losses,
    SUM ( 
            CASE 
                WHEN (plays.result = 'Push') THEN 1                            
            END 
        ) AS total_pushes,
    SUM ( profit ) AS total_profit,
    SUM ( 
            CASE  
              WHEN position( 'ML' IN plays.bet )>0 THEN 1                            
             END 
        ) AS total_moneyline,
    SUM ( 
            CASE  
                WHEN position( 'ML' IN plays.bet ) < 1 THEN 1                              
             END 
        ) AS total_ats,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet )> 0 AND (plays.result = 'Win') THEN 1                              
            END 
        ) AS total_moneyline_wins,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet )> 0 AND (plays.result = 'Loss') THEN 1                              
            END 
        ) AS total_moneyline_losses,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet )> 0 AND (plays.result = 'Push') THEN 1                              
            END 
        ) AS total_moneyline_pushes,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet )> 0 THEN plays.profit                              
            END 
        ) AS total_moneyline_profit,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet ) < 1 AND (plays.result = 'Win') THEN 1                              
            END 
        ) AS total_ats_wins,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet )< 1 AND (plays.result = 'Loss') THEN 1                              
            END 
        ) AS total_ats_losses,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet )< 1 AND (plays.result = 'Push') THEN 1                              
            END 
        ) AS total_ats_pushes,
    SUM ( 
            CASE 
                WHEN position( 'ML' IN plays.bet )< 1 THEN plays.profit                              
            END 
        ) AS total_ats_profit,
    SUM ( 
            CASE 
                WHEN (plays.wager = 200) AND (plays.result = 'Win') THEN 1                              
            END 
        ) AS total_2u_wins,
    SUM ( 
            CASE 
                WHEN (plays.wager = 200) AND (plays.result = 'Loss') THEN 1                              
            END 
        ) AS total_2u_losses,
    SUM ( 
            CASE 
                WHEN (plays.wager = 200) AND (plays.result = 'Push') THEN 1                              
            END 
        ) AS total_2u_pushes,
    SUM ( 
            CASE 
                WHEN (plays.wager = 200) THEN plays.profit                              
            END 
        ) AS total_2u_profit

    from plays  WHERE date >= :from_date  and  date <= :to_date ;
        '''

    all = datetime(2022, 10, 1).strftime('%Y-%m-%d')
    yesterday_date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
    three_days_ago = (datetime.today() - timedelta(3)).strftime('%Y-%m-%d')
    seven_days_ago = (datetime.today() - timedelta(7)).strftime('%Y-%m-%d')
    thirty_days_ago = (datetime.today() - timedelta(30)).strftime('%Y-%m-%d')

    today = datetime.today().strftime('%Y-%m-%d')
    total_plays = appbuilder.get_session.query(Play).count()
    print(total_plays)
    
    total_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.date >= all) & (Play.date <= today) ).count()
    total_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.date >= all) & (Play.date <= today)).count()
    total_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.date >= all) & (Play.date <= today) ).count()
    total_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_profit")).where((Play.date >= all) & (Play.date <= today) ).first()[0]
    if (total_profit == None):
        total_profit = 0

    total_ats = appbuilder.get_session.query(Play).where(~Play.bet.contains("ML") & (Play.date >= all) & (Play.date <= today) ).count()
    total_ml = appbuilder.get_session.query(Play).where(Play.bet.contains("ML") & (Play.date >= all) & (Play.date <= today) ).count()


    total_ats_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (~Play.bet.contains("ML")) & (Play.date >= all) & (Play.date <= today) ).count()
    total_ats_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (~Play.bet.contains("ML")) & (Play.date >= all) & (Play.date <= today) ).count()
    total_ats_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (~Play.bet.contains("ML")) & (Play.date >= all) & (Play.date <= today) ).count()
    total_ats_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ats_profit")).where((Play.date >= all) & (Play.date <= today) & (~Play.bet.contains("ML") )).first()[0]
    if (total_ats_profit == None):
        total_ats_profit = 0
    total_ml_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.bet.contains("ML")) & (Play.date >= all) & (Play.date <= today) ).count()
    total_ml_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.bet.contains("ML")) & (Play.date >= all) & (Play.date <= today) ).count()
    total_ml_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.bet.contains("ML")) & (Play.date >= all) & (Play.date <= today) ).count()
    total_ml_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ml_profit")).where((Play.date >= all) & (Play.date <= today) & (Play.bet.contains("ML") )).first()[0]
    if (total_ml_profit == None):
        total_ml_profit = 0
    total_2u_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.wager == 200) & (Play.date >= all) & (Play.date <= today) ).count()
    total_2u_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.wager == 200) & (Play.date >= all) & (Play.date <= today) ).count()
    total_2u_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.wager == 200) & (Play.date >= all) & (Play.date <= today) ).count()
    total_2u_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_2u_profit")).where((Play.date >= all) & (Play.date <= today) & (Play.wager == 200)).first()[0]
    if (total_2u_profit == None):
        total_2u_profit = 0
    all_plays = {
        'total_wins': total_wins, 
        'total_losses': total_losses, 
        'total_pushes': total_pushes, 
        'total_profit': total_profit,

        'total_ats_wins': total_ats_wins, 
        'total_ats_losses': total_ats_losses, 
        'total_ats_pushes': total_ats_pushes, 
        'total_ats_profit': total_ats_profit, 

        'total_moneyline_wins': total_ml_wins, 
        'total_moneyline_losses': total_ml_losses, 
        'total_moneylines_pushes': total_ml_pushes, 
        'total_moneyline_profit': total_ml_profit, 

        'total_2u_wins': total_2u_wins, 
        'total_2u_losses': total_2u_losses, 
        'total_2u_pushes': total_2u_pushes,       
        'total_2u_profit': total_2u_profit 

        }

    total_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.date >= yesterday_date) & (Play.date <= today)).count()
    total_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_profit")).where((Play.date >= yesterday_date) & (Play.date <= today) ).first()[0]
    if (total_profit == None):
        total_profit = 0
    total_ats = appbuilder.get_session.query(Play).where(~Play.bet.contains("ML") & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_ml = appbuilder.get_session.query(Play).where(Play.bet.contains("ML") & (Play.date >= yesterday_date) & (Play.date <= today) ).count()


    total_ats_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (~Play.bet.contains("ML")) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_ats_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (~Play.bet.contains("ML")) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_ats_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (~Play.bet.contains("ML")) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_ats_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ats_profit")).where((Play.date >= yesterday_date) & (Play.date <= today) & (~Play.bet.contains("ML") )).first()[0]
    if (total_ats_profit == None):
        total_ats_profit = 0
    total_ml_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.bet.contains("ML")) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_ml_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.bet.contains("ML")) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_ml_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.bet.contains("ML")) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_ml_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ml_profit")).where((Play.date >= yesterday_date) & (Play.date <= today) & (Play.bet.contains("ML") )).first()[0]
    if (total_ml_profit == None):
        total_ml_profit = 0
    total_2u_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.wager == 200) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_2u_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.wager == 200) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_2u_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.wager == 200) & (Play.date >= yesterday_date) & (Play.date <= today) ).count()
    total_2u_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_2u_profit")).where((Play.date >= yesterday_date) & (Play.date <= today) & (Play.wager == 200)).first()[0]
    if (total_2u_profit == None):
        total_2u_profit = 0

    yesterday = {
        'total_wins': total_wins, 
        'total_losses': total_losses, 
        'total_pushes': total_pushes, 
        'total_profit': total_profit,

        'total_ats_wins': total_ats_wins, 
        'total_ats_losses': total_ats_losses, 
        'total_ats_pushes': total_ats_pushes, 
        'total_ats_profit': total_ats_profit, 

        'total_moneyline_wins': total_ml_wins, 
        'total_moneyline_losses': total_ml_losses, 
        'total_moneylines_pushes': total_ml_pushes, 
        'total_moneyline_profit': total_ml_profit, 

        'total_2u_wins': total_2u_wins, 
        'total_2u_losses': total_2u_losses, 
        'total_2u_pushes': total_2u_pushes,       
        'total_2u_profit': total_2u_profit 

        }
    total_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.date >= three_days_ago) & (Play.date <= today)).count()
    total_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_profit")).where((Play.date >= three_days_ago) & (Play.date <= today) ).first()[0]
    if (total_profit == None):
        total_profit = 0

    total_ats = appbuilder.get_session.query(Play).where(~Play.bet.contains("ML") & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_ml = appbuilder.get_session.query(Play).where(Play.bet.contains("ML") & (Play.date >= three_days_ago) & (Play.date <= today) ).count()



    total_ats_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (~Play.bet.contains("ML")) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_ats_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (~Play.bet.contains("ML")) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_ats_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (~Play.bet.contains("ML")) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_ats_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ats_profit")).where((Play.date >= three_days_ago) & (Play.date <= today) & (~Play.bet.contains("ML") )).first()[0]
    if (total_ats_profit == None):
        total_ats_profit = 0

    total_ml_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.bet.contains("ML")) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_ml_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.bet.contains("ML")) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_ml_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.bet.contains("ML")) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_ml_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ml_profit")).where((Play.date >= three_days_ago) & (Play.date <= today) & (Play.bet.contains("ML") )).first()[0]
    if (total_ml_profit == None):
        total_ml_profit = 0

    total_2u_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.wager == 200) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_2u_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.wager == 200) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_2u_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.wager == 200) & (Play.date >= three_days_ago) & (Play.date <= today) ).count()
    total_2u_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_2u_profit")).where((Play.date >= three_days_ago) & (Play.date <= today) & (Play.wager == 200)).first()[0]
    if (total_2u_profit == None):
        total_2u_profit = 0


    last_three = {
        'total_wins': total_wins, 
        'total_losses': total_losses, 
        'total_pushes': total_pushes, 
        'total_profit': total_profit,

        'total_ats_wins': total_ats_wins, 
        'total_ats_losses': total_ats_losses, 
        'total_ats_pushes': total_ats_pushes, 
        'total_ats_profit': total_ats_profit, 

        'total_moneyline_wins': total_ml_wins, 
        'total_moneyline_losses': total_ml_losses, 
        'total_moneylines_pushes': total_ml_pushes, 
        'total_moneyline_profit': total_ml_profit, 

        'total_2u_wins': total_2u_wins, 
        'total_2u_losses': total_2u_losses, 
        'total_2u_pushes': total_2u_pushes,       
        'total_2u_profit': total_2u_profit 

        }

    total_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.date >= seven_days_ago) & (Play.date <= today)).count()
    total_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_profit")).where((Play.date >= seven_days_ago) & (Play.date <= today) ).first()[0]
    if (total_profit == None):
        total_profit = 0

    total_ats = appbuilder.get_session.query(Play).where(~Play.bet.contains("ML") & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_ml = appbuilder.get_session.query(Play).where(Play.bet.contains("ML") & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()


    total_ats_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (~Play.bet.contains("ML")) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_ats_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (~Play.bet.contains("ML")) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_ats_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (~Play.bet.contains("ML")) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_ats_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ats_profit")).where((Play.date >= seven_days_ago) & (Play.date <= today) & (~Play.bet.contains("ML") )).first()[0]
    if (total_ats_profit == None):
        total_ats_profit = 0

    total_ml_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.bet.contains("ML")) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_ml_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.bet.contains("ML")) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_ml_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.bet.contains("ML")) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_ml_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ml_profit")).where((Play.date >= seven_days_ago) & (Play.date <= today) & (Play.bet.contains("ML") )).first()[0]
    if (total_ml_profit == None):
        total_ml_profit = 0

    total_2u_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.wager == 200) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_2u_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.wager == 200) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_2u_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.wager == 200) & (Play.date >= seven_days_ago) & (Play.date <= today) ).count()
    total_2u_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_2u_profit")).where((Play.date >= seven_days_ago) & (Play.date <= today) & (Play.wager == 200)).first()[0]
    if (total_2u_profit == None):
        total_2u_profit = 0

    last_seven = {
        'total_wins': total_wins, 
        'total_losses': total_losses, 
        'total_pushes': total_pushes, 
        'total_profit': total_profit,

        'total_ats_wins': total_ats_wins, 
        'total_ats_losses': total_ats_losses, 
        'total_ats_pushes': total_ats_pushes, 
        'total_ats_profit': total_ats_profit, 

        'total_moneyline_wins': total_ml_wins, 
        'total_moneyline_losses': total_ml_losses, 
        'total_moneylines_pushes': total_ml_pushes, 
        'total_moneyline_profit': total_ml_profit, 

        'total_2u_wins': total_2u_wins, 
        'total_2u_losses': total_2u_losses, 
        'total_2u_pushes': total_2u_pushes,       
        'total_2u_profit': total_2u_profit 

        }

    total_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.date >= thirty_days_ago) & (Play.date <= today)).count()
    total_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_profit")).where((Play.date >= thirty_days_ago) & (Play.date <= today) ).first()[0]
    if (total_profit == None):
        total_profit = 0

    total_ats = appbuilder.get_session.query(Play).where(~Play.bet.contains("ML") & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_ml = appbuilder.get_session.query(Play).where(Play.bet.contains("ML") & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()


    total_ats_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (~Play.bet.contains("ML")) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_ats_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (~Play.bet.contains("ML")) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_ats_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (~Play.bet.contains("ML")) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_ats_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ats_profit")).where((Play.date >= thirty_days_ago) & (Play.date <= today) & (~Play.bet.contains("ML") )).first()[0]
    if (total_ats_profit == None):
        total_ats_profit = 0

    total_ml_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.bet.contains("ML")) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_ml_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.bet.contains("ML")) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_ml_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.bet.contains("ML")) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_ml_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_ml_profit")).where((Play.date >= thirty_days_ago) & (Play.date <= today) & (Play.bet.contains("ML") )).first()[0]
    if (total_ml_profit == None):
        total_ml_profit = 0

    total_2u_wins = appbuilder.get_session.query(Play).where((Play.result == 'Win') & (Play.wager == 200) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_2u_losses = appbuilder.get_session.query(Play).where((Play.result == 'Loss') & (Play.wager == 200) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_2u_pushes = appbuilder.get_session.query(Play).where((Play.result == 'Push') & (Play.wager == 200) & (Play.date >= thirty_days_ago) & (Play.date <= today) ).count()
    total_2u_profit = appbuilder.get_session.query( func.sum(Play.profit).label("total_2u_profit")).where((Play.date >= thirty_days_ago) & (Play.date <= today) & (Play.wager == 200)).first()[0]
    if (total_2u_profit == None):
        total_2u_profit = 0

    last_thirty = {
        'total_wins': total_wins, 
        'total_losses': total_losses, 
        'total_pushes': total_pushes, 
        'total_profit': total_profit,

        'total_ats_wins': total_ats_wins, 
        'total_ats_losses': total_ats_losses, 
        'total_ats_pushes': total_ats_pushes, 
        'total_ats_profit': total_ats_profit, 

        'total_moneyline_wins': total_ml_wins, 
        'total_moneyline_losses': total_ml_losses, 
        'total_moneylines_pushes': total_ml_pushes, 
        'total_moneyline_profit': total_ml_profit, 

        'total_2u_wins': total_2u_wins, 
        'total_2u_losses': total_2u_losses, 
        'total_2u_pushes': total_2u_pushes,       
        'total_2u_profit': total_2u_profit 

        }
    # all = datetime(2022, 10, 1).strftime('%Y-%m-%d')
    # all_plays = appbuilder.get_session.query(Play).from_statement(text(sql)).params({'from_date':  all, 'to_date':datetime.today().strftime('%Y-%m-%d')}).all()

    # #list_widget = MyListWidget
    # yesterday_date = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')
    # yesterday = appbuilder.get_session.query(Play).from_statement(text(sql)).params({'from_date':  yesterday_date, 'to_date':datetime.today().strftime('%Y-%m-%d')}).all()
    

    # three_days_ago = (datetime.today() - timedelta(3)).strftime('%Y-%m-%d')
    # three = appbuilder.get_session.query(Play).from_statement(text(sql)).params({'from_date':  three_days_ago, 'to_date':datetime.today().strftime('%Y-%m-%d')}).all()
    
    # seven_days_ago = (datetime.today() - timedelta(7)).strftime('%Y-%m-%d')
    # seven = appbuilder.get_session.query(Play).from_statement(text(sql)).params({'from_date':  seven_days_ago, 'to_date':datetime.today().strftime('%Y-%m-%d')}).all()
    

    # thirty_days_ago = (datetime.today() - timedelta(30)).strftime('%Y-%m-%d')
    # thirty = appbuilder.get_session.query(Play).from_statement(text(sql)).params({'from_date':  thirty_days_ago, 'to_date':datetime.today().strftime('%Y-%m-%d')}).all()
   
    # print(str(seven[0].total_wins) + ' - '+str(seven[0].total_losses) + ' - ' +str(seven[0].total_pushes))
    # # for i in seven:
    # #     print(i.home_moneyline)
    # #wins = datamodel.get_values_json(seven, datamodel.get_columns_list)
    yesterday_filter = '?_flt_1_date='+str(yesterday_date)
    last_three_filter = '?_flt_1_date='+str(three_days_ago)
    last_seven_filter = '?_flt_1_date='+str(seven_days_ago)
    last_30_filter = '?_flt_1_date='+str(thirty_days_ago)
    all_filter = '?_flt_1_date='+str(all)
    extra_args = {
        'yesterday_filter': yesterday_filter,
        'yesterday': yesterday,
        'last_three_filter': last_three_filter,
        'last_three': last_three,
        'last_seven_filter': last_seven_filter,
        'last_seven': last_seven,
        'last_thirty_filter': last_30_filter,
        'last_thirty': last_thirty,
        'all': all_filter,
        'all_plays':all_plays
    }
    
    list_template = 'list_template.html'

    #base_filters = [['date', FilterGreater, '2022-11-30'], ['date', FilterSmaller, '2022-12-06' ]]
    #appbuilder.get_session.query(Play).from_statement(text("select * from plays WHERE date >= :from_date and date <= :to_date;")).params({'from_date': '2022-11-30', 'to_date':'2022-12-05'}).all()
    # user = db.session.query(Play).from_statement(text("select * from plays WHERE date >= :from_date and date <= :to_date;")).params({'from_date': '2022-11-30', 'to_date':'2022-12-05'}).all()
   # print(len(user))
    
    # user = datamodel.query()
    #     db.text("select * from plays WHERE date >= :from_date and date <= to_date;")
    # ).params(from_date='2022-11-30', to_date='2022-12-05').first()

    # db.session.execute(sql)
    # db.session.commit()

    label_columns = {'custom_date': 'Date', 'away_moneyline':'Away ML Price', 'home_moneyline': 'Home ML Price', 'away_team': 'Away Team', 'home_team': 'Home Team', 'home_spread': 'Spread(Home)', 
    'away_score': 'Away Score', 'home_score': 'Home Score', 'bet': 'Bet Placed', 'custom_wager': 'Wager', 'custom_result': 'Bet Result', 'custom_profit': 'Net Profit'}
    list_columns = ['custom_date','away_team','home_team', 'home_spread', 'away_score', 'home_score','bet', 'custom_wager', 'custom_result', 'custom_profit']


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
                "expanded": True
            }, 
        ),
        ( 
            'Bet', 
            {
                'fields': ['bet', 'wager', 'result', 'profit'], 
                'expanded': True 
            }
        )
    ]
    

class PlayChartView(DirectByChartView):

    datamodel = SQLAInterface(Play)

    chart_title = "Direct Data"
    base_filters = [['wager', FilterEqual, '200.0'], ['date', FilterGreater, '2022-12-01' ]]
    definitions = [
        {
            "group": "date",
            "series": ["result", "profit"],
        }
    ]

class DateLess(BaseFilter):
    name = "Plays With Aggregates Between Dates"
    arg_name = "as"
    
    def apply(self, query, value):
        query, field = filters.get_field_setup_query(query, self.model, self.column_name)
        value = filters.set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query
        
        return query.filter(field < value)

class DateGreater(BaseFilter):
    name = "Plays With Aggregates Between Dates"
    arg_name = "as"
    
    def apply(self, query, value):
        query, field = filters.get_field_setup_query(query, self.model, self.column_name)
        value = filters.set_value_to_type(self.datamodel, self.column_name, value)

        if value is None:
            return query
        
        return query.filter(field > value)

        
class PlayChartView2(GroupByChartView):

    datamodel = SQLAInterface(Play)


    chart_title = "Statistics"
    chart_type = "LineChart"
    definitions = [
        {
            "label": "date Stat",
            "group": "date",
            "series": [
                (aggregate_sum, "profit"),
                (aggregate_avg, "profit")
            ],
        }
    ]



class MyView(BaseView):

    default_view = 'method1'

    @expose('/method1/')
    @has_access
    def method1(self):
        # do something with param1
        # and return to previous page or index
        return 'Hello'

    @expose('/method2/<string:param1>')
    @has_access
    def method2(self, param1):
        # do something with param1
        # and render template with param
        param1 = 'Goodbye %s' % (param1)
        return param1


    @expose('/method3/<string:param1>')
    @has_access
    def method3(self, param1):
        # do something with param1
        # and render template with param
        param1 = 'Goodbye %s' % (param1)
        self.update_redirect()
        return self.render_template('model.html',
                            param1 = param1)

        
# db.create_all()
# appbuilder.add_view(
#     PlayModelView, "List Plays", icon="fa-envelope", category="Plays"
# )
# appbuilder.add_view(
#     CustomPlayModelView, "List Custom Plays", icon="fa-envelope", category="Plays"
# )
# #appbuilder.add_view(CustomPlayModelView, "List Custom Plays", href=CustomPlayModelView.endpoint+"/table/", icon="fa-envelope", category="Plays")
# appbuilder.add_view(
#     PlayChartView,
#     "Show Play Chart",
#     icon="fa-dashboard",
#     category="Statistics",
# )
# appbuilder.add_view(
#     PlayChartView2,
#     "Show Play Chart2",
#     icon="fa-dashboard",
#     category="Statistics",
# )
# appbuilder.add_view(MyView, "Method1", category='My View')
# appbuilder.add_link("Method2", href='/myview/method2/john', category='My View')
# appbuilder.add_link("Method3", href='/myview/method3/john', category='My View')

"""
    Create your Model based REST API::

    class MyModelApi(ModelRestApi):
        datamodel = SQLAInterface(MyModel)

    appbuilder.add_api(MyModelApi)


    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(
        MyModelView,
        "My View",
        icon="fa-folder-open-o",
        category="My Category",
        category_icon='fa-envelope'
    )
"""

"""
    Application wide 404 error handler
"""


@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


