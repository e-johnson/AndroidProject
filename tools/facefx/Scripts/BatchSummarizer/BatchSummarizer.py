""" Summarize batch processing operations in FaceFX Studio.

Owner: John Briggs

Copyright (c) 2002-2012 OC3 Entertainment, Inc.

"""

from collections import defaultdict
import re
import copy
import datetime

import FxStudio
import ConfidenceScoreCompiler
import ConfidenceScoreGUI


class ProcessedFile(object):
    """ Contains any warnings or errors for a given file. """
    def __init__(self, group_name, anim_name):
        self.group_name = group_name
        self.anim_name = anim_name
        self.filename = None
        self.failed = False
        self.skipped = False
        self.warnings = []
        self.errors = []
        self.errorAreas = []

    def add_warning(self, message):
        self.warnings.append(message)

    def add_error(self, message):
        self.errors.append(message)

    def should_record(self):
        return len(self.warnings) or len(self.errors)

    def __str__(self):
        return '{0}/{1}'.format(self.group_name, self.anim_name)


class LogStateMachine(object):
    """ Represents the transitions between states as discrete funcitons. """
    def __init__(self):
        self.state = 'IRRELEVANT'
        self.reset_state()

        # Regex patterns for interesting lines.
        self.batch_start_pattern = re.compile('Batch started')
        self.path_pattern = re.compile(
            'Animation path: (?P<group>.+)/(?P<anim>.+)')
        self.duration_pattern = re.compile('Duration: (?P<duration>\d*\.\d+)')
        self.language_pattern = re.compile('Language: (?P<language>.*)')
        self.analysis_actor_pattern = re.compile('Analysis Actor: (?P<aa>.*)')
        self.filename_pattern = re.compile('Audio path: (?P<filename>.*)')
        self.anim_success_pattern = re.compile('Animation created successfully')
        self.anim_ignore_pattern = re.compile(
            'Ignoring: Could not analyze file')
        self.anim_fail_pattern = re.compile(
            'Animation was not created successfully')
        self.anim_skipped_pattern = re.compile(
            'skipped processing of audio file')
        self.end_batch_pattern = re.compile('Batch (succeeded|failed)')

        self.message_pattern = re.compile('.*\[.+\]:(?P<message>.*)')

    def reset_state(self):
        self.current_file = None
        self.duration_total = 0.0
        self.language_summary = defaultdict(lambda: 0)
        self.aa_summary = defaultdict(lambda: 0)
        self.processed_files = []
        self.analysis_warnings = []
        self.errorAreas = []

        self.start_time = None
        self.end_time = None

    def process_line(self, log_type, log_line):
        """ Process the line in the context of the current state. """
        if self.state == 'IRRELEVANT':
            if re.search(self.batch_start_pattern, log_line):
                self.reset_state()
                self.start_time = datetime.datetime.now()
                self.state = 'FIND_ANIMATION'

        elif self.state == 'FIND_ANIMATION':
            if log_type == 'Warning':
                self.analysis_warnings.append(log_line)

            m = re.search(self.path_pattern, log_line)
            if m:
                self.current_file = ProcessedFile(
                    m.group('group'), m.group('anim'))
                self.state = 'PROCESSING_ANIMATION'

            m = re.search(self.end_batch_pattern, log_line)
            if m:
                self.end_time = datetime.datetime.now()
                self.state = 'SUMMARY_READY'

        elif self.state == 'PROCESSING_ANIMATION':
            m = re.search(self.anim_ignore_pattern, log_line)
            if m:
                self.current_file.failed = True
                self.processed_files.append(copy.deepcopy(self.current_file))
                self.state = 'FIND_ANIMATION'

            m = re.search(self.anim_skipped_pattern, log_line)
            if m:
                self.current_file.skipped = True
                self.processed_files.append(copy.deepcopy(self.current_file))
                self.state = 'FIND_ANIMATION'

            if log_type == 'Warning':
                m = re.search(self.message_pattern, log_line)
                if m:
                    self.current_file.add_warning(m.group('message'))
                else:
                    self.current_file.add_warning(log_line)
                return

            if log_type == 'Error':
                m = re.search(self.message_pattern, log_line)
                if m:
                    self.current_file.add_warning(m.group('message'))
                else:
                    self.current_file.add_error(log_line)
                return

            m = re.search(self.duration_pattern, log_line)
            if m:
                self.duration_total += float(m.group('duration'))
                return

            m = re.search(self.language_pattern, log_line)
            if m:
                self.language_summary[m.group('language')] += 1
                return

            m = re.search(self.analysis_actor_pattern, log_line)
            if m:
                self.aa_summary[m.group('aa')] += 1
                return

            m = re.search(self.filename_pattern, log_line)
            if m:
                self.current_file.filename = m.group('filename')
                return

            if re.search(self.anim_success_pattern, log_line):
                self.processed_files.append(copy.deepcopy(self.current_file))
                self.state = 'FIND_ANIMATION'
                return

            if re.search(self.anim_fail_pattern, log_line):
                self.current_file.failed = True
                self.processed_files.append(copy.deepcopy(self.current_file))
                self.state = 'FIND_ANIMATION'
                return

            m = re.search(self.end_batch_pattern, log_line)
            if m:
                self.current_file.failed = True
                self.processed_files.append(copy.deepcopy(self.current_file))
                self.end_time = datetime.datetime.now()
                self.state = 'SUMMARY_READY'
                return

    def is_summary_ready(self):
        return self.state == 'SUMMARY_READY'

    def get_execution_time(self):
        """ Return how long it took to process the batch. """
        delta = self.end_time - self.start_time
        minutes, seconds = divmod(delta.seconds, 60)
        return '{0:02}:{1:02}.{2}'.format(minutes, seconds, delta.microseconds)

    def calculate_confidence(self):
        anims = []
        for f in self.processed_files:
            anims.append('{0}/{1}'.format(f.group_name, f.anim_name))

        # Calculate the areas with the worst confidence scores.
        self.errorAreas = ConfidenceScoreCompiler.calculateConfidenceScores(anims)

    def get_summary_lines(self):
        """ Returns a list of lines summarizing the batch operation."""

        def pluralize(count, description):
            # Incredibly naive pluralizer.
            return '{0} {1}{2}'.format(
                count, description, '' if count == 1 else 's')

        lines = []

        # Check how long the processing took.
        elapsed_str = self.get_execution_time()

        num_files = len(self.processed_files)
        num_warnings = 0
        num_errors = 0
        num_failures = 0
        num_skipped = 0
        num_successes = 0
        debug_section = []
        failed_files = []
        skipped_files = []
        for f in self.processed_files:
            num_warnings += len(f.warnings)
            num_errors += len(f.errors)
            if f.failed:
                failed_files.append('\t{0}'.format(f.filename))
                num_failures += 1
            elif f.skipped:
                skipped_files.append('\t{0}'.format(f.filename))
                num_skipped += 1
            else:
                num_successes += 1

            for e in f.errors:
                debug_section.append('\t[Error]:   {0}/{1} :  {2}'.format(
                    f.group_name, f.anim_name, e))
            for w in f.warnings:
                debug_section.append('\t[Warning]: {0}/{1} :  {2}'.format(
                    f.group_name, f.anim_name, w))

        lines.append('Batch analysis completed.')
        lines.append(
            '{0} processed. {1} failed. {2} skipped. {3} generated.'.format(
            pluralize(num_files, 'file'),
            pluralize(num_failures, 'file'),
            pluralize(num_skipped, 'file'),
            pluralize(num_successes, 'animation')))
        lines.append('{0}, {1}'.format(
            pluralize(num_errors, 'error'), pluralize(num_warnings, 'warning')))
        lines.append('Time elapsed: {0}'.format(elapsed_str))

        if len(self.analysis_warnings):
            lines.append('')
            lines.append('Batch warnings:')
            lines.extend(self.analysis_warnings)

        if len(failed_files):
            lines.append('')
            lines.append('Failed files:')
            lines.extend(failed_files)

        if len(skipped_files):
            lines.append('')
            lines.append('Skipped files:')
            lines.extend(skipped_files)

        if len(debug_section):
            lines.append('')
            lines.append('File warnings and errors:')
            lines.extend(debug_section)

        lines.append('')
        lines.append('Total duration: {0}'.format(self.duration_total))
        lines.append('Language distribution:')
        lines.extend(['\t{0}: {1}'.format(name, count) for name, count in
            self.language_summary.iteritems()])
        lines.append('Analysis actor distribution:')
        lines.extend(['\t{0}: {1}'.format(name, count) for name, count in
            self.aa_summary.iteritems()])

        lines.append('')

        ranked = self.errorAreas[:10]
        lines.append('Lowest {0}:'.format(
            pluralize(len(ranked), 'confidence score')))
        lines.extend(['\t{2:.1f}:\t{0}/{1}  [time: {3:.2f} -> {4:.2f}]'.format(f["group"],
            f["anim"], f["maxerror"], f["starttime"], f["endtime"]) for f in ranked])

        return lines

    def reset(self):
        self.state = 'IRRELEVANT'


def actual_log_processing(log_type, message, state_machine=LogStateMachine()):
    """ Actually do the processing. Hidden in a second function to avoid having
    to use a global variable for the state machine.

    """

    state_machine.process_line(log_type, message)
    if state_machine.is_summary_ready():
        state_machine.reset()

        # calculate the confidence scores.
        state_machine.calculate_confidence()
        lines = state_machine.get_summary_lines()

        for line in lines:
            FxStudio.msg(line)
        # Echo to Python if we're not in command-line mode.
        if not FxStudio.isCommandLineMode():
            print '\n'.join(lines)
            if len(state_machine.errorAreas) > 0:
                ConfidenceScoreGUI.createFrame(None, state_machine.errorAreas)


def on_log_message(log_type, message):
    """ Called after FaceFX Studio adds a line to its log files. """
    actual_log_processing(log_type, message)
