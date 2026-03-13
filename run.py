"""
Financial Data Analytics Dashboard — Main Entry Point
Runs the ETL pipeline and optionally launches the dashboard.
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(
        description='Financial Data Analytics Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    Run full pipeline + launch dashboard
  python run.py --pipeline-only    Run ETL pipeline only
  python run.py --dashboard-only   Launch dashboard (requires existing data)
  python run.py --report-only      Generate Excel report only
        """
    )
    parser.add_argument('--pipeline-only', action='store_true',
                        help='Run ETL pipeline without launching dashboard')
    parser.add_argument('--dashboard-only', action='store_true',
                        help='Launch dashboard without running pipeline')
    parser.add_argument('--report-only', action='store_true',
                        help='Generate Excel report only')
    parser.add_argument('--port', type=int, default=8050,
                        help='Dashboard port (default: 8050)')
    parser.add_argument('--debug', action='store_true',
                        help='Run dashboard in debug mode')

    args = parser.parse_args()

    if args.report_only:
        print("\n📊 Generating Excel Report...\n")
        from reports.excel_report import generate_excel_report
        path = generate_excel_report()
        print(f"\n✅ Report generated: {path}")
        return

    if not args.dashboard_only:
        print("\n🔄 Running ETL Pipeline...\n")
        from etl.pipeline import run_pipeline
        metrics = run_pipeline()

        # Generate Excel report after pipeline
        print("\n📊 Generating Excel Report...")
        from reports.excel_report import generate_excel_report
        report_path = generate_excel_report()
        print(f"\n✅ Report: {report_path}")

    if not args.pipeline_only:
        print("\n🚀 Launching Dashboard...\n")
        from dashboard.app import run_dashboard
        run_dashboard(debug=args.debug, port=args.port)


if __name__ == '__main__':
    main()
