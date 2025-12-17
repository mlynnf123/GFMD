#!/usr/bin/env python3
"""
Business Day Utilities for Email Sequence Timing
Handles business day calculations for professional email scheduling
"""

from datetime import datetime, timedelta
from typing import List

class BusinessDayCalculator:
    """Calculate business days and schedule emails appropriately"""
    
    def __init__(self):
        # US Federal holidays (static dates for simplicity)
        self.federal_holidays = [
            (1, 1),    # New Year's Day
            (7, 4),    # Independence Day
            (11, 11),  # Veterans Day
            (12, 25),  # Christmas Day
        ]
        
        # Floating holidays (approximate - would need proper calculation in production)
        self.floating_holidays = [
            "Martin Luther King Jr. Day",  # 3rd Monday in January
            "Presidents' Day",             # 3rd Monday in February
            "Memorial Day",                # Last Monday in May
            "Labor Day",                   # 1st Monday in September
            "Columbus Day",                # 2nd Monday in October
            "Thanksgiving",                # 4th Thursday in November
        ]
    
    def is_business_day(self, date: datetime) -> bool:
        """Check if a date is a business day (Mon-Fri, not holiday)"""
        # Weekend check (Monday=0, Sunday=6)
        if date.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Holiday check (simplified - only static holidays)
        month_day = (date.month, date.day)
        if month_day in self.federal_holidays:
            return False
        
        return True
    
    def add_business_days(self, start_date: datetime, business_days: int) -> datetime:
        """Add specified number of business days to a date"""
        current_date = start_date
        days_added = 0
        
        while days_added < business_days:
            current_date += timedelta(days=1)
            if self.is_business_day(current_date):
                days_added += 1
        
        return current_date
    
    def get_next_business_day(self, date: datetime) -> datetime:
        """Get the next business day from given date"""
        return self.add_business_days(date, 1)
    
    def get_previous_business_day(self, date: datetime) -> datetime:
        """Get the previous business day from given date"""
        current_date = date
        while True:
            current_date -= timedelta(days=1)
            if self.is_business_day(current_date):
                return current_date
    
    def business_days_between(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate number of business days between two dates"""
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        business_days = 0
        current_date = start_date
        
        while current_date < end_date:
            if self.is_business_day(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    def is_good_email_time(self, date: datetime) -> bool:
        """Check if datetime is a good time to send business emails"""
        # Must be business day
        if not self.is_business_day(date):
            return False
        
        # Check time of day (8 AM - 6 PM in recipient's timezone)
        hour = date.hour
        if hour < 8 or hour > 18:
            return False
        
        return True
    
    def get_next_good_email_time(self, date: datetime) -> datetime:
        """Get next appropriate time to send business emails"""
        current = date
        
        # If it's after business hours, move to next business day at 9 AM
        if current.hour >= 18:
            next_day = current.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
            return self.get_next_business_day_at_time(next_day, 9, 0)
        
        # If it's before business hours, set to 9 AM same day (if business day)
        if current.hour < 8:
            same_day_9am = current.replace(hour=9, minute=0, second=0, microsecond=0)
            if self.is_business_day(same_day_9am):
                return same_day_9am
            else:
                return self.get_next_business_day_at_time(same_day_9am, 9, 0)
        
        # If it's during business hours on a business day, use as-is
        if self.is_good_email_time(current):
            return current
        
        # Otherwise, next business day at 9 AM
        return self.get_next_business_day_at_time(current, 9, 0)
    
    def get_next_business_day_at_time(self, date: datetime, hour: int, minute: int = 0) -> datetime:
        """Get next business day at specific time"""
        next_business_day = self.get_next_business_day(date)
        return next_business_day.replace(hour=hour, minute=minute, second=0, microsecond=0)


def calculate_sequence_timing_business_days() -> List[int]:
    """Calculate email sequence timing in business days (every 2 business days)"""
    
    # Original timing: [0, 3, 7, 14, 21, 35] calendar days
    # New timing: Every 2 business days
    
    business_day_intervals = [0, 2, 4, 6, 8, 10]  # 2 business days apart
    
    return business_day_intervals


def test_business_day_calculator():
    """Test the business day calculator"""
    print("🗓️ Testing Business Day Calculator")
    print("=" * 50)
    
    calc = BusinessDayCalculator()
    
    # Test various dates
    test_dates = [
        datetime(2024, 12, 16),  # Monday
        datetime(2024, 12, 17),  # Tuesday
        datetime(2024, 12, 21),  # Saturday
        datetime(2024, 12, 22),  # Sunday
        datetime(2024, 12, 25),  # Christmas (Wednesday)
        datetime(2024, 1, 1),    # New Year's Day
    ]
    
    for date in test_dates:
        is_bday = calc.is_business_day(date)
        day_name = date.strftime("%A")
        print(f"{date.strftime('%Y-%m-%d')} ({day_name}): {'✅' if is_bday else '❌'} Business Day")
    
    print("\n📧 Email Timing Tests:")
    
    # Test adding business days
    start_date = datetime(2024, 12, 16, 9, 0)  # Monday 9 AM
    for i in range(1, 6):
        next_email = calc.add_business_days(start_date, i * 2)  # Every 2 business days
        print(f"Email {i + 1}: {next_email.strftime('%Y-%m-%d %A %I:%M %p')}")
    
    print(f"\n📅 New Sequence Timing (Business Days): {calculate_sequence_timing_business_days()}")


if __name__ == "__main__":
    test_business_day_calculator()