"""A quick-and-dirty batch export text file parser.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

import re
import shlex

from fbximporterror import FBXImportError


class BatchExportTextFileParser():
    """Parses a batch export text file. """

    def __init__(self, betf_path):
        """Loads and parses the batch export text file. """
        self.pose_names = None

        if betf_path is None:
            return

        with open(betf_path, 'r') as f:
            content = f.read()
            # Replace '//' comments with '#' for shlex, because shlex
            # operates only on one character at a time.
            lexer = shlex.shlex(re.sub('//', '#', content))
            lexer.commenters += '#'
            lexer.whitespace += ';'  # do not include ; as a token.
            lexer.wordchars += '-'  # used in slade batch export.
            # The lexer leaves the quote characters in the tokens. Remove them.
            tokens = [re.sub(''.join(['[', lexer.quotes, ']']), '', token)
                for token in lexer]
            if len(tokens) % 2:
                # A real batch export file will always have even numbers of tokens.
                raise FBXImportError('Invalid batch export text file.')

            # Pair the name, frame values by zipping offsetting strides through
            # the token list. Cast frame to an integer.
            try:
                self.pose_names = [(name, int(frame)) for name, frame in
                    zip(tokens[::2], tokens[1::2])]
            except ValueError:
                raise FBXImportError('Invalid batch export text file.')
