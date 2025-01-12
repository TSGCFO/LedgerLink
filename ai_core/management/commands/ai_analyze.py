# ai_core/management/commands/ai_analyze.py
from django.core.management.base import BaseCommand
from ...components import ProjectAnalyzer
from ...system import AISystem


class Command(BaseCommand):
    help = 'Analyzes the project structure and updates AI knowledge base'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform a full analysis instead of incremental'
        )

        parser.add_argument(
            '--app',
            type=str,
            help='Analyze specific app only'
        )

        parser.add_argument(
            '--output',
            type=str,
            help='Output analysis result to specified file'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting project analysis...')

        try:
            analyzer = AISystem.get_component('project_analyzer')

            analysis_params = {
                'full_analysis': options['full']
            }

            if options['app']:
                analysis_params['app_name'] = options['app']
                self.stdout.write(f"Analyzing app: {options['app']}")

            result = analyzer.analyze_project(**analysis_params)

            # Format analysis results
            stats = result.get('stats', {})
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nAnalysis completed successfully:"
                    f"\n- Files analyzed: {stats.get('files_analyzed', 0)}"
                    f"\n- Models found: {stats.get('models_found', 0)}"
                    f"\n- Views analyzed: {stats.get('views_analyzed', 0)}"
                    f"\n- URLs processed: {stats.get('urls_processed', 0)}"
                )
            )

            # Output to file if specified
            if options['output']:
                import json
                with open(options['output'], 'w') as f:
                    json.dump(result, f, indent=2)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nAnalysis results written to: {options['output']}"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Analysis failed: {str(e)}"
                )
            )