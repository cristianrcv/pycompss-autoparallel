#!/usr/bin/python

# -*- coding: utf-8 -*-

import nose
import sys

from nose.plugins.base import Plugin

class ExtensionPlugin(Plugin):
        name = "ExtensionPlugin"

        def options(self, parser, env):
                Plugin.options(self,parser,env)

        def configure(self, options, config):
                Plugin.configure(self, options, config)
                self.enabled = True

        @classmethod
        def wantFile(cls, file):
                return file.endswith('.py')

        @classmethod
        def wantDirectory(cls, directory):
                return True

        @classmethod
        def wantModule(cls, file):
                return True


if __name__ == '__main__':
        includeDirs = ["-w", "."]
        nose.main(addplugins=[ExtensionPlugin()], argv=sys.argv.extend(includeDirs))

