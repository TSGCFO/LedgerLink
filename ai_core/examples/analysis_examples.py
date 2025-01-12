# ai_core/examples/analysis_examples.py
from pathlib import Path
from typing import Dict, Any
from django.conf import settings
from ..components.project_analyzer import ProjectAnalyzer


def analysis_examples():
    """
    Examples of using the Project Analysis API
    """
    # Initialize analyzer
    analyzer = ProjectAnalyzer(settings.AI_SYSTEM_CONFIG['components']['project_analyzer'])

    # Basic project analysis
    basic_analysis = analyzer.analyze_project(full_analysis=False)

    # Full project analysis
    detailed_analysis = analyzer.analyze_project(full_analysis=True)

    # Analyze specific components
    component_analysis = analyzer.analyze_project(
        components=['models', 'views', 'templates']
    )

    return {
        'basic_analysis': basic_analysis,
        'detailed_analysis': detailed_analysis,
        'component_analysis': component_analysis
    }


def model_analysis_example():
    """
    Example of analyzing models
    """
    analyzer = ProjectAnalyzer(settings.AI_SYSTEM_CONFIG['components']['project_analyzer'])

    # Analyze project with focus on models
    analysis_result = analyzer.analyze_project(
        components=['models'],
        full_analysis=True
    )

    return analysis_result.get('models', {})


def template_analysis_example():
    """
    Example of analyzing templates
    """
    analyzer = ProjectAnalyzer(settings.AI_SYSTEM_CONFIG['components']['project_analyzer'])

    # Analyze project with focus on templates
    analysis_result = analyzer.analyze_project(
        components=['templates'],
        full_analysis=True
    )

    return analysis_result.get('templates', {})