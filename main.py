#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.ext import db
import time

class Game(db.Model):
    host = db.StringProperty()
    size = db.IntegerProperty()
    name = db.StringProperty()
    players = db.StringListProperty(str)
    created = db.DateTimeProperty(auto_now_add=True)
    
    def remaining(self):
        return self.size - len(self.players)
    
    def __str__(self):
        return ','.join(['-1', self.host, self.name, str(self.remaining())])
    
    def join(self, id):
        self.players.append(id)
        self.put()
        if len(self.players) >= self.size:
            self.delete()
        return ','.join([str(self.players.index(id)), self.host, self.name or '', str(self.remaining())])

class JoinHandler(webapp.RequestHandler):
    def post(self):
        players = self.request.get('players', '2')
        game = self.request.get('game', None)
        id = self.request.get('id')
        
        q = Game.all().filter('size =', int(players))
        if game:
            q.filter('name =', game)
        game = q.get()
        if game:
            self.response.out.write(game.join(id))
        else:
            self.error(404)
            #self.response.out.write('')

class HostHandler(webapp.RequestHandler):
    def post(self):
        players = self.request.get('players', '2')
        id = self.request.get('id')
        gid = self.request.get('game', hex(int(time.time()*1000))[2:])
        
        game = Game(host=id, size=int(players), name=gid)
        game.put()
        self.response.out.write(str(game))
        


def main():
    application = webapp.WSGIApplication([
        ('/host', HostHandler),
        ('/join', JoinHandler),     ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
