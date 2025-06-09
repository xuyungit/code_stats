#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

from git_utils import GitError
from git_analyzer import GitAnalyzer
from report_formatter import ReportFormatter


def main():
    parser = argparse.ArgumentParser(
        description='Calculate code statistics for a git repository over a specified period.'
    )
    parser.add_argument('repo_path', type=str, help='Path to the git repository.')
    parser.add_argument(
        '--days', 
        type=int, 
        default=7, 
        help='Number of recent days to show daily statistics for. Default is 7.'
    )
    parser.add_argument(
        '--authors',
        action='store_true',
        help='Show statistics broken down by author instead of daily breakdown.'
    )
    parser.add_argument(
        '--daily-authors',
        action='store_true',
        help='Show daily statistics with author breakdown for each day.'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.repo_path):
        print(f"Error: Repository path {args.repo_path} does not exist or is not a directory.")
        return

    try:
        # Initialize analyzer and formatter
        analyzer = GitAnalyzer(args.repo_path)
        formatter = ReportFormatter(os.path.abspath(args.repo_path))

        if args.authors:
            # Show author statistics for the entire period
            author_stats = analyzer.get_author_stats_period(args.days)
            formatter.print_author_stats(author_stats, args.days)
            
        elif args.daily_authors:
            # Show daily statistics with author breakdown
            daily_author_breakdown = analyzer.get_daily_author_breakdown(args.days)
            formatter.print_daily_author_stats(daily_author_breakdown, args.days)
            
        else:
            # Original daily breakdown mode
            daily_breakdown = analyzer.get_daily_breakdown(args.days)
            formatter.print_daily_stats(daily_breakdown, args.days)

        formatter.print_footer()

    except GitError as e:
        print(f"Error: {e}")
        return


if __name__ == '__main__':
    main()