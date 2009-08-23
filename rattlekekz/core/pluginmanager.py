#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Make this more usable and smarter :)

class manager():
    def __init__(self):
        self.plugins = {}

    def loadPlugin(self,plugin,params=[]):
        """this option is called by the view to load any plugins."""
        try:
            if not self.plugins.has_key(plugin):
                self.plugins[plugin]=__import__('rattlekekz.plugins',fromlist=[plugin])
                self.plugins[plugin]=getattr(self.plugins[plugin],plugin)
                try:
                    self.plugins[plugin]=self.plugins[plugin].plugin(self,self.model,self.view,*params)
                except:
                    del self.plugins[plugin]
                    self.view.gotException("Error executing %s." % plugin)
            else:
                self.view.gotException("%s is already loaded" % plugin)
        except:
            self.view.gotException("Error due loading of %s. May it doesn't exist, is damaged or some depencies aren't installed?" % plugin)

    def unloadPlugin(self,plugin):
        try:
            self.plugins[plugin].unload()
            del self.plugins[plugin]
        except:
            try:
                del self.view.plugins[plugin]
                del self.model.plugins[plugin]
                del self.plugins[plugin]
            except:
                self.gotException('unable to unload plugin %s.' % plugin)

class iterator():
    def hiThere(self,name,instance):
        """method for plugins to say "hi there" :D"""
        if not self.plugins.has_key(name):
            self.plugins[name]=instance
            return (self,0,"plugin registered")
        else:
            return (self,1,"the plugin or another instance of it is allready registered")

    def outHere(self,name,instance):
        """method for plugins to get the hell out of here"""
        if self.plugins.has_key(name):
            if self.plugins[name] is instance:
                del self.plugins[name]
            else:
                self.controller.gotException("instance don't match registered plugin") # This should never occure ;)

    def iterPlugins(self,method,kwds=[]):
        taken,handled=False,False
        for i in self.plugins:
            try:
                value = getattr(self.plugins[i], method)(self,*kwds)
                if value is 'handled':
                    handled=True
                    break
                elif value is 'taken':
                    taken=True
                    continue
            except AttributeError:
                pass # TODO: May add some message or so.
            except:
                pass # TODO: add message for error in plugin xy
        if not handled:
            getattr(self.controller, method)(*kwds)
