import requests
import sys
import colorama
from colorama import Fore, Back, Style

def check_username(username):
    """Make a request to OKCupid's servers to check a single username.

    Return an object with the following attributes:
      - .valid
      - .available
      - .reason, the reason the username was not valid (a numeric code)
      - .recommendations, OKCupid's (terrible/snarky) recommendations
        for alternate usernames if the username was not available
    """
    class Result (object):
        def __init__(self, valid, available=False, reason=None, recommendations=None):
            self.available = available
            self.valid = valid
            self.reason = reason
            self.recommendations = recommendations or []
        def __repr__(self):
            if not self.valid:
                desc = "invalid"
            else:
                desc = "available" if self.available else "not available"
            return "<availability result: {}>".format(desc)
    url = "http://www.okcupid.com/signup"
    parameters = {"check_screenname": username}
    response = requests.post(url, data=parameters).json()
    return Result(**response)

def run_check_username(args, username):
    """Run a check on a single username and print the results."""
    if not args.quiet:
        colored_username = Style.BRIGHT + username + Style.RESET_ALL
        print "Checking '{}'..".format(colored_username),
    result = check_username(username)
    if not result.valid:
        if not args.quiet:
            print Fore.RED + "invalid" + Style.RESET_ALL
    elif result.available:
        if not args.quiet:
            print Fore.GREEN + "available" + Style.RESET_ALL
    else:
        if not args.quiet:
            print Fore.RED + "taken" + Style.RESET_ALL
            if args.verbose and result.recommendations:
                for suggestion in result.recommendations:
                    print "\t" + Fore.YELLOW + suggestion + Style.RESET_ALL
    return result.available

def run_check_usernames(args):
    """Run checks on a list username and print the results.
    
    Return the number of usernames that were available."""
    tally = 0
    for username in args.usernames:
        if run_check_username(args, username):
            tally += 1
            if args.shortcircuit:
                break
    return tally

def main():
    """Main function for OKCupid username checker.

    Take a list of usernames from the command line and check them.
    Print the results on the command line (unless otherwise instructed)
    and return success (0) if at least one username was available,
    otherwise 1.
    """
    from argparse import ArgumentParser
    description = "Check whether an OKCupid username is taken."
    parser = ArgumentParser(description=description)
    parser.add_argument("usernames",
                        metavar="username", type=str, nargs="+",
                        help="a username to check")
    parser.add_argument("-v", "--verbose",
                        dest="verbose", action="store_const",
                        const=True, default=False,
                        help="verbose output including recommendations")
    parser.add_argument("-s", "--shortcircuit",
                        dest="shortcircuit", action="store_const",
                        const=True, default=False,
                        help="stop on first success")
    parser.add_argument("-C", "--nocolor",
                        dest="nocolor", action="store_const",
                        const=True, default=False,
                        help="plain, unstyled output")
    parser.add_argument("-q", "--quiet",
                        dest="quiet", action="store_const",
                        const=True, default=False,
                        help="no output (return 0 if at least one successful)")
    args = parser.parse_args()
    if args.nocolor:
        colorama.init(strip=True, convert=False)
    else:
        colorama.init()
    if not run_check_usernames(args):
        sys.exit(1)

if __name__ == '__main__':
    main()
