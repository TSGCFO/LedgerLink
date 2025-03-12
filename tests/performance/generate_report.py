#!/usr/bin/env python
"""
Performance Test Report Generator

This script processes pytest-benchmark result data and generates a performance report
showing current performance metrics and historical trends.
"""

import json
import os
import datetime
import glob
import sys
from collections import defaultdict

# Configuration
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'performance', 'results')
BENCHMARK_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             '.benchmarks')
REPORT_FILE = os.path.join(RESULTS_DIR, f'performance_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
HISTORY_FILE = os.path.join(RESULTS_DIR, 'performance_history.json')

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# Performance thresholds in milliseconds
THRESHOLDS = {
    'fast': 100,       # < 100ms
    'acceptable': 500, # < 500ms
    'slow': 1000,      # < 1000ms
    # > 1000ms is considered very slow
}

def find_latest_benchmark_data():
    """Find the latest benchmark data file"""
    benchmark_dirs = glob.glob(os.path.join(BENCHMARK_DATA, '*'))
    if not benchmark_dirs:
        print("No benchmark data found!")
        return None
    
    latest_dir = max(benchmark_dirs, key=os.path.getmtime)
    json_files = glob.glob(os.path.join(latest_dir, '*.json'))
    
    if not json_files:
        print(f"No JSON files found in {latest_dir}")
        return None
    
    return json_files[0]

def load_benchmark_data(filepath):
    """Load benchmark data from file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading benchmark data: {e}")
        return None

def load_history_data():
    """Load historical performance data"""
    if not os.path.exists(HISTORY_FILE):
        return {}
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history data: {e}")
        return {}

def save_history_data(history_data):
    """Save updated historical performance data"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history_data, f, indent=2)
    except Exception as e:
        print(f"Error saving history data: {e}")

def update_history(history_data, current_data):
    """Update historical data with current benchmark results"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if 'benchmarks' not in current_data:
        return history_data
    
    for benchmark in current_data['benchmarks']:
        name = benchmark['name']
        mean_time = benchmark['stats']['mean'] * 1000  # Convert to milliseconds
        
        if name not in history_data:
            history_data[name] = []
        
        # Add current data point
        history_data[name].append({
            'date': today,
            'mean_time': mean_time,
            'min_time': benchmark['stats']['min'] * 1000,
            'max_time': benchmark['stats']['max'] * 1000,
            'commit': current_data.get('commit_info', {}).get('id', 'unknown')
        })
        
        # Keep only the last 10 data points
        if len(history_data[name]) > 10:
            history_data[name] = history_data[name][-10:]
    
    return history_data

def get_performance_category(time_ms):
    """Categorize performance based on thresholds"""
    if time_ms < THRESHOLDS['fast']:
        return 'fast', '✅'
    elif time_ms < THRESHOLDS['acceptable']:
        return 'acceptable', '✅'
    elif time_ms < THRESHOLDS['slow']:
        return 'slow', '⚠️'
    else:
        return 'very slow', '❌'

def analyze_trend(history):
    """Analyze performance trend"""
    if not history or len(history) < 2:
        return "insufficient data", "➖"
    
    # Get last two data points
    current = history[-1]['mean_time']
    previous = history[-2]['mean_time']
    
    change_pct = ((current - previous) / previous) * 100
    
    if abs(change_pct) < 5:
        return "stable", "➖"
    elif change_pct < 0:
        return f"improving ({abs(change_pct):.1f}%)", "✅"
    else:
        return f"degrading ({change_pct:.1f}%)", "❌"

def generate_report(benchmark_data, history_data):
    """Generate performance report markdown"""
    report = []
    report.append("# LedgerLink Performance Test Report")
    report.append(f"\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if 'commit_info' in benchmark_data:
        commit = benchmark_data['commit_info']
        report.append(f"\nCommit: {commit.get('id', 'unknown')}")
        report.append(f"Branch: {commit.get('branch', 'unknown')}")
    
    report.append("\n## Performance Summary\n")
    report.append("| Test | Mean (ms) | Min (ms) | Max (ms) | Status | Trend |")
    report.append("|------|-----------|----------|----------|--------|-------|")
    
    tests_by_category = defaultdict(list)
    
    for benchmark in benchmark_data.get('benchmarks', []):
        name = benchmark['name']
        mean_time = benchmark['stats']['mean'] * 1000  # Convert to milliseconds
        min_time = benchmark['stats']['min'] * 1000
        max_time = benchmark['stats']['max'] * 1000
        
        category, status_icon = get_performance_category(mean_time)
        
        trend_text, trend_icon = "N/A", "➖"
        if name in history_data:
            trend_text, trend_icon = analyze_trend(history_data[name])
        
        row = f"| {name} | {mean_time:.2f} | {min_time:.2f} | {max_time:.2f} | {status_icon} | {trend_icon} |"
        report.append(row)
        
        # Group tests by category for summary
        tests_by_category[category].append(name)
    
    # Add category summary
    report.append("\n## Performance Categories\n")
    for category in ['fast', 'acceptable', 'slow', 'very slow']:
        if category in tests_by_category:
            report.append(f"### {category.title()} Tests ({len(tests_by_category[category])})\n")
            for test in tests_by_category[category]:
                report.append(f"- {test}")
            report.append("")
    
    # Add trend analysis
    report.append("\n## Performance Trends\n")
    for name, history in history_data.items():
        if len(history) > 1:
            report.append(f"### {name}\n")
            
            # Create simple ASCII trend
            trend_values = [point['mean_time'] for point in history]
            max_val = max(trend_values)
            min_val = min(trend_values)
            range_val = max(1, max_val - min_val)  # Avoid division by zero
            
            # Create a simple ASCII chart
            chart = ["Performance over time (last 10 runs):"]
            chart.append("```")
            
            # Get dates for x-axis
            dates = [point['date'].split('-')[-1] for point in history]  # Just day part
            
            # Create the chart
            height = 10
            for y in range(height, 0, -1):
                level = min_val + (range_val * (y / height))
                line = f"{level:.1f} ms |"
                for val in trend_values:
                    if val >= level:
                        line += "*"
                    else:
                        line += " "
                chart.append(line)
            
            # Add x-axis
            chart.append("       +" + "-" * len(trend_values))
            
            # Add dates on x-axis if we have them
            if dates:
                date_line = "        "
                for day in dates:
                    date_line += day + " "
                chart.append(date_line)
            
            chart.append("```")
            report.extend(chart)
            report.append("")
    
    return "\n".join(report)

def main():
    """Main function to generate performance report"""
    print("Generating performance report...")
    
    # Find and load benchmark data
    benchmark_file = find_latest_benchmark_data()
    if not benchmark_file:
        print("No benchmark data found. Run performance tests first.")
        return 1
    
    benchmark_data = load_benchmark_data(benchmark_file)
    if not benchmark_data:
        print("Failed to load benchmark data.")
        return 1
    
    # Load and update history
    history_data = load_history_data()
    history_data = update_history(history_data, benchmark_data)
    save_history_data(history_data)
    
    # Generate report
    report = generate_report(benchmark_data, history_data)
    
    # Save report
    try:
        with open(REPORT_FILE, 'w') as f:
            f.write(report)
        print(f"Performance report saved to: {REPORT_FILE}")
    except Exception as e:
        print(f"Error saving report: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())