#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List
from datetime import date

from stats_parser import sort_authors_by_activity


class ReportFormatter:
    """Handles formatting and display of git statistics reports."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the formatter with repository path.
        
        Args:
            repo_path: Absolute path to the repository
        """
        self.repo_path = repo_path
    
    def print_header(self, title: str, days: int = None) -> None:
        """
        Prints a formatted header for reports.
        
        Args:
            title: The main title of the report
            days: Number of days (optional)
        """
        if days:
            full_title = f"{title} for the last {days} day(s)"
        else:
            full_title = title
        
        print(f"\n--- {full_title} ---")
        print(f"Repository: {self.repo_path}")
        print("-----------------------------------------------------")
    
    def print_footer(self) -> None:
        """Prints the report footer."""
        print("-----------------------------------------------------")
    
    def format_net_change(self, net_change: int) -> str:
        """
        Formats net change with appropriate sign.
        
        Args:
            net_change: The net change value
            
        Returns:
            Formatted string with sign
        """
        sign = '+' if net_change >= 0 else ''
        return f"{net_change} ({sign}{net_change})"
    
    def print_author_stats(self, author_stats: Dict, days: int) -> None:
        """
        Prints author statistics report.
        
        Args:
            author_stats: Dictionary of author statistics
            days: Number of days the stats cover
        """
        self.print_header("Author Git Repository Statistics", days)
        
        if not author_stats:
            print("No activity found for the specified period.")
            return
        
        sorted_authors = sort_authors_by_activity(author_stats)
        
        for author_email, stats in sorted_authors:
            print(f"\nAuthor: {stats['name']} <{author_email}>")
            print(f"  Commits: {stats['commits_count']}")
            print(f"  Files changed: {stats['total_files_changed']}")
            print(f"  Lines added: {stats['added_lines']}")
            print(f"  Lines deleted: {stats['deleted_lines']}")
            
            net_change = stats['added_lines'] - stats['deleted_lines']
            print(f"  Net lines change: {self.format_net_change(net_change)}")
            
            total_activity = stats['added_lines'] + stats['deleted_lines']
            print(f"  Total line activity: {total_activity}")
    
    def print_daily_stats(self, daily_breakdown: List[Dict], days: int) -> None:
        """
        Prints daily statistics report.
        
        Args:
            daily_breakdown: List of daily statistics
            days: Number of days
        """
        self.print_header("Daily Git Repository Statistics", days)
        
        for day_data in daily_breakdown:
            target_date = day_data['date']
            stats = day_data['stats']
            
            print(f"\nDate: {target_date.strftime('%Y-%m-%d')}")
            
            if stats:
                print(f"  Commits: {stats['commits_count']}")
                print(f"  Files changed: {stats['total_files_changed']}")
                print(f"  Lines added: {stats['added_lines']}")
                print(f"  Lines deleted: {stats['deleted_lines']}")
                
                net_change = stats['added_lines'] - stats['deleted_lines']
                print(f"  Net lines change: {self.format_net_change(net_change)}")
                
                total_activity = stats['added_lines'] + stats['deleted_lines']
                print(f"  Total line activity: {total_activity}")
            else:
                print("  No activity or error fetching stats for this day.")
    
    def print_daily_author_stats(self, daily_author_breakdown: List[Dict], days: int) -> None:
        """
        Prints daily statistics with author breakdown.
        
        Args:
            daily_author_breakdown: List of daily author statistics
            days: Number of days
        """
        self.print_header("Daily Git Repository Statistics with Author Breakdown", days)
        
        for day_data in daily_author_breakdown:
            target_date = day_data['date']
            author_stats = day_data['author_stats']
            
            print(f"\nDate: {target_date.strftime('%Y-%m-%d')}")
            
            if author_stats:
                sorted_authors = sort_authors_by_activity(author_stats)
                day_totals = {'commits': 0, 'added': 0, 'deleted': 0}
                
                for author_email, stats in sorted_authors:
                    print(f"  {stats['name']} <{author_email}>:")
                    print(f"    Commits: {stats['commits_count']}")
                    print(f"    Files changed: {stats['total_files_changed']}")
                    print(f"    Lines added: {stats['added_lines']}")
                    print(f"    Lines deleted: {stats['deleted_lines']}")
                    
                    net_change = stats['added_lines'] - stats['deleted_lines']
                    print(f"    Net change: {self.format_net_change(net_change)}")
                    
                    day_totals['commits'] += stats['commits_count']
                    day_totals['added'] += stats['added_lines']
                    day_totals['deleted'] += stats['deleted_lines']
                
                print(f"  Day Total:")
                print(f"    Total commits: {day_totals['commits']}")
                print(f"    Total lines added: {day_totals['added']}")
                print(f"    Total lines deleted: {day_totals['deleted']}")
                
                net_total = day_totals['added'] - day_totals['deleted']
                print(f"    Net change: {self.format_net_change(net_total)}")
                
                total_activity = day_totals['added'] + day_totals['deleted']
                print(f"    Total activity: {total_activity}")
            else:
                print("  No activity or error fetching stats for this day.")