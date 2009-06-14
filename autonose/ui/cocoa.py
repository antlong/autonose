#!/usr/bin/env python

import sys

import os
import threading
from Cocoa import *
from WebKit import WebView
import cgi
import objc

from shared import Main

class AutonoseApp(NSObject):
	def initWithMainLoop_(self, mainLoop):
		self.init()
		self.mainLoop = mainLoop
		return self
		
	def run(self):
		pool = NSAutoreleasePool.alloc().init()
		self.app = NSApplication.sharedApplication()
		origin = [100,200]
		size = [400,600]
		self.view = WebView.alloc().initWithFrame_frameName_groupName_(NSMakeRect(0,0, *size), None, None)
		self.view.setAutoresizingMask_(NSViewHeightSizable | NSViewWidthSizable)
		
		self.htmlView = self.view.mainFrame()
		window_mask = NSTitledWindowMask | NSResizableWindowMask | NSClosableWindowMask | NSMiniaturizableWindowMask
		window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
			NSMakeRect(*(origin + size)), window_mask, NSBackingStoreBuffered, True)
		window.setTitle_("Autonose")
		self.doUpdate("<h1>loading...</h1>")
		
		window.contentView().addSubview_(self.view)
		window.makeKeyAndOrderFront_(None)
		try:
			self.app.run()
		except KeyboardInterrupt:
			pool.release()
			self.doExit()

	def doExit(self, *args):
		self.app.terminate_(self)

	def doUpdate(self, page=None):
		if page is None:
			page = self.mainLoop.page
		self.htmlView.loadHTMLString_baseURL_(str(page), NSURL.fileURLWithPath_(os.path.dirname(__file__)))
		self.htmlView.webView().setNeedsDisplay_(True)
	
	def runMainLoop(self):
		self.releasePool = NSAutoreleasePool.alloc().init()
		self.mainLoop.run()
		self.releasePool.release()

class App(object):
	script = __file__
	def __init__(self):
		self.mainloop = Main(delegate=self)
		self.app = AutonoseApp.alloc().initWithMainLoop_(self.mainloop)
		sel = objc.selector(self.app.runMainLoop, signature="v@:")
		self.main = NSThread.detachNewThreadSelector_toTarget_withObject_(sel, self.app, None)
		self.app.run()
	
	def exit(self):
		self.do(self.app.doExit)
	
	def do(self, func, arg=None):
		sel = objc.selector(func, signature="v@:")
		self.app.performSelectorOnMainThread_withObject_waitUntilDone_(sel, arg, True)
	
	def update(self, page=None):
		self.do(self.app.doUpdate, page)


if __name__ == '__main__':
	pool = NSAutoreleasePool.alloc().init()
	App()
	pool.release()
	