

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
import datetime

from flask_appbuilder import Model
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from flask_appbuilder.models.decorators import renders
from flask import Markup

mindate = datetime.date(datetime.MINYEAR, 1, 1)


class Play(Model): 
    __tablename__ = 'plays'

    id = Column(Integer, primary_key = True)
    date = Column(Date)
    away_team = Column(String(20))
    home_team = Column(String(20))
    home_spread = Column(Float)
    home_spread_price = Column(Integer)
    away_moneyline = Column(Integer)
    home_moneyline = Column(Integer)
    bet = Column(String(30))
    wager = Column(Float)
    away_score = Column(Integer)
    home_score = Column(Integer)
    result = Column(String(4))
    profit = Column(Integer)

    total_plays = Column(Integer, nullable=True)

    total_wins = Column(Integer, nullable=True)
    total_losses = Column(Integer, nullable=True)
    total_pushes = Column(Integer, nullable=True)
    total_profit = Column(Integer, nullable=True)

    total_ats = Column(Integer, nullable=True)
    total_moneyline = Column(Integer, nullable=True)

    total_moneyline_wins = Column(Integer, nullable=True)
    total_moneyline_losses = Column(Integer, nullable=True)
    total_moneyline_pushes = Column(Integer, nullable=True)
    total_moneyline_profit = Column(Integer, nullable=True)


    total_ats_wins = Column(Integer, nullable=True)
    total_ats_losses = Column(Integer, nullable=True)
    total_ats_pushes = Column(Integer, nullable=True)
    total_ats_profit = Column(Integer, nullable=True)

    total_2u_wins = Column(Integer, nullable=True)
    total_2u_losses = Column(Integer, nullable=True)
    total_2u_pushes = Column(Integer, nullable=True)
    total_2u_profit = Column(Integer, nullable=True)

    #double_win = False
    #double_loss = False

    def double_win(self):
        if (self.wager == 200):
            if (self.result == 'Win'):
                return True
        return False

    def double_loss(self):
        if (self.wager == 200):
            if (self.result == 'Loss'):
                return True
        return False
    
    def render_double(self, input):
        if (self.double_win()):
            return Markup('<span class="badge rounded-pill bg-success"> '+str(input)+'</span>')
        if (self.double_loss()):
            return Markup('L '+str(input))
        return Markup(str(input))

           # return Markup('<td class="table-success">'+str(input)+'</td>')
 
    @renders('result')
    def custom_date(self):
        away = self.away_team
        home = self.home_team
        if (home == 'blazers'):
            home = 'trail-blazers'
        if (away == 'blazers'):
            away = 'trail-blazers'
        date = self.date
        matchup = "https://www.teamrankings.com/nba/matchup/"+away+"-"+home+"-"+str(date)
        return Markup('<a target="_blank" href="'+matchup+'"><span class="badge rounded-pill" id="link_badge" > '+str(self.date)+'</span></a>')

    @renders('result')
    def custom_result(self):
        if (self.result == 'Win'):
            return Markup('<span class="badge bg-win" > '+str(self.result)+'</span>')
        elif (self.result == 'Loss'):
            return Markup('<span class="badge bg-loss" > '+str(self.result)+'</span>')
        else:
            return self.result
 
    @renders('profit')
    def custom_profit(self):
        if (self.result == 'Win'):
            return Markup('$' + str(self.profit))
        else:
            return Markup('$' + str(self.profit) )

    @renders('wager')
    def custom_wager(self):
        if (self.wager == 200):
            return Markup('<b><u>$' + str(self.wager) + '</u></b>')
        else:
            return Markup('$' + str(self.wager) + '</b>')

    def __repr__(self):
        return (self.away_team)

