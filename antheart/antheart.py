
import argparse
import logging
import time
import Queue

LOGGER = logging.getLogger()


from . import heart

def build_parser():
    PARSER = argparse.ArgumentParser(description='Heart rate monitoring utlities.')
    PARSER.add_argument('--debug', action='store_true', help='Print debug output')
    parsers = PARSER.add_subparsers(dest='command')
    target_parser = parsers.add_parser('target', help='')
    target_parser.add_argument('rate', type=float, help='Target this rate')
    thresh_mx = target_parser.add_mutually_exclusive_group()

    thresh_mx.add_argument('--above', action='store_true', help='Heart rate must be above rate')
    thresh_mx.add_argument('--below', action='store_true', help='Heart rate must be below rate')
    thresh_mx.add_argument('--threshold', type=float, help='Number of beats either way to accept', default=5)

    target_parser.add_argument('--threshold-seconds', type=float, help='How long to wait before warning', default=5)
    target_parser.add_argument('--warn-period', type=float, help='Rewarn after delay', default=5)

    return PARSER


def main():
    args = build_parser().parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.command == 'target':
        if args.above:
            lower_rate, upper_rate = args.rate, None
        elif args.below:
            lower_rate, upper_rate = None, args.rate, 
        else:
            lower_rate = args.rate - args.threshold
            upper_rate = args.rate + args.threshold

        target_heart_rate(lower_rate, upper_rate, args.threshold_seconds, args.warn_period)
    else:
        raise ValueError(args.command)


def get_heart_rate(q, timeout):
    if timeout is None:
        return q.get()
    elif timeout > 0:
        try:
            return q.get(timeout=timeout)
        except Queue.Empty:
            return None
    else:
        return None

def target_heart_rate(lower_rate, upper_rate, threshold_seconds, warn_period):
    last_rate = warn_start = limit_start = None

    detector = limit_detector(lower_rate, upper_rate, threshold_seconds)
    warner = warn_detector(warn_period)
    detector.send(None)
    warner.send(None)

    with heart.with_heart_rate_queue() as q:
        while True:
            timeout = next_timeout(limit_start, warn_start)
            rate = get_heart_rate(q, timeout) or last_rate

            limit_start, limit_warning = detector.send(rate)
            warn_start, display_warning = warner.send(limit_warning)
            if display_warning:
                print display_warning

            last_rate = rate

def limit_detector(lower_rate, upper_rate, threshold_seconds):
    "Coroutine to detect if heart rate has limited limits"
    limit_start = None
    rate = yield None, None
    while True:
        if lower_rate and rate < lower_rate:
            if limit_start is None:
                limit_start = time.time()

            if time.time() - limit_start > threshold_seconds:
                LOGGER.debug('Low rate detected %r <  %r', rate, lower_rate)
                rate = yield (None, 'Rate too low {} < {}'.format(rate, lower_rate))
            else:
                rate = yield (limit_start + threshold_seconds, None)

        if upper_rate and rate > upper_rate:
            if not limit_start:
                limit_start = time.time()

            if time.time() - limit_start > threshold_seconds:
                LOGGER.debug('High rate detected %r >  %r', rate, upper_rate)
                rate = yield (None, 'Rate too high {} > {}'.format(rate, upper_rate))
            else:
                rate = yield (limit_start + threshold_seconds, None)

def warn_detector(warn_period):
    "Warn periodically"
    # This is a bit crazy...
    warning = yield None, None
    last_warn = None
    while True:
        if warning:
            if last_warn is None:
                last_warn = time.time()
                warning = yield last_warn + warn_period, warning
            elif last_warn and time.time() - last_warn  > warn_period:
                last_warn += warn_period
                warning = yield last_warn + warn_period, warning
            else:
                warning = yield last_warn + warn_period, None
        else:
            last_warn = None
            warning = yield None, None
            continue






def next_timeout(*expiries):
    if all(x is None for x in expiries):
        return None
    else:
        return min(x for x in expiries if x is not None) - time.time()


