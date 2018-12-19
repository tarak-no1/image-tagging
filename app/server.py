# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import logging.config

import tornado.ioloop
import tornado.web
from tornado.options import options

from app.settings import MODEL_DIR, STATIC_DIR
from app.handler import IndexHandler, GetAttributes, Upload, ContactUsHandler


MODELS = {}


def main():
    """Start Server"""
    # Get the Port and Debug mode from command line options or default in settings.py
    options.parse_command_line()

    # create logger for app
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)

    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=format)

    # Load ML Models
    logger.info("Loading the Model...")
    
    urls = [
        (r"/image-tagging", IndexHandler),
        (r"/image-tagging/get-attributes", GetAttributes),
        (r"/image-tagging/upload-files", Upload),
        (r"/image-tagging/contact-us", ContactUsHandler)
    ]

    # Create Tornado application
    application = tornado.web.Application(
        urls,
        debug=options.debug,
        static_path=STATIC_DIR,
        autoreload=options.debug)

    # Start Server
    logger.info("Starting App on Port: {} with Debug Mode: {}".format(options.port, options.debug))
    application.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
