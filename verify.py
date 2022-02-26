from argparse import ArgumentParser
from datetime import datetime, timedelta
from pprint import pprint
from re import match


def verify_date(number):
    assert len(number) == 18, "Chinese Citzen ID-number must have 18 bits"
    try:
        date = datetime.strptime(number[6:14], "%Y%m%d")
    except ValueError:
        return False
    return True


def verify_verification_bit(number):
    assert len(number) == 18, "Chinese Citzen ID-number must have 18 bits"
    bit_weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    weighted_sum = sum([int(number[i]) * bit for i, bit in enumerate(bit_weights)])
    last_bits = (1, 0, "X", 9, 8, 7, 6, 5, 4, 3, 2)
    return str(last_bits[weighted_sum % 11]) == number[-1]


def verify_id_number(number, show_result=False):
    valid = verify_date(number) and verify_verification_bit(number)
    if show_result:
        print(f"Verifying {number}, {'valid 😊!' if valid else 'invalid 😭!'}")
    return valid


def get_start_end_date(date_prefix=""):
    l = len(date_prefix)
    assert l >= 0
    assert l <= 8
    start_year = "1900"
    start_month = "01"
    start_day = "01"
    today = datetime.today()
    end_year = today.strftime("%Y")
    end_month = "12"
    end_day = "31"

    if l == 0:
        pass
    elif l <= 4:
        start_year = date_prefix + "0" * (4 - l)
        end_year = date_prefix + "9" * (4 - l)
    elif l <= 6:
        start_year = date_prefix[0:4]
        end_year = start_year
        start_month = f'{max(int(date_prefix[4:] + (6- l)*"0"), 1):02}'
        end_month = f'{min(int(date_prefix[4:] + (6-l) * "9"), 12):02}'
    elif l <= 8:
        start_year = date_prefix[0:4]
        end_year = start_year
        start_month = date_prefix[4:6]
        end_month = start_month
        start_day = f'{max(int(date_prefix[6:] + (8- l)*"0"), 1):02}'
        end_day = f'{min(int(date_prefix[6:] + (8-l) * "9"), 31):02}'
    start_date = datetime.strptime(start_year + start_month + start_day, "%Y%m%d")
    end_date = datetime.strptime(end_year + end_month + end_day, "%Y%m%d")
    if end_date > today:
        end_date = today
    return start_date, end_date


def guess_birthday(head, tail, birthday_prefix=""):
    assert len(head) == 6
    assert len(tail) == 4
    start_date, end_date = get_start_end_date(birthday_prefix)
    during = end_date - start_date
    candidates = set()
    for day_delta in range(during.days):
        date = start_date + timedelta(days=day_delta)
        print(f"Guess {date.strftime('%Y%m%d')}, result is", end="")
        id_number = head + date.strftime("%Y%m%d") + tail
        valid = verify_id_number(id_number)
        if valid:
            candidates.add(id_number)
            print(" valid😊!")
        else:
            print(" invalid😭!")

    pprint(
        f"All guesses finished, get {len(candidates)} candidates are {candidates}",
    )
    return candidates


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_verify = subparsers.add_parser("verify", help="verify given id numbers")
    parser_verify.set_defaults(function=verify_id_number)
    parser_verify.add_argument("id_numbers", nargs="+")

    parser_guess = subparsers.add_parser("guess", help="guess the birthday")
    parser_guess.set_defaults(function=guess_birthday)
    parser_guess.add_argument("head", help="head of id number, must be 6 digits")
    parser_guess.add_argument("tail", help="tail of id number, must be 4 digits")
    parser_guess.add_argument(
        "--birthday_prefix", help="birthday prefix, default is ''(empty)", default=""
    )

    args = parser.parse_args()

    if args.function == verify_id_number:
        for id_number in args.id_numbers:
            args.function(id_number, show_result=True)
    elif args.function == guess_birthday:
        args.function(args.head, args.tail, args.birthday_prefix)


if __name__ == "__main__":
    main()
